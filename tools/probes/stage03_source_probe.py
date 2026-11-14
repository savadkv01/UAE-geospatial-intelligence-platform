"""Stage 03 source-profiling probe (evidence tool, not part of the product codebase).

Reproduces the measurements in docs/profiling-report.md. Network access is
bounded by an approved budget; read the report before running.

Setup (disposable venv, git-ignored):
    python -m venv .scratch/stage03/venv
    .scratch/stage03/venv/Scripts/python -m pip install pystac-client==0.9.1 \
        planetary-computer==1.0.0 rasterio==1.5.2 pyproj==3.8.0 shapely==2.2.0 \
        psutil==7.2.2 python-dotenv==1.2.4 boto3==1.44.3 requests==2.34.2

Usage (from the repository root):
    python tools/probes/stage03_source_probe.py <step> [<step> ...]
Steps: env, catalog, access, s2, s1, worldcover, ghsl, osm, followup, cdse
The cdse step needs CDSE_S3_ACCESS_KEY / CDSE_S3_SECRET_KEY in the untracked .env.

Outputs go to .scratch/stage03/{results,data} (git-ignored).
Network volume is measured as the system-wide bytes_recv delta (psutil),
which is an UPPER BOUND for the probe's own traffic. The run aborts if the
cumulative delta across steps exceeds the approved 1 GB budget.
"""

from __future__ import annotations

import json
import os
import platform
import statistics
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import psutil
import requests

REPO = Path(__file__).resolve().parents[2]
SCRATCH = REPO / ".scratch" / "stage03"
RESULTS = SCRATCH / "results"
DATA = SCRATCH / "data"
RESULTS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
LEDGER = RESULTS / "budget.json"
BUDGET_BYTES = 1_000_000_000

# Probe test box around Abu Dhabi island (lon/lat, EPSG:4326). Not the AOI.
BBOX = [54.30, 24.38, 54.50, 24.52]
YEARS = list(range(2017, 2027))

PC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
ES_URL = "https://earth-search.aws.element84.com/v1"
CDSE_URL = "https://stac.dataspace.copernicus.eu/v1"

S2_MASK_CLASSES = {0, 1, 3, 8, 9, 10}  # measurement-spec SCL mask set

