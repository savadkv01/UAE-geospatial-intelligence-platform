"""Stage 04 feasibility pilot 2 (calibrated sigma0 at sites + Al Ain vegetation patch) (evidence tool, not part of the product codebase).

Reproduces measurements in docs/feasibility-pilot.md. Network access is bounded by the
approved Stage 04 budget (ADR 0012); read the report before running. Needs pilot 1 outputs
(tools/probes/stage04_pilot.py) in .scratch/stage04/out/pilot/.
Setup: reuse the Stage 03 disposable venv (see tools/probes/stage03_source_probe.py); no extra packages.
Usage (from the repository root):
    .scratch/stage03/venv/Scripts/python tools/probes/stage04_pilot2.py
Outputs go to .scratch/stage04/out/ (git-ignored). Byte counts are system-wide psutil
bytes_recv deltas, i.e. UPPER BOUNDS for the script's own traffic.
Original run notes:
    Stage 04 pilot 2 (disposable). Approved 2026-11-24.
    
    Part A: LUT-calibrated, thermal-noise-removed S1 VV sigma0 in native radar geometry at the SAME
            pre-registered sites (U1, C1, C2, C3) and passes as pilot 1; gates G4/G5a unchanged.
    Part B: Al Ain vegetation patch (10x10 km, rule-selected from WorldCover 2021, UAE-only), S2 NDVI
            with SCL water (6) excluded; gate G5b' (area-based). Cumulative pilot cap 2.6 GB.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import warnings
import xml.etree.ElementTree as ET
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
import requests
from pyproj import Transformer
from pystac_client import Client
from rasterio.enums import Resampling
from rasterio.errors import NotGeoreferencedWarning
from rasterio.transform import Affine, rowcol
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds
from rasterio.windows import Window
from shapely.geometry import Point, box, shape
from shapely.ops import unary_union

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parents[2] / ".scratch" / "stage04"
P1 = HERE / "out" / "pilot"
OUT = HERE / "out" / "pilot2"
QL = OUT / "quicklooks"
CACHE = OUT / "cache"
for d in (OUT, QL, CACHE):
    d.mkdir(parents=True, exist_ok=True)

ES_URL = "https://earth-search.aws.element84.com/v1"
PC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
DST_CRS = "EPSG:32640"
PRIOR_PILOT_BYTES = 1_785_000_000  # pilot 1: 567.5 MB (run 1) + 1,209.7 MB (run 2) + ~5 MB diagnostics
CAP_BYTES = 2_600_000_000
AOI_C = (54.55, 24.25, 54.80, 24.45)
SEARCH_REGION = (55.40, 23.95, 55.74, 24.40)
WINDOWS = {"2019/20": "2019-12-01/2020-02-29", "2024/25": "2024-12-01/2025-02-28",
           "2025/26": "2025-12-01/2026-02-28"}
BASELINE = "2019/20"
SCL_MASK = {0, 1, 3, 8, 9, 10}
WATER = 6
HALF = 50  # native px (~10 m) -> ~1 km block

to_utm = Transformer.from_crs("EPSG:4326", DST_CRS, always_xy=True).transform
to_geo = Transformer.from_crs(DST_CRS, "EPSG:4326", always_xy=True).transform
R0 = psutil.net_io_counters().bytes_recv
T0 = time.time()
STEPS: dict = {}
RESULTS: dict = {}


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


def save() -> None:
    (OUT / "results.json").write_text(json.dumps(RESULTS, indent=1, default=str))


def guard() -> None:
    if PRIOR_PILOT_BYTES + net() > CAP_BYTES:
        RESULTS["aborted"] = f"cumulative {PRIOR_PILOT_BYTES + net()} B > {CAP_BYTES} B"
        save()
        sys.exit("ABORT: cumulative pilot cap reached")


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


def make_grid(bbox, res):
    b = transform_bounds("EPSG:4326", DST_CRS, *bbox)
    x0, y0 = np.floor(b[0] / res) * res, np.ceil(b[3] / res) * res
    w, h = int((np.ceil(b[2] / res) * res - x0) / res), int((y0 - np.floor(b[1] / res) * res) / res)
    return Affine(res, 0, x0, 0, -res, y0), w, h


def warp_read(href, grid, resampling=Resampling.nearest):
    t, w, h = grid
    for attempt in range(3):
        try:
            with rasterio.open(href) as src, WarpedVRT(src, crs=DST_CRS, transform=t, width=w, height=h,
                                                       resampling=resampling, nodata=0, src_nodata=0) as v:
                return v.read() if v.count > 1 else v.read(1)
        except rasterio.errors.RasterioIOError:
            if attempt == 2:
                raise
            time.sleep(10)


def write_png(path, rgb):
    with rasterio.open(path, "w", driver="PNG", width=rgb.shape[2], height=rgb.shape[1], count=3,
                       dtype="uint8") as dst:
        dst.write(rgb)


def diverging(a, lim):
    t = np.clip((a + lim) / (2 * lim), 0, 1)
    r = np.where(t < 0.5, 2 * t, 1.0); g = np.where(t < 0.5, 2 * t, 2 - 2 * t); b = np.where(t < 0.5, 1.0, 2 - 2 * t)
    rgb = (np.stack([r, g, b]) * 255).astype("uint8")
    rgb[:, ~np.isfinite(a)] = 128
    return rgb


# =============================================================== Part A: sigma0
def _floats(el):
    return np.array([float(x) for x in el.text.split()])


def _interp2(lines, pix_lists, vals, rows, cols):
    per_vec = np.stack([np.interp(cols, p, v) for p, v in zip(pix_lists, vals)])
    out = np.empty((rows.size, cols.size))
    for j in range(cols.size):
        out[:, j] = np.interp(rows, lines, per_vec[:, j])
    return out


def calib_lut(xml: bytes, rows, cols):
    root = ET.fromstring(xml)
    vecs = root.findall(".//calibrationVector")
    lines = np.array([int(v.find("line").text) for v in vecs])
    return _interp2(lines, [_floats(v.find("pixel")) for v in vecs],
                    [_floats(v.find("sigmaNought")) for v in vecs], rows, cols)


def noise_lut(xml: bytes, rows, cols):
    root = ET.fromstring(xml)
    rv = root.findall(".//noiseRangeVector") or root.findall(".//noiseVector")
    if not rv:
        raise ValueError("no noise range vectors")
    key = "noiseRangeLut" if rv[0].find("noiseRangeLut") is not None else "noiseLut"
    lines = np.array([int(v.find("line").text) for v in rv])
    rng = _interp2(lines, [_floats(v.find("pixel")) for v in rv], [_floats(v.find(key)) for v in rv], rows, cols)
    az = np.ones_like(rng)
    for blk in root.findall(".//noiseAzimuthVector"):
        fal, lal = int(blk.find("firstAzimuthLine").text), int(blk.find("lastAzimuthLine").text)
        frs, lrs = int(blk.find("firstRangeSample").text), int(blk.find("lastRangeSample").text)
        bl, lut = _floats(blk.find("line")), _floats(blk.find("noiseAzimuthLut"))
        rm, cm = (rows >= fal) & (rows <= lal), (cols >= frs) & (cols <= lrs)
        if rm.any() and cm.any():
            vals = np.interp(rows, bl, lut) if bl.size > 1 else np.full(rows.size, lut[0])
            az[np.ix_(rm, cm)] = vals[rm][:, None]
    return rng * az, bool(root.findall(".//noiseAzimuthVector"))


def asset_key(item, word):
    keys = [k for k in item.assets if word in k and "vv" in k.lower()]
    if not keys:
        raise KeyError(f"no {word} vv asset in {sorted(item.assets)}")
    return keys[0]


def s1_passes(client, dt):
    items = list(client.search(collections=["sentinel-1-grd"], bbox=AOI_C, datetime=dt).items())
    by = defaultdict(list)
    for it in items:
        if (it.properties.get("sat:orbit_state"), it.properties.get("sat:relative_orbit")) == ("ascending", 130):
            by[it.datetime.date().isoformat()].append(it)
    passes = [by[d] for d in sorted(by)]
    if len(passes) > 7:
        passes = [passes[i] for i in np.unique(np.linspace(0, len(passes) - 1, 7).round().astype(int))]
    return passes


def part_a(sites):
    pc = Client.open(PC_URL)
    per_site = {k: defaultdict(list) for k in sites}
    noise_share = {k: defaultdict(list) for k in sites}
    meta = defaultdict(list)
    for wname, dt in WINDOWS.items():
        with Step(f"sigma0_{wname}"):
            for slices in s1_passes(pc, dt):
                b0 = net()
                rec = {"date": slices[0].datetime.date().isoformat(), "sites": {}}
                for it in slices:
                    todo = [k for k, s in sites.items() if shape(it.geometry).contains(Point(s["lon"], s["lat"]))
                            and k not in rec["sites"]]
                    if not todo:
                        continue
                    signed = planetary_computer.sign(it)
                    cal_xml = requests.get(signed.assets[asset_key(it, "calibration")].href, timeout=120).content
                    noi_xml = requests.get(signed.assets[asset_key(it, "noise")].href, timeout=120).content
                    with rasterio.open(signed.assets["vv"].href) as src:
                        gcps, _ = src.gcps
                        for k in todo:
                            r, c = rowcol(gcps, [sites[k]["lon"]], [sites[k]["lat"]])
                            r, c = int(r[0]), int(c[0])
                            if not (HALF <= r < src.height - HALF and HALF <= c < src.width - HALF):
                                continue
                            dn = src.read(1, window=Window(c - HALF, r - HALF, 2 * HALF, 2 * HALF)).astype("float64")
                            rows = np.arange(r - HALF, r + HALF, dtype=float)
                            cols = np.arange(c - HALF, c + HALF, dtype=float)
                            a = calib_lut(cal_xml, rows, cols)
                            eta, has_az = noise_lut(noi_xml, rows, cols)
                            p = dn ** 2
                            s0 = np.where((dn > 0) & (p > eta), (p - eta) / a ** 2, np.nan)
                            per_site[k][wname].append(s0)
                            noise_share[k][wname].append(float(np.nanmedian(np.where(dn > 0, eta / p, np.nan))))
                            rec["sites"][k] = {"row": r, "col": c, "item": it.id, "azimuth_noise": has_az,
                                               "neg_after_noise_frac": round(float(np.mean((dn > 0) & (p <= eta))), 4),
                                               "median_sigma0_db": round(float(10 * np.log10(np.nanmedian(s0))), 2)}
                    guard()
                rec["bytes_upper_bound"] = net() - b0
                meta[wname].append(rec)
                log(f"  sigma0 {wname} {rec['date']} sites={sorted(rec['sites'])}")
    out = {}
    for k in sites:
        mean_db = {w: 10 * np.log10(np.nanmean(np.stack(v), axis=0)) for w, v in per_site[k].items() if v}
        out[k] = {"label": sites[k]["label"], "n_passes": {w: len(v) for w, v in per_site[k].items()},
                  "median_sigma0_db": {w: round(float(np.nanmedian(m)), 2) for w, m in mean_db.items()},
                  "median_noise_share": {w: round(float(np.median(v)), 3) for w, v in noise_share[k].items()},
                  "dsigma0_vv_db": {w: round(float(np.nanmedian(mean_db[w] - mean_db[BASELINE])), 2)
                                    for w in mean_db if w != BASELINE}}
    return out, meta


# =============================================================== Part B: Al Ain
def select_patch():
    grid = make_grid(SEARCH_REGION, 100)
    pc = Client.open(PC_URL, modifier=planetary_computer.sign_inplace)
    wc = np.zeros((grid[2], grid[1]), "uint8")
    for it in pc.search(collections=["esa-worldcover"], bbox=SEARCH_REGION, datetime="2021").items():
        a = warp_read(it.assets["map"].href, grid)
        wc = np.where((wc == 0) & (a > 0), a, wc)
    veg = np.isin(wc, (10, 40)).astype(float)
    cands = []
    for r in range(0, wc.shape[0] - 100, 10):
        for c in range(0, wc.shape[1] - 100, 10):
            if (wc[r:r + 100, c:c + 100] == 0).any():
                continue
            cands.append((veg[r:r + 100, c:c + 100].mean(), r, c))
    cands.sort(reverse=True)
    t = grid[0]
    checked = []
    for score, r, c in cands[:8]:
        x0, y0 = t.c + c * 100, t.f - r * 100
        corners = [to_geo(x0 + dx, y0 - dy) for dx, dy in ((0, 0), (10000, 0), (0, 10000), (10000, 10000), (5000, 5000))]
        codes = []
        for lon, lat in corners:
            j = requests.get("https://nominatim.openstreetmap.org/reverse", timeout=30,
                             params={"format": "json", "lat": lat, "lon": lon, "zoom": 3},
                             headers={"User-Agent": "uae-geo-portfolio-stage04-probe/0.1"}).json()
            codes.append(j.get("address", {}).get("country_code"))
            time.sleep(1.2)
        checked.append({"score": round(score, 4), "corners": corners, "country_codes": codes})
        if all(cc == "ae" for cc in codes):
            lons, lats = [p[0] for p in corners[:4]], [p[1] for p in corners[:4]]
            return {"bbox_utm_origin": [x0, y0], "veg_share_tree_crop": round(score, 4),
                    "bbox_4326_envelope": [min(lons), min(lats), max(lons), max(lats)],
                    "corners_lonlat": corners[:4], "checked": checked}
    raise RuntimeError(f"no UAE-only patch among top candidates: {checked}")


def s2_eligible(client, bbox, dt):
    aoi = box(*bbox)
    by = defaultdict(list)
    for it in client.search(collections=["sentinel-2-c1-l2a"], bbox=bbox, datetime=dt).items():
        if (it.properties.get("eo:cloud_cover") or 100) <= 30:
            by[it.datetime.date().isoformat()].append(it)
    out = []
    for d, its in by.items():
        cov = unary_union([shape(i.geometry) for i in its]).intersection(aoi).area / aoi.area
        if cov >= 0.98:
            out.append({"date": d, "items": its, "coverage": round(cov, 3),
                        "mean_cc": float(np.mean([i.properties["eo:cloud_cover"] for i in its]))})
    return sorted(out, key=lambda x: x["mean_cc"])


def s2_ndvi(entry, grid):
    f = CACHE / f"alain_{entry['date']}.npz"
    if f.exists():
        z = np.load(f)
        return z["ndvi"], json.loads(str(z["meta"]))
    b0, t0 = net(), time.time()
    t, w, h = grid
    red = np.zeros((h, w), "uint16"); nir = np.zeros_like(red); scl = np.zeros((h, w), "uint8")
    its = sorted(entry["items"], key=lambda i: "MGRS-40" not in str(i.properties.get("grid:code")))
    ef = its[0].assets["red"].extra_fields
    rb = (ef.get("raster:bands") or ef.get("bands") or [{}])[0]
    scale, offset = rb.get("scale", rb.get("raster:scale")), rb.get("offset", rb.get("raster:offset"))
    if scale is None or offset is None:
        raise ValueError(f"no scale/offset on {its[0].id}")
    for it in its:
        need = scl == 0
        if not need.any():
            break
        s, r, n = (warp_read(it.assets[k].href, grid) for k in ("scl", "red", "nir"))
        fill = need & (s > 0) & (r > 0)
        scl[fill], red[fill], nir[fill] = s[fill], r[fill], n[fill]
        guard()
    rr, nn = red * scale + offset, nir * scale + offset
    valid = (scl > 0) & ~np.isin(scl, list(SCL_MASK | {WATER})) & (rr > 0) & (nn > 0)
    ndvi = np.where(valid, (nn - rr) / (nn + rr), np.nan).astype("float32")
    meta = {"items": [i.id for i in its], "valid_fraction": round(float(valid.mean()), 4),
            "water_share": round(float((scl == WATER).mean()), 4), "bytes_upper_bound": net() - b0,
            "seconds": round(time.time() - t0, 1)}
    np.savez_compressed(f, ndvi=ndvi, meta=json.dumps(meta))
    return ndvi, meta


def persistent_change(d1, d2, thr=0.10):
    both = np.isfinite(d1) & np.isfinite(d2)
    return both & (((d1 >= thr) & (d2 >= thr)) | ((d1 <= -thr) & (d2 <= -thr))), both


def top_block(mask):
    best = (-1, 0, 0)
    for r in range(0, mask.shape[0] - 100 + 1, 50):
        for c in range(0, mask.shape[1] - 100 + 1, 50):
            n = int(mask[r:r + 100, c:c + 100].sum())
            if n > best[0]:
                best = (n, r, c)
    return best


def part_b():
    with Step("alain_patch_selection"):
        patch = select_patch()
    x0, y0 = patch["bbox_utm_origin"]
    grid = (Affine(10, 0, x0, 0, -10, y0), 1000, 1000)
    env = patch["bbox_4326_envelope"]
    es = Client.open(ES_URL)
    pcs = Client.open(PC_URL, modifier=planetary_computer.sign_inplace)
    wc = np.zeros((1000, 1000), "uint8")
    for it in pcs.search(collections=["esa-worldcover"], bbox=env, datetime="2021").items():
        a = warp_read(it.assets["map"].href, grid)
        wc = np.where((wc == 0) & (a > 0), a, wc)
    land = (wc != 80) & (wc > 0)
    # desert control C4: same rule as C3 (bare>=0.99, farthest from blocks with built>=0.05)
    blocks = [(r, c, (wc[r:r + 100, c:c + 100] == 60).mean(), (wc[r:r + 100, c:c + 100] == 50).mean())
              for r in range(0, 1000, 100) for c in range(0, 1000, 100)]
    built = np.array([(r, c) for r, c, _, bu in blocks if bu >= 0.05] or [(-10000, -10000)])
    bare = [(r, c) for r, c, ba, _ in blocks if ba >= 0.99]
    c4 = max(bare, key=lambda rc: np.min(np.hypot(built[:, 0] - rc[0], built[:, 1] - rc[1]))) if bare else None
    patch["c4_block_rc"] = c4
    patch["worldcover_fractions"] = {int(k): round(float(v) / wc.size, 4) for k, v in
                                     zip(*np.unique(wc, return_counts=True))}
    RESULTS["alain_patch"] = patch
    save()
    comps, cov, metas, first = {}, {}, {}, {}
    for wname, dt in WINDOWS.items():
        with Step(f"alain_s2_{wname}"):
            sel = s2_eligible(es, env, dt)
            first[wname] = sel[0]
            stack, ms = [], []
            for e in sel[:6]:
                nd, m = s2_ndvi(e, grid)
                m.update(date=e["date"], mean_cc=e["mean_cc"])
                stack.append(nd); ms.append(m)
                log(f"  alain {wname} {e['date']} valid={m['valid_fraction']}")
            stack = np.stack(stack)
            cnt = np.isfinite(stack).sum(0)
            comps[wname] = np.nanmedian(stack, axis=0)
            cov[wname] = {"eligible_dates": len(sel), "land_ge1": round(float((cnt[land] >= 1).mean()), 4),
                          "land_ge3": round(float((cnt[land] >= 3).mean()), 4)}
            metas[wname] = ms
    d = {w: comps[w] - comps[BASELINE] for w in WINDOWS if w != BASELINE}
    w1, w2 = list(d)
    pers, both = persistent_change(d[w1], d[w2])
    n, r, c = top_block(pers)
    res = {"coverage": cov, "s2_dates": metas,
           "persistent_change_km2": round(float(pers.sum()) * 100 / 1e6, 3),
           "persistent_gain_km2": round(float((pers & (d[w1] > 0)).sum()) * 100 / 1e6, 3),
           "persistent_loss_km2": round(float((pers & (d[w1] < 0)).sum()) * 100 / 1e6, 3),
           "valid_both_km2": round(float(both.sum()) * 100 / 1e6, 2),
           "top_block": {"pixels": n, "row": r, "col": c,
                         "lonlat_center": to_geo(x0 + (c + 50) * 10, y0 - (r + 50) * 10),
                         "median_dndvi": {w: round(float(np.nanmedian(d[w][r:r + 100, c:c + 100])), 3) for w in d}}}
    if c4:
        cr, cc = c4
        res["c4"] = {"lonlat_center": to_geo(x0 + (cc + 50) * 10, y0 - (cr + 50) * 10),
                     "median_dndvi": {w: round(float(np.nanmedian(d[w][cr:cr + 100, cc:cc + 100])), 4) for w in d}}
    write_png(QL / "alain_dndvi_persistent.png", diverging(np.where(pers, d[w2], np.nan)[::2, ::2], 0.4))
    for w in d:
        write_png(QL / f"alain_dndvi_{w.replace('/', '_')}.png", diverging(d[w][::2, ::2], 0.4))
    tb = Affine(10, 0, x0 + (c - 100) * 10, 0, -10, y0 - (r - 100) * 10)
    for w in WINDOWS:
        its = sorted(first[w]["items"], key=lambda i: "MGRS-40" not in str(i.properties.get("grid:code")))
        rgb = warp_read(its[0].assets["visual"].href, (tb, 300, 300))
        write_png(QL / f"alain_top_{w.replace('/', '_')}_rgb.png", rgb.astype("uint8"))
    rs, cs = slice(max(r - 100, 0), r + 200), slice(max(c - 100, 0), c + 200)
    write_png(QL / f"alain_top_dndvi_{w2.replace('/', '_')}.png", diverging(d[w2][rs, cs], 0.4))
    return res


def part_b_c_info():
    """Info only: G5b' calculation on AOI (c) from pilot-1 composites, WorldCover water masked (approximation)."""
    comps = {}
    for w in WINDOWS:
        with rasterio.open(P1 / f"ndvi_median_{w.replace('/', '_')}.tif") as src:
            comps[w] = src.read(1)
            grid = (src.transform, src.width, src.height)
    pc = Client.open(PC_URL, modifier=planetary_computer.sign_inplace)
    wc = np.zeros((grid[2], grid[1]), "uint8")
    for it in pc.search(collections=["esa-worldcover"], bbox=AOI_C, datetime="2021").items():
        a = warp_read(it.assets["map"].href, grid)
        wc = np.where((wc == 0) & (a > 0), a, wc)
    d = [np.where(wc != 80, comps[w] - comps[BASELINE], np.nan) for w in WINDOWS if w != BASELINE]
    pers, _ = persistent_change(*d)
    n, r, c = top_block(pers)
    return {"persistent_change_km2": round(float(pers.sum()) * 100 / 1e6, 3), "top_block_pixels": n,
            "top_block_lonlat": to_geo(grid[0].c + (c + 50) * 10, grid[0].f - (r + 50) * 10),
            "note": "WorldCover water mask, not SCL 6 (pilot-1 cache lacks SCL)"}


def main():
    MON.start()
    RESULTS.update(started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    sites = {k: v for k, v in json.loads((P1 / "sites_registered.json").read_text()).items() if k in ("U1", "C1", "C2", "C3")}
    RESULTS["part_a_sites"] = sites
    RESULTS["part_a"], RESULTS["part_a_passes"] = part_a(sites)
    save()
    RESULTS["part_b"] = part_b()
    save()
    with Step("c_info"):
        RESULTS["part_b_c_info"] = part_b_c_info()
    MON.running = False
    RESULTS.update(steps=STEPS, total_seconds=round(time.time() - T0, 1), bytes_upper_bound_run=net(),
                   bytes_cumulative_pilot=PRIOR_PILOT_BYTES + net(), peak_rss_bytes=MON.peak,
                   disk_bytes_pilot2=sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()),
                   finished_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    save()
    log("done")


if __name__ == "__main__":
    main()
