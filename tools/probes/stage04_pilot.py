"""Stage 04 feasibility pilot 1 (AOI (c): S2 NDVI + S1 DN-squared proxy) (evidence tool, not part of the product codebase).

Reproduces measurements in docs/feasibility-pilot.md. Network access is bounded by the
approved Stage 04 budget (ADR 0012); read the report before running.
Setup: reuse the Stage 03 disposable venv (see tools/probes/stage03_source_probe.py); no extra packages.
Usage (from the repository root):
    .scratch/stage03/venv/Scripts/python tools/probes/stage04_pilot.py
Outputs go to .scratch/stage04/out/ (git-ignored). Byte counts are system-wide psutil
bytes_recv deltas, i.e. UPPER BOUNDS for the script's own traffic.
Original run notes:
    Stage 04 feasibility pilot (disposable). AOI (c), P1 pilot windows, indicators I2.
    
    Approved plan (2026-11-24): S2 Earth Search c1, 6 clearest full-coverage dates per window ->
    median NDVI composite; S1 PC GRD asc rel130, <=7 passes per window -> mean DN^2 -> dB proxy.
    Sites C3/V1 are fixed by WorldCover rules *before* indicators are computed. Aborts at 1.9 GB.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import warnings
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("GDAL_HTTP_MERGE_CONSECUTIVE_RANGES", "YES")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "4")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "3")

import numpy as np
import planetary_computer
import psutil
import rasterio
from pyproj import Transformer
from pystac_client import Client
from rasterio.enums import Resampling
from rasterio.errors import NotGeoreferencedWarning
from rasterio.features import geometry_mask
from rasterio.transform import Affine
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds
from shapely.geometry import Point, box, mapping, shape
from shapely.ops import transform as shp_transform, unary_union

warnings.filterwarnings("ignore", category=NotGeoreferencedWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

HERE = Path(__file__).resolve().parents[2] / ".scratch" / "stage04"
OUT = HERE / "out" / "pilot"
CACHE = OUT / "cache"
QL = OUT / "quicklooks"
for d in (OUT, CACHE, QL):
    d.mkdir(parents=True, exist_ok=True)

ES_URL = "https://earth-search.aws.element84.com/v1"
PC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
AOI_BBOX = (54.55, 24.25, 54.80, 24.45)
DST_CRS = "EPSG:32640"
RES = 10
ABORT_BYTES = 1_900_000_000  # the recorded run 2 used 1.9 GB minus 580 MB (run 1 was stopped)
S2_DATES_PER_WINDOW = 6
S1_PASSES_PER_WINDOW = 7
S1_TRACK = ("ascending", 130)
SCL_MASK = {0, 1, 3, 8, 9, 10}
PILOT_WINDOWS = {"2019/20": "2019-12-01/2020-02-29", "2024/25": "2024-12-01/2025-02-28",
                 "2025/26": "2025-12-01/2026-02-28"}
P1_WINDOWS = {"2019/20": "2019-12-01/2020-02-29", "2020/21": "2020-12-01/2021-02-28",
              "2021/22": "2021-12-01/2021-12-31", "2022/23": "2022-12-01/2023-02-28",
              "2023/24": "2023-12-01/2024-02-29", "2024/25": "2024-12-01/2025-02-28",
              "2025/26": "2025-12-01/2026-02-28"}
BASELINE = "2019/20"
FIXED_SITES = {"U1": ("urban change: Riyadh City", 54.757, 24.353),
               "C1": ("urban control: Khalifa City A", 54.569, 24.424),
               "C2": ("urban control: MBZ City", 54.565, 24.340)}

# ---------------------------------------------------------------- grid
AOI = box(*AOI_BBOX)
to_utm = Transformer.from_crs("EPSG:4326", DST_CRS, always_xy=True).transform
to_geo = Transformer.from_crs(DST_CRS, "EPSG:4326", always_xy=True).transform
_b = transform_bounds("EPSG:4326", DST_CRS, *AOI_BBOX)
XMIN, YMIN = np.floor(_b[0] / RES) * RES, np.floor(_b[1] / RES) * RES
XMAX, YMAX = np.ceil(_b[2] / RES) * RES, np.ceil(_b[3] / RES) * RES
W, H = int((XMAX - XMIN) / RES), int((YMAX - YMIN) / RES)
DST_T = Affine(RES, 0, XMIN, 0, -RES, YMAX)
AOI_UTM = shp_transform(to_utm, AOI)
IN_AOI = ~geometry_mask([mapping(AOI_UTM)], out_shape=(H, W), transform=DST_T)

# ---------------------------------------------------------------- measurement
R0 = psutil.net_io_counters().bytes_recv
T0 = time.time()
STEPS: dict[str, dict] = {}


class PeakRSS(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.proc, self.peak, self.running = psutil.Process(), 0, True

    def run(self):
        while self.running:
            self.peak = max(self.peak, self.proc.memory_info().rss)
            time.sleep(0.25)


MON = PeakRSS()


def net() -> int:
    return psutil.net_io_counters().bytes_recv - R0


def guard() -> None:
    if net() > ABORT_BYTES:
        save({"aborted": f"transfer upper bound {net()} B > {ABORT_BYTES} B"})
        sys.exit("ABORT: pilot transfer budget reached")


def dir_bytes(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def log(msg: str) -> None:
    print(f"[{time.time() - T0:7.1f}s | {net() / 1e6:8.1f} MB | rss {MON.peak / 1e9:4.2f} GB] {msg}", flush=True)


class Step:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.t, self.b = time.time(), net()
        log(f"start {self.name}")

    def __exit__(self, *exc):
        STEPS[self.name] = {"seconds": round(time.time() - self.t, 1), "bytes_upper_bound": net() - self.b}
        log(f"end {self.name}: {STEPS[self.name]}")
        guard()


RESULTS: dict = {}


def save(extra: dict | None = None) -> None:
    if extra:
        RESULTS.update(extra)
    (OUT / "results.json").write_text(json.dumps(RESULTS, indent=1, default=str))


# ---------------------------------------------------------------- io helpers
def warp_read(href: str, resampling=Resampling.nearest, gcp: bool = False, grid=None) -> np.ndarray:
    t, w, h = grid or (DST_T, W, H)
    for attempt in range(3):
        try:
            with rasterio.open(href) as src:
                kw = dict(crs=DST_CRS, transform=t, width=w, height=h, resampling=resampling,
                          nodata=0, src_nodata=0)
                if gcp:
                    # An explicit target grid over a GCP-only source yields a constant array
                    # (measured 2026-11-24), so geocode to a native 10 m grid first, then align.
                    with WarpedVRT(src, src_crs=src.gcps[1], crs=DST_CRS, resolution=RES,
                                   src_nodata=0, nodata=0) as geo, WarpedVRT(geo, **kw) as vrt:
                        return vrt.read(1)
                with WarpedVRT(src, **kw) as vrt:
                    return vrt.read() if vrt.count > 1 else vrt.read(1)
        except rasterio.errors.RasterioIOError as exc:
            if attempt == 2:
                raise
            log(f"  retry read ({type(exc).__name__}): {href[:90]}")
            time.sleep(10)


def write_png(path: Path, rgb: np.ndarray) -> None:
    with rasterio.open(path, "w", driver="PNG", width=rgb.shape[2], height=rgb.shape[1], count=3,
                       dtype="uint8") as dst:
        dst.write(rgb)


def diverging(a: np.ndarray, lim: float) -> np.ndarray:
    t = np.clip((a + lim) / (2 * lim), 0, 1)
    r = np.where(t < 0.5, 2 * t, 1.0)
    g = np.where(t < 0.5, 2 * t, 2 - 2 * t)
    b = np.where(t < 0.5, 1.0, 2 - 2 * t)
    rgb = (np.stack([r, g, b]) * 255).astype("uint8")
    rgb[:, ~np.isfinite(a)] = 128
    return rgb


def write_tif(path: Path, arr: np.ndarray, nodata=None) -> None:
    with rasterio.open(path, "w", driver="GTiff", width=W, height=H, count=1, dtype=arr.dtype, crs=DST_CRS,
                       transform=DST_T, compress="deflate", tiled=True, nodata=nodata) as dst:
        dst.write(arr, 1)


def px(lon: float, lat: float) -> tuple[int, int]:
    x, y = to_utm(lon, lat)
    return int((YMAX - y) / RES), int((x - XMIN) / RES)


def block_slice(row: int, col: int, half: int = 50):
    return slice(max(row - half, 0), row + half), slice(max(col - half, 0), col + half)


# ---------------------------------------------------------------- catalogue
def s2_eligible(client: Client, dt: str) -> list[dict]:
    items = list(client.search(collections=["sentinel-2-c1-l2a"], bbox=AOI_BBOX, datetime=dt).items())
    by_date = defaultdict(list)
    for it in items:
        if (it.properties.get("eo:cloud_cover") or 100) <= 30:
            by_date[it.datetime.date().isoformat()].append(it)
    out = []
    for d, its in by_date.items():
        cov = unary_union([shape(i.geometry) for i in its]).intersection(AOI).area / AOI.area
        if cov >= 0.98:
            out.append({"date": d, "items": its, "coverage": round(cov, 3),
                        "mean_cc": float(np.mean([i.properties["eo:cloud_cover"] for i in its]))})
    return sorted(out, key=lambda x: x["mean_cc"])


def s1_passes(client: Client, dt: str) -> list[dict]:
    items = list(client.search(collections=["sentinel-1-grd"], bbox=AOI_BBOX, datetime=dt).items())
    by_date = defaultdict(list)
    for it in items:
        p = it.properties
        if (p.get("sat:orbit_state"), p.get("sat:relative_orbit")) == S1_TRACK:
            by_date[it.datetime.date().isoformat()].append(it)
    out = []
    for d, its in sorted(by_date.items()):
        cov = unary_union([shape(i.geometry) for i in its]).intersection(AOI).area / AOI.area
        out.append({"date": d, "items": its, "coverage": round(cov, 3),
                    "platforms": sorted({str(i.properties.get("platform")).upper() for i in its})})
    return out


# ---------------------------------------------------------------- steps
def step_worldcover() -> np.ndarray:
    client = Client.open(PC_URL, modifier=planetary_computer.sign_inplace)
    items = list(client.search(collections=["esa-worldcover"], bbox=AOI_BBOX, datetime="2021").items())
    wc = np.zeros((H, W), "uint8")
    for it in items:
        a = warp_read(it.assets["map"].href)
        wc = np.where((wc == 0) & (a > 0), a, wc)
    RESULTS["worldcover_items"] = [i.id for i in items]
    return wc


def fix_rule_sites(wc: np.ndarray) -> dict:
    """C3 and V1 by documented rules on 1 km blocks fully inside the AOI (before any indicator)."""
    blocks = []
    for r0 in range(0, H - 100, 100):
        for c0 in range(0, W - 100, 100):
            if not IN_AOI[r0:r0 + 100, c0:c0 + 100].all():
                continue
            b = wc[r0:r0 + 100, c0:c0 + 100]
            blocks.append({"r": r0 + 50, "c": c0 + 50, "bare": float((b == 60).mean()),
                           "built": float((b == 50).mean()),
                           "veg": float(np.isin(b, (10, 30, 40)).mean())})
    built = np.array([(b["r"], b["c"]) for b in blocks if b["built"] >= 0.05])
    bare = [b for b in blocks if b["bare"] >= 0.99]
    for b in bare:
        b["dist_px"] = float(np.min(np.hypot(built[:, 0] - b["r"], built[:, 1] - b["c"])))
    c3 = max(bare, key=lambda b: b["dist_px"])
    v1 = max(blocks, key=lambda b: b["veg"])
    sites = {}
    for k, (label, lon, lat) in FIXED_SITES.items():
        r, c = px(lon, lat)
        sites[k] = {"label": label, "lon": lon, "lat": lat, "row": r, "col": c, "rule": "pre-registered point"}
    for k, b, label, rule in (("C3", c3, "desert control", "bare>=0.99, max distance to blocks with built>=0.05"),
                              ("V1", v1, "vegetation site", "max tree+grass+cropland share")):
        lon, lat = to_geo(XMIN + (b["c"] + 0.5) * RES, YMAX - (b["r"] + 0.5) * RES)
        sites[k] = {"label": label, "lon": round(lon, 5), "lat": round(lat, 5), "row": b["r"], "col": b["c"],
                    "rule": rule, "block_stats": b}
    return sites


def s2_date(entry: dict, wc: np.ndarray) -> tuple[np.ndarray, dict]:
    f = CACHE / f"s2_{entry['date']}.npy"
    if f.exists():
        return np.load(f), json.loads((CACHE / f"s2_{entry['date']}.json").read_text())
    b0, t0 = net(), time.time()
    its = sorted(entry["items"], key=lambda i: "MGRS-40" not in str(i.properties.get("grid:code")))
    red = np.zeros((H, W), "uint16"); nir = np.zeros_like(red); scl = np.zeros((H, W), "uint8")
    ef = its[0].assets["red"].extra_fields
    rb = (ef.get("raster:bands") or ef.get("bands") or [{}])[0]
    scale, offset = rb.get("scale", rb.get("raster:scale")), rb.get("offset", rb.get("raster:offset"))
    if scale is None or offset is None:
        raise ValueError(f"no scale/offset metadata on {its[0].id}")
    for it in its:
        need = scl == 0
        if not (need & IN_AOI).any():
            break
        s = warp_read(it.assets["scl"].href)
        r = warp_read(it.assets["red"].href)
        n = warp_read(it.assets["nir"].href)
        fill = need & (s > 0) & (r > 0)
        scl[fill], red[fill], nir[fill] = s[fill], r[fill], n[fill]
        guard()
    rr, nn = red * scale + offset, nir * scale + offset
    valid = (scl > 0) & ~np.isin(scl, list(SCL_MASK)) & (rr > 0) & (nn > 0) & IN_AOI
    ndvi = np.where(valid, (nn - rr) / (nn + rr), np.nan).astype("float32")
    bare = (wc == 60) & IN_AOI & (scl > 0)
    meta = {"items": [i.id for i in its], "scale": scale, "offset": offset,
            "valid_fraction_aoi": round(float(valid.sum() / IN_AOI.sum()), 4),
            "scl2_share_on_bare": round(float((scl[bare] == 2).mean()), 5) if bare.any() else None,
            "scl_masked_share_aoi": round(float(np.isin(scl[IN_AOI], list(SCL_MASK - {0})).mean()), 4),
            "bytes_upper_bound": net() - b0, "seconds": round(time.time() - t0, 1)}
    np.save(f, ndvi)
    (CACHE / f"s2_{entry['date']}.json").write_text(json.dumps(meta))
    return ndvi, meta


def s1_pass(entry: dict) -> dict[str, np.ndarray]:
    f = CACHE / f"s1_{entry['date']}.npz"
    if f.exists():
        z = np.load(f)
        return {k: z[k] for k in z.files}
    out = {}
    for pol in ("vv", "vh"):
        dn = np.zeros((H, W), "uint16")
        for it in entry["items"]:
            a = warp_read(planetary_computer.sign(it.assets[pol].href), gcp=True)
            m = (dn == 0) & (a > 0)
            dn[m] = a[m]
            guard()
        out[pol] = dn
    np.savez_compressed(f, **out)
    return out


def site_stats(arr: np.ndarray, s: dict) -> float | None:
    rs, cs = block_slice(s["row"], s["col"])
    v = arr[rs, cs][IN_AOI[rs, cs]]
    v = v[np.isfinite(v)]
    return round(float(np.median(v)), 4) if v.size >= 100 else None


def quicklook_rgb(entry: dict, s: dict, name: str) -> None:
    """True-colour 3 km crop around a site from the clearest date (same-source visual review)."""
    x, y = to_utm(s["lon"], s["lat"])
    t = Affine(RES, 0, x - 1500, 0, -RES, y + 1500)
    pt = Point(s["lon"], s["lat"])
    its = [i for i in entry["items"] if shape(i.geometry).contains(pt)] or entry["items"]
    its = sorted(its, key=lambda i: "MGRS-40" not in str(i.properties.get("grid:code")))
    rgb = warp_read(its[0].assets["visual"].href, grid=(t, 300, 300))
    write_png(QL / f"{name}_rgb.png", rgb.astype("uint8"))


def main() -> None:
    MON.start()
    RESULTS.update({"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "aoi_bbox": AOI_BBOX,
                    "grid": {"crs": DST_CRS, "res_m": RES, "width": W, "height": H, "x0": XMIN, "y0": YMAX,
                             "aoi_pixels": int(IN_AOI.sum())},
                    "env": {"python": sys.version.split()[0], "rasterio": rasterio.__version__,
                            "gdal": rasterio.__gdal_version__, "cpu_logical": psutil.cpu_count(),
                            "ram_gb": round(psutil.virtual_memory().total / 1e9, 1)}})
    disk0 = dir_bytes(OUT)
    es = Client.open(ES_URL)
    pc = Client.open(PC_URL)

    with Step("worldcover_and_sites"):
        wc = step_worldcover()
        land = IN_AOI & (wc != 80) & (wc > 0)
        sites = fix_rule_sites(wc)
        RESULTS["sites"] = sites
        (OUT / "sites_registered.json").write_text(json.dumps(sites, indent=1))
        save()

    with Step("catalogue_p1"):
        cat = {}
        for wname, dt in P1_WINDOWS.items():
            s2 = s2_eligible(es, dt)
            s1 = s1_passes(pc, dt)
            cat[wname] = {"dt": dt, "s2_eligible_dates": len(s2), "s2": s2, "s1_passes": len(s1), "s1": s1,
                          "s1_slices": sum(len(p["items"]) for p in s1)}
        RESULTS["catalogue_p1"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("s2", "s1")}
                                   for k, v in cat.items()}
        save()

    ndvi_comp, s1_db, coverage, s2_meta, s1_meta = {}, {}, {}, {}, {}
    for wname in PILOT_WINDOWS:
        sel = cat[wname]["s2"][:S2_DATES_PER_WINDOW]
        with Step(f"s2_{wname}"):
            stack, metas = [], []
            for e in sel:
                nd, meta = s2_date(e, wc)
                meta.update(date=e["date"], coverage=e["coverage"], mean_cc=e["mean_cc"])
                stack.append(nd); metas.append(meta)
                log(f"  s2 {wname} {e['date']} valid={meta['valid_fraction_aoi']}")
            stack = np.stack(stack)
            cnt = np.isfinite(stack).sum(0).astype("uint8")
            ndvi_comp[wname] = np.nanmedian(stack, axis=0).astype("float32")
            del stack
            coverage[wname] = {"land_ge1": round(float((cnt[land] >= 1).mean()), 4),
                               "land_ge3": round(float((cnt[land] >= 3).mean()), 4),
                               "aoi_ge1": round(float((cnt[IN_AOI] >= 1).mean()), 4),
                               "median_count_land": float(np.median(cnt[land]))}
            s2_meta[wname] = metas
            write_tif(OUT / f"ndvi_median_{wname.replace('/', '_')}.tif", ndvi_comp[wname], nodata=np.nan)
            write_tif(OUT / f"ndvi_count_{wname.replace('/', '_')}.tif", cnt)
        passes = cat[wname]["s1"]
        if len(passes) > S1_PASSES_PER_WINDOW:
            idx = np.unique(np.linspace(0, len(passes) - 1, S1_PASSES_PER_WINDOW).round().astype(int))
            passes = [passes[i] for i in idx]
        with Step(f"s1_{wname}"):
            sums = {p: np.zeros((H, W), "float64") for p in ("vv", "vh")}
            cnts = {p: np.zeros((H, W), "uint8") for p in ("vv", "vh")}
            metas = []
            for e in passes:
                b0 = net()
                dn = s1_pass(e)
                for p in ("vv", "vh"):
                    v = dn[p] > 0
                    sums[p][v] += dn[p][v].astype("float64") ** 2
                    cnts[p] += v
                metas.append({"date": e["date"], "slices": len(e["items"]), "coverage": e["coverage"],
                              "platforms": e["platforms"], "bytes_upper_bound": net() - b0,
                              "vv_valid_fraction_aoi": round(float((dn["vv"][IN_AOI] > 0).mean()), 4)})
                log(f"  s1 {wname} {e['date']} slices={len(e['items'])}")
            s1_db[wname] = {p: np.where(cnts[p] > 0, 10 * np.log10(sums[p] / np.maximum(cnts[p], 1)), np.nan)
                            .astype("float32") for p in ("vv", "vh")}
            s1_meta[wname] = metas
            coverage[wname]["s1_vv_aoi_ge1"] = round(float((cnts["vv"][IN_AOI] >= 1).mean()), 4)
            for p in ("vv", "vh"):
                write_tif(OUT / f"s1_{p}_meandb_proxy_{wname.replace('/', '_')}.tif", s1_db[wname][p], nodata=np.nan)
        RESULTS.update(coverage=coverage, s2_dates=s2_meta, s1_passes=s1_meta, steps=STEPS)
        save()

    with Step("indicators_sites_quicklooks"):
        deltas = {}
        for wname in PILOT_WINDOWS:
            if wname == BASELINE:
                continue
            deltas[wname] = {"dndvi": ndvi_comp[wname] - ndvi_comp[BASELINE],
                             "dvv": s1_db[wname]["vv"] - s1_db[BASELINE]["vv"],
                             "dvh": s1_db[wname]["vh"] - s1_db[BASELINE]["vh"]}
            tag = wname.replace("/", "_")
            write_png(QL / f"aoi_dndvi_{tag}.png", diverging(deltas[wname]["dndvi"][::4, ::4], 0.3))
            write_png(QL / f"aoi_dvv_{tag}.png", diverging(deltas[wname]["dvv"][::4, ::4], 6.0))
        # exploratory blocks (labelled as such; not pre-registered)
        wins = list(deltas)
        expl = {"gain_ndvi": (None, -9), "loss_ndvi": (None, 9), "rise_vv": (None, -99)}
        for r0 in range(50, H - 50, 100):
            for c0 in range(50, W - 50, 100):
                s = {"row": r0, "col": c0}
                if not IN_AOI[r0 - 50:r0 + 50, c0 - 50:c0 + 50].all():
                    continue
                g = [site_stats(deltas[w]["dndvi"], s) for w in wins]
                v = [site_stats(deltas[w]["dvv"], s) for w in wins]
                if None not in g:
                    if min(g) > expl["gain_ndvi"][1]:
                        expl["gain_ndvi"] = (s, min(g))
                    if max(g) < expl["loss_ndvi"][1]:
                        expl["loss_ndvi"] = (s, max(g))
                if None not in v and min(v) > expl["rise_vv"][1]:
                    expl["rise_vv"] = (s, min(v))
        all_sites = dict(sites)
        for k, (s, _) in expl.items():
            if s:
                lon, lat = to_geo(XMIN + (s["col"] + 0.5) * RES, YMAX - (s["row"] + 0.5) * RES)
                all_sites[f"X_{k}"] = {"label": f"exploratory: {k}", "lon": round(lon, 5), "lat": round(lat, 5),
                                       "row": s["row"], "col": s["col"], "rule": "exploratory (post-hoc)"}
        stats = {}
        for k, s in all_sites.items():
            stats[k] = {"label": s["label"], "lon": s["lon"], "lat": s["lat"], "rule": s["rule"],
                        "ndvi": {w: site_stats(ndvi_comp[w], s) for w in PILOT_WINDOWS},
                        "vv_db": {w: site_stats(s1_db[w]["vv"], s) for w in PILOT_WINDOWS},
                        "dndvi": {w: site_stats(deltas[w]["dndvi"], s) for w in wins},
                        "dvv_db": {w: site_stats(deltas[w]["dvv"], s) for w in wins},
                        "dvh_db": {w: site_stats(deltas[w]["dvh"], s) for w in wins},
                        "wc2021_fractions": {str(c): round(float(n), 3) for c, n in zip(
                            *np.unique(wc[block_slice(s["row"], s["col"])], return_counts=True))}}
            tot = sum(np.unique(wc[block_slice(s["row"], s["col"])], return_counts=True)[1])
            stats[k]["wc2021_fractions"] = {c: round(n / tot, 3) for c, n in
                                            ((c, float(n)) for c, n in stats[k]["wc2021_fractions"].items())}
            for w in PILOT_WINDOWS:
                quicklook_rgb(cat[w]["s2"][0], s, f"{k}_{w.replace('/', '_')}")
            for w in wins:
                rs, cs = slice(max(s["row"] - 150, 0), s["row"] + 150), slice(max(s["col"] - 150, 0), s["col"] + 150)
                write_png(QL / f"{k}_dndvi_{w.replace('/', '_')}.png", diverging(deltas[w]["dndvi"][rs, cs], 0.3))
                write_png(QL / f"{k}_dvv_{w.replace('/', '_')}.png", diverging(deltas[w]["dvv"][rs, cs], 6.0))
        RESULTS["site_stats"] = stats

    MON.running = False
    RESULTS.update(steps=STEPS, total_seconds=round(time.time() - T0, 1), bytes_upper_bound_total=net(),
                   peak_rss_bytes=MON.peak, disk_growth_bytes=dir_bytes(OUT) - disk0,
                   disk_cache_bytes=dir_bytes(CACHE),
                   finished_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    save()
    log("done")


if __name__ == "__main__":
    main()