os.environ.update(
    {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.TIF,.tiff,.jp2",
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "GDAL_HTTP_MAX_RETRY": "3",
        "GDAL_HTTP_RETRY_DELAY": "2",
        "VSI_CACHE": "FALSE",
    }
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"{now()} {msg}"
    print(line, flush=True)
    with open(RESULTS / "probe.log", "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {"total_bytes_recv_upper_bound": 0, "steps": {}}


def recv() -> int:
    return psutil.net_io_counters().bytes_recv


def check_budget(extra: int = 0) -> None:
    led = ledger()
    if led["total_bytes_recv_upper_bound"] + extra > BUDGET_BYTES:
        raise RuntimeError(
            f"Budget exceeded: {led['total_bytes_recv_upper_bound'] + extra} > {BUDGET_BYTES}"
        )


def write(step: str, payload: dict) -> None:
    (RESULTS / f"{step}.json").write_text(json.dumps(payload, indent=2, default=str))


# ---------------------------------------------------------------- env
def step_env() -> dict:
    import boto3
    import planetary_computer
    import pyproj
    import pystac_client
    import rasterio
    import shapely

    return {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "ram_gb": round(psutil.virtual_memory().total / 1e9, 1),
        "packages": {
            "pystac-client": pystac_client.__version__,
            "planetary-computer": planetary_computer.__version__,
            "rasterio": rasterio.__version__,
            "gdal": rasterio.__gdal_version__,
            "pyproj": pyproj.__version__,
            "proj": pyproj.proj_version_str,
            "shapely": shapely.__version__,
            "boto3": boto3.__version__,
            "requests": requests.__version__,
            "psutil": psutil.__version__,
        },
        "bbox": BBOX,
    }


# ---------------------------------------------------------------- catalog
def _proj(item_props: dict, assets: dict) -> str | None:
    for k in ("proj:epsg", "proj:code"):
        if k in item_props:
            return str(item_props[k])
    for a in assets.values():
        for k in ("proj:epsg", "proj:code"):
            if k in a:
                return str(a[k])
    return None


def _search_all(url: str, collection: str, modifier=None, headers=None) -> tuple[list, dict]:
    from pystac_client import Client

    client = Client.open(url, modifier=modifier, headers=headers)
    items, per_year, errors = [], {}, {}
    for y in YEARS:
        t0 = time.time()
        try:
            search = client.search(
                collections=[collection],
                bbox=BBOX,
                datetime=f"{y}-01-01T00:00:00Z/{y}-12-31T23:59:59Z",
                limit=100,
            )
            got = [it.to_dict() for it in search.items()]
            items.extend(got)
            per_year[y] = {"items": len(got), "seconds": round(time.time() - t0, 1)}
        except Exception as exc:  # recorded verbatim in the report
            errors[y] = f"{type(exc).__name__}: {exc}"
            per_year[y] = {"items": None, "seconds": round(time.time() - t0, 1)}
    return items, {"per_year": per_year, "errors": errors}


def _summarise_s2(items: list) -> dict:
    cc, baselines, epsg, tiles, platforms = [], Counter(), Counter(), Counter(), Counter()
    asset_keys = Counter()
    media = {}
    for it in items:
        p = it["properties"]
        if p.get("eo:cloud_cover") is not None:
            cc.append(p["eo:cloud_cover"])
        b = p.get("s2:processing_baseline") or p.get("processing:version")
        baselines[str(b)] += 1
        epsg[_proj(p, it["assets"])] += 1
        tiles[str(p.get("s2:mgrs_tile") or p.get("grid:code") or p.get("mgrs:grid_square"))] += 1
        platforms[str(p.get("platform"))] += 1
        for k, a in it["assets"].items():
            asset_keys[k] += 1
            media.setdefault(k, a.get("type"))
    q = statistics.quantiles(cc, n=4) if len(cc) > 3 else None
    return {
        "n_items": len(items),
        "cloud_cover": {
            "n": len(cc),
            "min": min(cc) if cc else None,
            "q1_median_q3": q,
            "max": max(cc) if cc else None,
            "share_le_10pct": round(sum(c <= 10 for c in cc) / len(cc), 3) if cc else None,
            "share_le_30pct": round(sum(c <= 30 for c in cc) / len(cc), 3) if cc else None,
        },
        "processing_baselines": dict(baselines.most_common()),
        "proj": dict(epsg),
        "tiles": dict(tiles),
        "platforms": dict(platforms),
        "asset_keys": dict(asset_keys),
        "asset_media_types": media,
    }


def _summarise_s1(items: list) -> dict:
    orbits, modes, pols, plats, timeliness = Counter(), Counter(), Counter(), Counter(), Counter()
    asset_keys, media = Counter(), {}
    per_year_track = defaultdict(Counter)
    for it in items:
        p = it["properties"]
        key = f"{p.get('sat:orbit_state')}/rel{p.get('sat:relative_orbit')}"
        orbits[key] += 1
        per_year_track[it["properties"]["datetime"][:4]][key] += 1
        modes[str(p.get("sar:instrument_mode"))] += 1
        pols[str(p.get("sar:polarizations"))] += 1
        plats[str(p.get("platform"))] += 1
        timeliness[str(p.get("s1:product_timeliness"))] += 1
        for k, a in it["assets"].items():
            asset_keys[k] += 1
            media.setdefault(k, a.get("type"))
    return {
        "n_items": len(items),
        "orbit_state_relative_orbit": dict(orbits),
        "per_year_track": {y: dict(c) for y, c in sorted(per_year_track.items())},
        "instrument_modes": dict(modes),
        "polarizations": dict(pols),
        "platforms": dict(plats),
        "timeliness": dict(timeliness),
        "asset_keys": dict(asset_keys),
        "asset_media_types": media,
    }


def step_catalog() -> dict:
    import planetary_computer

    targets = [
        ("pc", PC_URL, "sentinel-2-l2a", "s2", planetary_computer.sign_inplace),
        ("pc", PC_URL, "sentinel-1-grd", "s1", planetary_computer.sign_inplace),
        ("es", ES_URL, "sentinel-2-c1-l2a", "s2", None),
        ("es", ES_URL, "sentinel-1-grd", "s1", None),
        ("cdse", CDSE_URL, "sentinel-2-l2a", "s2", None),
        ("cdse", CDSE_URL, "sentinel-1-grd", "s1", None),
    ]
    out = {}
    for provider, url, coll, kind, mod in targets:
        name = f"{provider}:{coll}"
        log(f"catalog search {name}")
        t0 = time.time()
        try:
            items, meta = _search_all(url, coll, modifier=mod)
            summary = _summarise_s2(items) if kind == "s2" else _summarise_s1(items)
            if items:
                (RESULTS / f"sample_item_{provider}_{coll}.json").write_text(
                    json.dumps(items[-1], indent=2)
                )
            # keep compact per-item metadata for later sample selection
            slim = [
                {
                    "id": it["id"],
                    "datetime": it["properties"].get("datetime"),
                    "cloud": it["properties"].get("eo:cloud_cover"),
                    "orbit_state": it["properties"].get("sat:orbit_state"),
                    "rel_orbit": it["properties"].get("sat:relative_orbit"),
                    "mode": it["properties"].get("sar:instrument_mode"),
                }
                for it in items
            ]
            (RESULTS / f"items_{provider}_{coll}.json").write_text(json.dumps(slim))
            out[name] = {**meta, "summary": summary, "seconds": round(time.time() - t0, 1)}
        except Exception as exc:
            out[name] = {"error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()}
    return out


# ---------------------------------------------------------------- access
def _status(url: str, headers: dict | None = None) -> dict:
    try:
        r = requests.get(url, headers={"Range": "bytes=0-1023", **(headers or {})}, timeout=60)
        return {"http_status": r.status_code, "bytes": len(r.content), "ctype": r.headers.get("content-type")}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def step_access() -> dict:
    """Catalogue access vs asset access: anonymous 1 KB range GETs on asset hrefs."""
    import planetary_computer

    res = {}
    for provider, coll, key in [
        ("pc", "sentinel-2-l2a", "B04"),
        ("pc", "sentinel-1-grd", "vv"),
        ("es", "sentinel-2-c1-l2a", "red"),
        ("es", "sentinel-1-grd", "vv"),
        ("cdse", "sentinel-2-l2a", "B04_10m"),
        ("cdse", "sentinel-1-grd", "vv"),
    ]:
        f = RESULTS / f"sample_item_{provider}_{coll}.json"
        if not f.exists():
            res[f"{provider}:{coll}"] = {"error": "no sample item from catalog step"}
            continue
        item = json.loads(f.read_text())
        assets = item["assets"]
        akey = key if key in assets else next((k for k in assets if key.lower() in k.lower()), None)
        if not akey:
            res[f"{provider}:{coll}"] = {"error": f"asset like {key} not found", "keys": list(assets)}
            continue
        href = assets[akey]["href"]
        entry = {"asset_key": akey, "href_scheme": href.split(":")[0], "alternate": list(assets[akey].get("alternate", {}).keys())}
        if provider == "pc":
            unsigned = href.split("?")[0]
            entry["unsigned"] = _status(unsigned)
            entry["signed"] = _status(planetary_computer.sign(unsigned))
        elif href.startswith("http"):
            entry["anonymous"] = _status(href)
        else:
            entry["anonymous"] = "non-HTTP href; anonymous HTTP not applicable"
            for alt_name, alt in assets[akey].get("alternate", {}).items():
                if alt.get("href", "").startswith("http"):
                    entry[f"anonymous_alternate_{alt_name}"] = _status(alt["href"])
        res[f"{provider}:{coll}"] = entry
    return res


# ---------------------------------------------------------------- raster helpers
def _window_read(href: str, band_name: str, scl: bool = False) -> dict:
    import numpy as np
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    t0 = time.time()
    with rasterio.open(href) as src:
        b = transform_bounds("EPSG:4326", src.crs, *BBOX)
        win = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
        win = win.intersection(rasterio.windows.Window(0, 0, src.width, src.height))
        arr = src.read(1, window=win)
        nod = src.nodata
        info = {
            "band": band_name,
            "crs": str(src.crs),
            "res": src.res,
            "dtype": src.dtypes[0],
            "nodata": nod,
            "scales": src.scales,
            "offsets": src.offsets,
            "full_shape": [src.height, src.width],
            "block_shapes": src.block_shapes[:1],
            "overviews": src.overviews(1),
            "compression": str(src.compression),
            "window_shape": list(arr.shape),
            "seconds": round(time.time() - t0, 1),
        }
    valid = arr != (nod if nod is not None else 0)
    info["nonnodata_fraction"] = round(float(valid.mean()), 4)
    if scl:
        vals, counts = np.unique(arr, return_counts=True)
        info["scl_histogram"] = {int(v): int(c) for v, c in zip(vals, counts)}
        usable = ~np.isin(arr, list(S2_MASK_CLASSES))
        info["valid_after_scl_mask_fraction"] = round(float(usable.mean()), 4)
    else:
        v = arr[valid]
        if v.size:
            info["dn_p2_p50_p98"] = [float(x) for x in np.percentile(v, [2, 50, 98])]
    return info


def _pick(items_file: Path, months: list[str], n: int) -> list[str]:
    items = json.loads(items_file.read_text())
    picks = []
    for m in months:
        cands = [i for i in items if i["datetime"].startswith(m) and i["cloud"] is not None]
        cands.sort(key=lambda i: i["cloud"])
        if cands:
            picks.append(cands[0]["id"])
        if len(picks) >= n:
            break
    return picks


def step_s2() -> dict:
    import planetary_computer
    from pystac_client import Client

    months = ["2021-01", "2024-01", "2025-01"]  # pre/post PB 04.00 offset change
    out = {}
    for provider, url, coll, keys, mod in [
        ("pc", PC_URL, "sentinel-2-l2a", {"red": "B04", "nir": "B08", "scl": "SCL"}, planetary_computer.sign_inplace),
        ("es", ES_URL, "sentinel-2-c1-l2a", {"red": "red", "nir": "nir", "scl": "scl"}, None),
    ]:
        ids = _pick(RESULTS / f"items_{provider}_{coll}.json", months, 3)
        client = Client.open(url, modifier=mod)
        for iid in ids:
            check_budget()
            r0 = recv()
            item = next(client.search(collections=[coll], ids=[iid]).items())
            entry = {
                "datetime": item.properties.get("datetime"),
                "cloud": item.properties.get("eo:cloud_cover"),
                "baseline": item.properties.get("s2:processing_baseline"),
                "raster_bands_meta": {
                    k: item.assets[v].extra_fields.get("raster:bands") for k, v in keys.items() if v in item.assets
                },
                "bands": {},
            }
            for k, v in keys.items():
                try:
                    entry["bands"][k] = _window_read(item.assets[v].href, k, scl=(k == "scl"))
                except Exception as exc:
                    entry["bands"][k] = {"error": f"{type(exc).__name__}: {exc}"}
            entry["bytes_recv_upper_bound"] = recv() - r0
            _add_bytes(f"s2:{provider}:{iid}", entry["bytes_recv_upper_bound"])
            out[f"{provider}:{iid}"] = entry
            log(f"s2 {provider} {iid} recv<= {entry['bytes_recv_upper_bound']}")
    return out


def step_s1() -> dict:
    import numpy as np
    import planetary_computer
    import rasterio
    from pystac_client import Client
    from rasterio.vrt import WarpedVRT
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    items = json.loads((RESULTS / "items_pc_sentinel-1-grd.json").read_text())
    items = [i for i in items if i["mode"] == "IW" and i["datetime"] >= "2025-01"]
    picks = []
    for state in ("ascending", "descending"):
        picks += [i["id"] for i in items if i["orbit_state"] == state][:2]
    client = Client.open(PC_URL, modifier=planetary_computer.sign_inplace)
    out = {}
    for iid in picks:
        check_budget()
        r0 = recv()
        item = next(client.search(collections=["sentinel-1-grd"], ids=[iid]).items())
        entry = {
            "datetime": item.properties.get("datetime"),
            "orbit_state": item.properties.get("sat:orbit_state"),
            "relative_orbit": item.properties.get("sat:relative_orbit"),
            "asset_keys": list(item.assets),
            "bands": {},
        }
        for pol in ("vv", "vh"):
            if pol not in item.assets:
                entry["bands"][pol] = {"error": "asset missing"}
                continue
            t0 = time.time()
            try:
                with rasterio.open(item.assets[pol].href) as src:
                    gcps, gcp_crs = src.gcps
                    meta = {
                        "native_crs": str(src.crs),
                        "gcp_count": len(gcps),
                        "gcp_crs": str(gcp_crs),
                        "dtype": src.dtypes[0],
                        "nodata": src.nodata,
                        "full_shape": [src.height, src.width],
                        "block_shapes": src.block_shapes[:1],
                        "overviews": src.overviews(1),
                        "compression": str(src.compression),
                    }
                    with WarpedVRT(src, src_crs=gcp_crs, crs="EPSG:32640", resolution=10) as vrt:
                        b = transform_bounds("EPSG:4326", vrt.crs, *BBOX)
                        win = from_bounds(*b, transform=vrt.transform).round_offsets().round_lengths()
                        arr = vrt.read(1, window=win)
                valid = arr > 0
                v = arr[valid].astype("float64")
                meta.update(
                    {
                        "window_shape": list(arr.shape),
                        "nonzero_fraction": round(float(valid.mean()), 4),
                        "dn_p2_p50_p98": [float(x) for x in np.percentile(v, [2, 50, 98])] if v.size else None,
                        "seconds": round(time.time() - t0, 1),
                    }
                )
                entry["bands"][pol] = meta
            except Exception as exc:
                entry["bands"][pol] = {"error": f"{type(exc).__name__}: {exc}", "seconds": round(time.time() - t0, 1)}
            check_budget(recv() - r0)
        entry["bytes_recv_upper_bound"] = recv() - r0
        _add_bytes(f"s1:pc:{iid}", entry["bytes_recv_upper_bound"])
        out[iid] = entry
        log(f"s1 {iid} recv<= {entry['bytes_recv_upper_bound']}")
    return out


def step_worldcover() -> dict:
    import numpy as np
    import planetary_computer
    import rasterio
    from pystac_client import Client
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    check_budget()
    r0 = recv()
    client = Client.open(PC_URL, modifier=planetary_computer.sign_inplace)
    items = list(client.search(collections=["esa-worldcover"], bbox=BBOX).items())
    out = {"items": [(i.id, i.properties.get("esa_worldcover:product_version")) for i in items]}
    item = sorted(items, key=lambda i: i.id)[-1]
    t0 = time.time()
    with rasterio.open(item.assets["map"].href) as src:
        b = transform_bounds("EPSG:4326", src.crs, *BBOX)
        win = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=win)
        out["read"] = {
            "item": item.id,
            "crs": str(src.crs),
            "res": src.res,
            "dtype": src.dtypes[0],
            "nodata": src.nodata,
            "window_shape": list(arr.shape),
            "seconds": round(time.time() - t0, 1),
        }
    vals, counts = np.unique(arr, return_counts=True)
    out["read"]["class_fraction"] = {int(v): round(int(c) / arr.size, 4) for v, c in zip(vals, counts)}
    out["bytes_recv_upper_bound"] = recv() - r0
    _add_bytes("worldcover", out["bytes_recv_upper_bound"])
    return out


# ---------------------------------------------------------------- cdse
def step_cdse() -> dict:
    import boto3
    from dotenv import load_dotenv

    load_dotenv(REPO / ".env")
    ak, sk = os.getenv("CDSE_S3_ACCESS_KEY"), os.getenv("CDSE_S3_SECRET_KEY")
    if not (ak and sk):
        return {"error": "CDSE_S3_ACCESS_KEY / CDSE_S3_SECRET_KEY not set in .env"}
    s3 = boto3.client(
        "s3",
        endpoint_url="https://eodata.dataspace.copernicus.eu",
        aws_access_key_id=ak,
        aws_secret_access_key=sk,
        region_name="default",
    )
    out = {}

    def s3_parts(href: str) -> tuple[str, str]:
        path = href.split("://", 1)[1]
        bucket, key = path.split("/", 1)
        return bucket, key

    s2 = json.loads((RESULTS / "sample_item_cdse_sentinel-2-l2a.json").read_text())
    akey = next(k for k in s2["assets"] if k.upper().startswith("B04_10M"))
    href = s2["assets"][akey]["href"]
    bucket, key = s3_parts(href)
    head = s3.head_object(Bucket=bucket, Key=key)
    size = head["ContentLength"]
    out["s2"] = {"item": s2["id"], "asset_key": akey, "href": href, "size_bytes": size}
    check_budget(size)
    if size <= 250_000_000:
        dest = DATA / Path(key).name
        t0 = time.time()
        s3.download_file(bucket, key, str(dest))
        out["s2"]["download_seconds"] = round(time.time() - t0, 1)
        out["s2"]["downloaded_bytes"] = dest.stat().st_size
        _add_bytes("cdse:s2:B04", dest.stat().st_size)
        try:
            out["s2"]["read"] = _window_read(str(dest), "red")
        except Exception as exc:
            out["s2"]["read"] = {"error": f"{type(exc).__name__}: {exc}"}
    else:
        out["s2"]["skipped"] = "asset larger than 250 MB per-asset cap"

    s1 = json.loads((RESULTS / "sample_item_cdse_sentinel-1-grd.json").read_text())
    s1_assets = {}
    for k, a in s1["assets"].items():
        h = a.get("href", "")
        if h.startswith("s3://"):
            b, kk = s3_parts(h)
            try:
                if kk.endswith("/"):
                    resp = s3.list_objects_v2(Bucket=b, Prefix=kk)
                    s1_assets[k] = {
                        "prefix": True,
                        "objects": resp.get("KeyCount"),
                        "total_bytes": sum(o["Size"] for o in resp.get("Contents", [])),
                    }
                else:
                    s1_assets[k] = {"size_bytes": s3.head_object(Bucket=b, Key=kk)["ContentLength"], "type": a.get("type")}
            except Exception as exc:
                s1_assets[k] = {"error": f"{type(exc).__name__}: {exc}"}
    out["s1_catalogue_only"] = {"item": s1["id"], "assets": s1_assets}
    return out


# ---------------------------------------------------------------- ghsl
def step_ghsl() -> dict:
    import zipfile

    import numpy as np
    import rasterio
    from pyproj import Transformer
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    tr = Transformer.from_crs("EPSG:4326", "ESRI:54009", always_xy=True)
    x, y = tr.transform((BBOX[0] + BBOX[2]) / 2, (BBOX[1] + BBOX[3]) / 2)
    # GHSL 54009 tiling: 1000 km tiles from (-18041000, 9000000); verified by HEAD below.
    col = int((x + 18041000) // 1_000_000) + 1
    row = int((9_000_000 - y) // 1_000_000) + 1
    base = (
        "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S_GLOBE_R2023A/"
        "GHS_BUILT_S_E2020_GLOBE_R2023A_54009_100/V1-0/tiles/"
    )
    name = f"GHS_BUILT_S_E2020_GLOBE_R2023A_54009_100_V1_0_R{row}_C{col}.zip"
    out = {"mollweide_xy": [x, y], "tile": name}
    h = requests.head(base + name, timeout=60)
    out["head_status"] = h.status_code
    if h.status_code != 200:
        return out
    size = int(h.headers.get("content-length", 0))
    check_budget(size)
    dest = DATA / name
    t0 = time.time()
    with requests.get(base + name, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    out["download_seconds"] = round(time.time() - t0, 1)
    out["downloaded_bytes"] = dest.stat().st_size
    _add_bytes("ghsl", dest.stat().st_size)
    with zipfile.ZipFile(dest) as z:
        out["zip_members"] = z.namelist()
        tif = next(n for n in z.namelist() if n.lower().endswith(".tif"))
    with rasterio.open(f"zip://{dest}!{tif}") as src:
        b = transform_bounds("EPSG:4326", src.crs, *BBOX)
        win = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=win)
        out["read"] = {
            "crs": src.crs.to_wkt()[:120] + "...",
            "res": src.res,
            "dtype": src.dtypes[0],
            "nodata": src.nodata,
            "window_shape": list(arr.shape),
        }
    valid = arr != (src.nodata if src.nodata is not None else -1)
    v = arr[valid]
    out["read"]["built_m2_per_100m_cell_p50_p98_max"] = (
        [float(np.percentile(v, 50)), float(np.percentile(v, 98)), float(v.max())] if v.size else None
    )
    out["read"]["share_cells_built_gt0"] = round(float((v > 0).mean()), 4) if v.size else None
    return out


# ---------------------------------------------------------------- osm
def step_osm() -> dict:
    s, w, n, e = BBOX[1], BBOX[0], BBOX[3], BBOX[2]
    q = f"""
[out:json][timeout:120];
(
  way["building"]({s},{w},{n},{e});
  relation["building"]({s},{w},{n},{e});
);
out tags meta;
"""
    t0 = time.time()
    r = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": q},
        headers={"User-Agent": "uae-geospatial-portfolio-stage03-probe/0.1"},
        timeout=300,
    )
    out = {"http_status": r.status_code, "seconds": round(time.time() - t0, 1), "bytes": len(r.content)}
    _add_bytes("osm", len(r.content))
    if r.status_code != 200:
        out["body_head"] = r.text[:500]
        return out
    els = r.json()["elements"]
    years = Counter(el.get("timestamp", "")[:4] for el in els)
    tags = Counter()
    for el in els:
        for k in ("start_date", "building:levels", "height", "addr:street", "name"):
            if k in el.get("tags", {}):
                tags[k] += 1
    out.update(
        {
            "n_buildings": len(els),
            "last_edit_year_hist": dict(sorted(years.items())),
            "tag_presence": {k: round(v / len(els), 4) for k, v in tags.items()} if els else {},
            "osm_base_timestamp": r.json().get("osm3s", {}).get("timestamp_osm_base"),
        }
    )
    q2 = f"""
[out:json][timeout:120];
(
  way["landuse"]({s},{w},{n},{e});
  way["natural"="water"]({s},{w},{n},{e});
  way["leisure"="park"]({s},{w},{n},{e});
);
out count;
"""
    r2 = requests.post("https://overpass-api.de/api/interpreter", data={"data": q2}, timeout=300,
                       headers={"User-Agent": "uae-geospatial-portfolio-stage03-probe/0.1"})
    _add_bytes("osm:count", len(r2.content))
    out["context_feature_count"] = r2.json().get("elements") if r2.status_code == 200 else r2.status_code
    return out


# ---------------------------------------------------------------- followup
def step_followup() -> dict:
    """Anomaly follow-ups: anonymous HTTPS read of the Earth Search S1 asset
    (metadata claims requester-pays) and CDSE S1 searches retried after a pause
    for years that returned HTTP 429 in the catalog step."""
    from pystac_client import Client

    it = json.loads((RESULTS / "sample_item_es_sentinel-1-grd.json").read_text())
    href = it["assets"]["vv"]["href"]
    bucket, key = href[5:].split("/", 1)
    url = f"https://{bucket}.s3.eu-central-1.amazonaws.com/{key}"
    r = requests.get(url, headers={"Range": "bytes=0-1023"}, timeout=60)
    out = {
        "es_s1_anonymous_https": {
            "href": href,
            "https_url_tested": url,
            "http_status": r.status_code,
            "ctype": r.headers.get("content-type"),
            "bytes": len(r.content),
        }
    }
    catalog = json.loads((RESULTS / "catalog.json").read_text())
    failed = [int(y) for y in catalog.get("cdse:sentinel-1-grd", {}).get("errors", {})]
    client = Client.open(CDSE_URL)
    retry = {}
    for y in failed:
        time.sleep(20)
        try:
            retry[y] = sum(
                1
                for _ in client.search(
                    collections=["sentinel-1-grd"],
                    bbox=BBOX,
                    datetime=f"{y}-01-01T00:00:00Z/{y}-12-31T23:59:59Z",
                    limit=100,
                ).items()
            )
        except Exception as exc:
            retry[y] = f"{type(exc).__name__}: {exc}"
    out["cdse_s1_retry_after_20s_pause"] = retry
    return out


# ---------------------------------------------------------------- runner
def _add_bytes(label: str, n: int) -> None:
    led = ledger()
    led["steps"][label] = n
    led["total_bytes_recv_upper_bound"] = sum(led["steps"].values())
    LEDGER.write_text(json.dumps(led, indent=2))


STEPS = {
    "env": step_env,
    "catalog": step_catalog,
    "access": step_access,
    "s2": step_s2,
    "s1": step_s1,
    "worldcover": step_worldcover,
    "cdse": step_cdse,
    "ghsl": step_ghsl,
    "osm": step_osm,
    "followup": step_followup,
}

if __name__ == "__main__":
    for step in sys.argv[1:]:
        log(f"START {step}")
        r0, t0 = recv(), time.time()
        try:
            check_budget()
            payload = STEPS[step]()
        except Exception as exc:
            payload = {"error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()}
        payload["_meta"] = {
            "step": step,
            "started_utc": datetime.fromtimestamp(t0, timezone.utc).isoformat(timespec="seconds"),
            "elapsed_s": round(time.time() - t0, 1),
            "system_bytes_recv_delta": recv() - r0,
        }
        if step in ("catalog", "access"):
            _add_bytes(step, payload["_meta"]["system_bytes_recv_delta"])
        write(step, payload)
        log(f"END {step} elapsed={payload['_meta']['elapsed_s']}s recv_delta={payload['_meta']['system_bytes_recv_delta']}")
