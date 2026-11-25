"""Stage 04 AOI comparison probe (catalogue + WorldCover) (evidence tool, not part of the product codebase).

Reproduces measurements in docs/feasibility-pilot.md. Network access is bounded by the
approved Stage 04 budget (ADR 0012); read the report before running.
Setup: reuse the Stage 03 disposable venv (see tools/probes/stage03_source_probe.py); no extra packages.
Usage (from the repository root):
    .scratch/stage03/venv/Scripts/python tools/probes/stage04_aoi_compare.py
Outputs go to .scratch/stage04/out/ (git-ignored). Byte counts are system-wide psutil
bytes_recv deltas, i.e. UPPER BOUNDS for the script's own traffic.
Original run notes:
    Stage 04 AOI comparison probe (disposable). Catalogue + WorldCover only; aborts at 100 MB.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import planetary_computer
import psutil
import rasterio
from pystac_client import Client
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from shapely.geometry import box, shape

OUT = Path(__file__).resolve().parents[2] / ".scratch" / "stage04" / "out"
OUT.mkdir(exist_ok=True)
PC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
ES_URL = "https://earth-search.aws.element84.com/v1"
CDSE_URL = "https://stac.dataspace.copernicus.eu/v1"
BUDGET = 100 * 1024**2
BOXES = {
    "a_coastal_islands": (54.30, 24.40, 54.65, 24.60),
    "b_al_ain_inland": (55.60, 24.05, 55.85, 24.30),
    "c_mainland_corridor": (54.55, 24.25, 54.80, 24.45),
}
R0 = psutil.net_io_counters().bytes_recv
T0 = time.time()


def used() -> int:
    return psutil.net_io_counters().bytes_recv - R0


def guard() -> None:
    if used() > BUDGET:
        sys.exit(f"ABORT: transfer upper bound {used()} B exceeds 100 MB budget")


def search(client, collection, bbox, dt, fields, retries=3):
    for attempt in range(retries):
        try:
            s = client.search(collections=[collection], bbox=bbox, datetime=dt, limit=250, fields=fields)
            return list(s.items_as_dicts())
        except Exception as exc:  # 429 throttling on CDSE
            if attempt == retries - 1:
                raise
            print(f"  retry {collection} {dt}: {type(exc).__name__}", flush=True)
            time.sleep(20)


def frac(geom, aoi) -> float:
    return round(shape(geom).intersection(aoi).area / aoi.area, 3)


def s2_es(name, bbox):
    client = Client.open(ES_URL)
    aoi = box(*bbox)
    fields = {"include": ["id", "geometry", "properties.datetime", "properties.eo:cloud_cover",
                          "properties.grid:code"], "exclude": ["assets", "links"]}
    monthly, monthly_cc30, tiles, cov = Counter(), Counter(), Counter(), defaultdict(list)
    for y in range(2018, 2027):
        items = search(client, "sentinel-2-c1-l2a", bbox, f"{y}-01-01/{y}-12-31", fields)
        for it in items:
            p = it["properties"]
            m = p["datetime"][:7]
            monthly[m] += 1
            if (p.get("eo:cloud_cover") or 100) <= 30:
                monthly_cc30[m] += 1
            t = p.get("grid:code") or it["id"].split("_")[1]
            tiles[t] += 1
            cov[t].append(frac(it["geometry"], aoi))
        guard()
    tile_cov = {t: round(float(np.median(v)), 3) for t, v in cov.items()}
    return {"monthly": dict(sorted(monthly.items())), "monthly_cc30": dict(sorted(monthly_cc30.items())),
            "tiles": dict(tiles), "tile_median_aoi_fraction": tile_cov}


def s2_cdse_2022(bbox):
    client = Client.open(CDSE_URL)
    items = search(client, "sentinel-2-l2a", bbox, "2021-12-01/2022-12-31",
                   {"include": ["id", "properties.datetime"], "exclude": ["assets", "links"]})
    return dict(sorted(Counter(it["properties"]["datetime"][:7] for it in items).items()))


def s1_pc(name, bbox):
    client = Client.open(PC_URL)
    aoi = box(*bbox)
    fields = {"include": ["id", "geometry", "properties.datetime", "properties.sat:relative_orbit",
                          "properties.sat:orbit_state"], "exclude": ["assets", "links"]}
    per_track = defaultdict(Counter)       # track -> DJF season -> passes (distinct days)
    days = defaultdict(lambda: defaultdict(set))
    cov = defaultdict(lambda: defaultdict(float))  # track -> date -> summed slice fraction
    for y in range(2018, 2027):
        items = search(client, "sentinel-1-grd", bbox, f"{y}-01-01/{y}-12-31", fields)
        for it in items:
            p = it["properties"]
            trk = f"{p.get('sat:orbit_state')}/rel{p.get('sat:relative_orbit')}"
            d = p["datetime"][:10]
            cov[trk][d] += frac(it["geometry"], aoi)
            mm, yy = int(d[5:7]), int(d[:4])
            if mm in (12, 1, 2):
                season = f"{yy if mm == 12 else yy - 1}/{str((yy + 1 if mm == 12 else yy))[2:]}"
                days[trk][season].add(d)
        guard()
    for trk, s in days.items():
        for season, ds in s.items():
            per_track[trk][season] = len(ds)
    track_cov = {t: round(float(np.median([min(v, 1.0) for v in dd.values()])), 3) for t, dd in cov.items()}
    return {"djf_passes_per_track": {t: dict(sorted(c.items())) for t, c in per_track.items()},
            "track_median_aoi_fraction": track_cov}


def worldcover(bbox):
    client = Client.open(PC_URL, modifier=planetary_computer.sign_inplace)
    items = list(client.search(collections=["esa-worldcover"], bbox=bbox,
                               datetime="2021-01-01/2021-12-31").items())
    counts, total = Counter(), 0
    for item in items:
        with rasterio.open(item.assets["map"].href) as src:
            b = transform_bounds("EPSG:4326", src.crs, *bbox)
            win = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
            arr = src.read(1, window=win, boundless=True, fill_value=0)
        v, c = np.unique(arr[arr > 0], return_counts=True)
        counts.update(dict(zip(v.tolist(), c.tolist())))
        total += int((arr > 0).sum())
    names = {10: "tree", 20: "shrub", 30: "grass", 40: "cropland", 50: "built", 60: "bare",
             70: "snow", 80: "water", 90: "wetland", 95: "mangrove", 100: "moss"}
    return {"items": [i.id for i in items],
            "class_fraction": {names.get(k, k): round(n / total, 4) for k, n in sorted(counts.items())}}


def main():
    res = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "boxes": BOXES, "results": {}}
    for name, bbox in BOXES.items():
        t = time.time()
        r = {}
        print(f"[{name}] s2 es", flush=True); r["s2_es"] = s2_es(name, bbox)
        print(f"[{name}] s1 pc", flush=True); r["s1_pc"] = s1_pc(name, bbox)
        print(f"[{name}] worldcover", flush=True); r["worldcover"] = worldcover(bbox)
        print(f"[{name}] cdse 2022", flush=True); r["s2_cdse_2021_12_to_2022_12"] = s2_cdse_2022(bbox)
        r["seconds"] = round(time.time() - t, 1)
        res["results"][name] = r
        guard()
        time.sleep(5)
    res["bytes_recv_upper_bound"] = used()
    res["elapsed_s"] = round(time.time() - T0, 1)
    (OUT / "compare.json").write_text(json.dumps(res, indent=1))
    print(f"done: {res['elapsed_s']} s, {used()/1e6:.1f} MB (system-wide upper bound)")


if __name__ == "__main__":
    main()
