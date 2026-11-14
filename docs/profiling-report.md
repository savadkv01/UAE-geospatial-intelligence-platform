# Source Profiling Report

- Stage: 03 — Source discovery and profiling
- Date: 2026-11-14 (probe run 18:28–18:39 UTC)
- Status: measured; approved by the user on 2026-11-14
- Companion: [Source register](source-register.md)

This report records what the Stage 03 probe **actually executed and measured**. Every number below comes from a command listed in §2 and run in the environment in §1. The probe was bounded, read-only and disposable, and stayed within the user-approved budget. It does not select an AOI (Stage 04), build ingestion code (Stage 09) or validate any analytical threshold.

## 1. Environment (measured, `env` step)

| Item | Value |
| --- | --- |
| OS | Windows 11 (10.0.26300), AMD64, 8 logical CPUs, 34.1 GB RAM |
| Python | 3.13.14 (disposable venv in git-ignored `.scratch/stage03/venv`) |
| Packages | pystac-client 0.9.1, planetary-computer 1.0.0, rasterio 1.5.2 (GDAL 3.12.2), pyproj 3.8.0 (PROJ 9.8.1), shapely 2.2.0, boto3 1.44.3, requests 2.34.2, psutil 7.2.2, python-dotenv 1.2.4 |
| Network | Residential connection; no cloud compute |
| Probe test box | lon 54.30–54.50, lat 24.38–24.52 (EPSG:4326), ≈ 20 × 15 km around Abu Dhabi island. **Not the AOI.** |
| Credentials | CDSE S3 keys read from an untracked, git-ignored `.env` (variable names only; values never printed or logged) |

## 2. Commands Executed

All commands ran from the repository root. The probe ran as `.scratch/stage03/probe.py`. A copy for reruns is kept at [tools/probes/stage03_source_probe.py](../tools/probes/stage03_source_probe.py), with identical step logic. It writes to `.scratch/stage03/` and folds the command-4 follow-up checks into a `followup` step.

| # | Command | Started (UTC) | Elapsed | Purpose |
| --- | --- | --- | --- | --- |
| 1 | `.scratch\stage03\venv\Scripts\python.exe .scratch\stage03\probe.py env catalog` | 18:28:48 | 6.7 s + 348.3 s | Environment capture; STAC searches over the test box for each year 2017–2026 |
| 2 | `... probe.py access` | 18:35:01 | 9.8 s | Anonymous / unsigned / signed 1 KB range GETs on one asset per provider and collection |
| 3 | `... probe.py s2 worldcover ghsl osm s1` | 18:35:18 | 29.8 + 4.3 + 5.0 + 28.4 + 14.9 s | Windowed raster reads and context-layer probes |
| 4 | Inline follow-up: anonymous HTTPS range GET on the Earth Search S1 asset; CDSE S1 searches for 2018 and 2019 repeated after a 20 s pause | ≈ 18:37 | ≈ 45 s | Resolve two anomalies from commands 1–2 |
| 5 | `... probe.py cdse` | 18:38:22 | 11.5 s | CDSE S3 download of one S2 band; S1 asset sizes via `HeadObject` |

Searches used `pystac_client.Client.search(collections=[…], bbox=BBOX, datetime=<year>, limit=100)` and paged through all matching items. Windowed reads used `rasterio.open(href)`, `transform_bounds` from EPSG:4326 to the asset CRS and `read(window=…)`. S1 GRD reads used `WarpedVRT(src, src_crs=<GCP CRS>, crs="EPSG:32640", resolution=10)`.

## 3. Transfer Budget (measured)

Approved budget: ≤ 1 GB in total.

| Step | Bytes (upper bound) | How measured |
| --- | --- | --- |
| catalog | 147,246,894 | System-wide `psutil.net_io_counters().bytes_recv` delta |
| access | 394,368 | System-wide delta |
| s2 (6 items × 3 bands) | 46,038,096 | Per-item system-wide deltas (3.8–16.6 MB per item) |
| s1 (4 items × 2 pols) | 46,677,964 | Per-item system-wide deltas (5.7–21.5 MB per item) |
| worldcover | 631,628 | System-wide delta |
| ghsl | 3,197,333 | Exact downloaded file size |
| osm | 8,947,265 | Exact response body sizes (uncompressed) |
| cdse | 76,894,146 | Exact downloaded file size |
| **Total** | **330,027,694 (≈ 0.33 GB)** | Within budget; the script aborts at 1 GB |

System-wide deltas include any concurrent traffic on the machine, so they are **upper bounds**, not exact probe traffic. The follow-up checks in command 4 (one 1 KB range GET plus two catalogue searches) and the pip install were not included in the ledger.

## 4. Catalogue Results (measured, command 1)

### 4.1 Sentinel-2 L2A: items intersecting the test box per year

| Provider / collection | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026* | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PC `sentinel-2-l2a` | 174 | 413 | 427 | 432 | 412 | **613** | **721** | 432 | 519 | 444 | 4,587 |
| Earth Search `sentinel-2-c1-l2a` | **9** | **147** | 339 | 437 | 432 | **36** | 437 | 447 | 519 | 453 | 3,256 |
| CDSE `sentinel-2-l2a` | 192 | 417 | 435 | 443 | 432 | 435 | 438 | 450 | 519 | 450 | 4,211 |

\* 2026 runs to 14 Nov 2026.

| Property | PC | Earth Search c1 | CDSE |
| --- | --- | --- | --- |
| MGRS tiles | 39RZH, 40RBN, 40QBM | same | same, plus **one spurious 01MAV item (EPSG:32701)** |
| `proj:epsg` | 32640 (3,065), 32639 (1,522) | 32640 (2,171), 32639 (1,085) | 32640 (2,806), 32639 (1,404), 32701 (1) |
| Processing baselines | **02.12 (1,635), 03.00 (233), 04.00 (491)**, 05.00–05.13 (2,228) | 05.00–05.13 only | 05.00–05.13 only |
| Platforms | S2A 1,994; S2B 2,207; S2C 386 | S2A 1,308; S2B 1,546; S2C 402 | S2A 1,807; S2B 2,005; S2C 399 |
| `eo:cloud_cover` median (Q1–Q3) | 8.9 % (1.1–28.3) | 5.0 % (0.5–27.0) | 4.6 % (0.5–26.3) |
| Share of items ≤ 10 % / ≤ 30 % cloud | 0.53 / 0.76 | 0.58 / 0.77 | 0.59 / 0.77 |
| Band asset keys (examples) | `B04`, `B08`, `SCL`, `visual` | `red`, `nir`, `scl`, `cloud`, `visual` | `B04_10m`, `B08_10m`, `SCL_20m`, `CLD_20m`, `TCI_10m` |
| Media type | COG | COG | JPEG 2000 in SAFE (`s3://eodata/...`) |

Cloud cover is a whole-tile scene statistic, not a measure for the test box.

### 4.2 Sentinel-1 GRD: items intersecting the test box per year

| Provider / collection | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026* | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PC `sentinel-1-grd` | 123 | 139 | 134 | 140 | 147 | 135 | 133 | 135 | 323 | 263 | 1,672 |
| Earth Search `sentinel-1-grd` | 130 | 149 | 141 | 149 | 154 | 139 | 140 | 150 | 218 | 267 | 1,637 |
| CDSE `sentinel-1-grd` | 130 | 149† | 141† | 149 | 156 | 143 | 140 | 157 | 222 | 265 | 1,652 |

† The first attempt returned HTTP 429 (`{"error":"WAF","message":"Rate limit exceeded"}`). The values come from the retry after a 20 s pause (command 4).

| Property (PC; ES and CDSE match closely) | Value |
| --- | --- |
| Tracks (orbit state / relative orbit) | ascending 28 (343), ascending 130 (638), descending 64 (321), descending 166 (370) |
| Mode / polarisation | IW in all items; VV+VH in 1,667 of 1,672 (VV only 3; HH+HV 2) |
| Platforms | S1A for most years; **S1B only 4 items** in 2017–2021; S1C from 2025 and S1D from 2026 (accounting for the higher 2025–26 counts) |
| Timeliness | Fast-24h in 1,669 items (CDSE does not populate this property) |
| Assets | `vv`, `vh` (COG) plus `schema-calibration-*`, `schema-noise-*`, `schema-product-*` XML and `safe-manifest` (all three providers) |

## 5. Catalogue Access versus Asset Access (measured, commands 2 and 4)

Each test was a 1 KB `Range` GET without credentials, unless noted.

| Provider / asset | Catalogue | Asset request | Result |
| --- | --- | --- | --- |
| PC S2 `B04`, unsigned | anonymous | Azure Blob HTTPS | **409** (XML error) |
| PC S2 `B04`, SAS-signed via `planetary_computer.sign` | anonymous | Azure Blob HTTPS | **206**, 1,024 B |
| PC S1 `vv`, unsigned / signed | anonymous | Azure Blob HTTPS | **409** / **206** |
| ES S2 c1 `red` | anonymous | `https://…` public bucket | **206**, COG |
| ES S1 `vv` | anonymous | href `s3://sentinel-s1-l1c/…`, tested as `https://sentinel-s1-l1c.s3.eu-central-1.amazonaws.com/…` | **206**, COG header, although the collection metadata says `storage:requester_pays: true` |
| CDSE S2 `B04_10m`, alternate HTTPS href | anonymous | `https` alternate | **401** |
| CDSE S1 `vv`, alternate HTTPS href | anonymous | `https` alternate | **401** |
| CDSE S2 `B04_10m` via S3 keys | — | `s3://eodata/…` with boto3 | **Downloaded** (§6.4) |

## 6. Raster Sample Results (measured, commands 3 and 5)

### 6.1 Sentinel-2 L2A windowed reads (PC and Earth Search)

Sampling selected the lowest-cloud item in Jan 2021, Jan 2024 and Jan 2025, chosen to span the PB 04.00 offset change.

| Item | Baseline | CRS / res | dtype / nodata | Declared scale, offset | B04 DN p2 / p50 / p98 | Valid after SCL mask† |
| --- | --- | --- | --- | --- | --- | --- |
| PC `S2B_…20210118…T40QBM` | 02.12 | 32640 / 10 m | uint16 / **None** | **none in STAC**; GDAL 1 / 0 | 152 / 1,050 / 4,840 | 0.981 |
| PC `S2A_…20240108…T40QBM` | 05.10 | 32640 / 10 m | uint16 / 0 | **none in STAC**; GDAL 1 / 0 | 1,103 / 2,512 / 5,832 | 0.935 |
| PC `S2A_…20250112…T40QBM` | 05.11 | 32640 / 10 m | uint16 / 0 | **none in STAC**; GDAL 1 / 0 | 1,079 / 3,088 / 5,760 | 0.967 |
| ES `S2B_T39RZH_20210111` | 05.00 | 32639 / 10 m | uint16 / 0 | 0.0001, −0.1 (STAC and GDAL) | 1,042 / 1,922 / 5,608 | 0.962 |
| ES `S2A_T40QBM_20240108` | 05.10 | 32640 / 10 m | uint16 / 0 | 0.0001, −0.1 | 1,102 / 2,510 / 5,740 | 0.935 |
| ES `S2A_T40QBM_20250112` | 05.11 | 32640 / 10 m | uint16 / 0 | 0.0001, −0.1 | 1,079 / 3,088 / 5,760 | 0.967 |

† Fraction of SCL pixels **not** in {0, 1, 3, 8, 9, 10}, the mask set in the [measurement spec](measurement-spec.md).

- **SCL histograms.** Class 6 (water) covers about 53 % of every window because the test box includes open sea. Class 5 (bare soil) covers about 43 %, and class 4 (vegetation) under 1 %. Class 2 (dark area) appears only in the PB 02.12 scene (689 px).
- **Format.** All windows were deflate-compressed COGs with internal overviews. PC block size is 512 px; ES block size is 1,024 px for 10 m bands and 512 px for SCL. Each band window took 0.4–4.5 s to read.
- **Partial coverage.** For tile 40QBM the window was only 141 rows high, because the test box lies mostly north of that tile. The comparable full-window sample is the 39RZH item.

### 6.2 Sentinel-1 GRD windowed reads (PC)

| Item | Track | Native CRS | GCPs | Full shape | Window (10 m, EPSG:32640) | Non-zero fraction | VV DN p2 / p50 / p98 | Bytes (upper bound) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1A 20251227T142459 | asc 130 | **None** | 210 (EPSG:4326) | 16,728 × 25,822 | 679 × 2,049 | **0.040** | 37 / 69 / 169 | 5.9 MB |
| S1A 20251227T142434 | asc 130 | None | 210 | 16,728 × 25,816 | 1,581 × 2,047 | 0.983 | 44 / 130 / 848 | 21.5 MB |
| S1A 20251230T021538 | desc 166 | None | 189 | 15,608 × 25,726 | 1,581 × 2,048 | 0.860 | 38 / 112 / 872 | 13.5 MB |
| S1C 20251229T022245 | desc 64 | None | 210 | 16,743 × 25,217 | 1,579 × 2,044 | **0.083** | 62 / 122 / 450 | 5.7 MB |

- All rasters were uint16 with nodata 0, stored as zstd-compressed COGs with 1,024 px blocks and overviews 2–64. Each band window took 0.8–2.7 s.
- **Pixel values are uncalibrated digital numbers.** Computing σ⁰ requires the per-scene `schema-calibration-*` lookup tables (LUTs), which are present as assets.
- **One pass can span two slices.** The two S1A scenes on 27 Dec 2025 are consecutive slices of the same pass, and only together do they cover the test box.

### 6.3 Context and reference layers

| Source | Measured result |
| --- | --- |
| ESA WorldCover (PC) | Two items intersect the box: `…_2021_v200_N24E054` (v2.0.0) and `…_2020_v100_N24E054` (v1.0.0). Read 2021: **EPSG:4326**, 8.33 × 10⁻⁵° (≈ 10 m), uint8, nodata 0, window 1,680 × 2,400, 2.0 s. Class fractions: water 80 = 0.449, bare 60 = 0.252, built-up 50 = 0.201, tree 10 = 0.038, mangroves 95 = 0.034, shrub 20 = 0.015, grass 30 = 0.007, cropland 40 = 0.004, herbaceous wetland 90 = 0.001. |
| GHSL GHS-BUILT-S E2020 R2023A, 100 m | Tile `R7_C24`, computed from Mollweide coordinates and confirmed by an HTTP 200 HEAD request. Downloaded 3,197,333 B in 3.3 s; the zip contains the GeoTIFF and a PDF data package. ESRI:54009 Mollweide, 100 m, uint16, nodata 65535. Window 167 × 225; built-up surface per 100 m cell: median 0, p98 4,421 m², max 9,486 m²; 31.8 % of cells > 0. |
| OpenStreetMap via Overpass (`overpass-api.de`) | Buildings query: HTTP 200, 27.4 s, 8,946,731 B; **26,044** building ways and relations; data timestamp `2026-11-14T18:35:01Z`. Tag presence: `building:levels` 13.0 %, `height` 4.6 %, `name` 3.5 %, `addr:street` 0.14 %, **`start_date` 0.01 %**. Last-edit year: 2016 = 5,142, **2023 = 12,465 (48 %)**, other years ≤ 1,289. A second query (landuse / water / park counts) **failed with HTTP 502** and was not retried. |

### 6.4 CDSE (command 5)

| Asset | Result |
| --- | --- |
| S2 L2A `B04_10m`, item `S2B_MSIL2A_20260102…N0511…T39RZH` | `s3://eodata/…/IMG_DATA/R10m/T39RZH_20260102T065159_B04_10m.jp2`, **76,894,146 B**, downloaded in 7.9 s (≈ 9.7 MB/s). Full tile 10,980 × 10,980, EPSG:32639, 10 m, uint16, **nodata unset**, no scale or offset declared in GDAL, JPEG 2000 with 1,024 px blocks and overviews 2–16. Test-box window 1,602 × 2,068: B04 DN p2 / p50 / p98 = 1,152 / 2,324 / 6,532. |
| S1 GRD item `S1A_IW_GRDH_1SDV_20260101T143243…_COG` (catalogue and `HeadObject` only) | `vv` COG **512,870,243 B**; `vh` COG **433,656,307 B**; calibration, noise and product XML files ≈ 0.4–1.8 MB each. **CDSE serves S1 GRD as COGs.** This disproves the earlier assumption that it would be SAFE-only. |

## 7. Anomalies

| # | Anomaly | Evidence | Consequence |
| --- | --- | --- | --- |
| A1 | PC S2 L2A mixes processing baselines 02.12–05.13 and does **not** declare `raster:bands` scale or offset. PB 02.12 files have no nodata value. | §4.1, §6.1 | DN → reflectance conversion must be derived per item from the baseline. Mixing PC items with Collection-1 items risks a −1000 DN offset error ([S2]). |
| A2 | PC S2 has more items in 2022 (613) and 2023 (721) than other years (≈ 430). | §4.1 | Probable duplicate or reprocessed copies (**assumption**). Ingestion must de-duplicate by tile and datatake. |
| A3 | Earth Search `sentinel-2-c1-l2a` is sparse for 2017 (9), 2018 (147) and **2022 (36)**. | §4.1; the AWS Registry states that L2A has been available globally only since December 2018 (§9) | The 2017–2018 sparsity is consistent with ESA's routine L2A production reaching non-European areas only in December 2018. The 2022 gap is unexplained. ES alone cannot supply consistent 2017–2018 or 2022 baselines, and its `sentinel-2-pre-c1-l2a` collection is not radiometrically harmonised. |
| A4 | The Earth Search `sentinel-1-grd` collection says `storage:requester_pays: true`, but an anonymous HTTPS GET returned 206 and the AWS Registry says "No AWS account required". | §5; AWS Registry (§8) | The metadata is out of date. Access is anonymous as of 2026-11-14 but could change; recheck in Stage 09. |
| A5 | CDSE rate-limited rapid sequential searches (HTTP 429, WAF). | §4.2 | Ingestion needs backoff and throttling for CDSE. |
| A6 | CDSE returned one item from MGRS 01MAV (EPSG:32701) for an Abu Dhabi bbox. | §4.1 | Probably a footprint crossing the antimeridian (**assumption**). Results need a spatial post-filter. |
| A7 | S1 GRD has no CRS (GCP georeferencing only), and a single pass can span two slices. | §6.2 | Terrain correction or geocoding and slice assembly are Stage 10 work. |
| A8 | Very few S1B acquisitions (4) over the test box. | §4.2 | Before 2025, the revisit is S1A-only: ≈ 12 days per track, 4 tracks. The cause was not investigated. |
| A9 | PC S1 `platform` values are inconsistently cased (`SENTINEL-1A` / `sentinel-1a`). | §4.2 | Normalise values when ingesting. |
| A10 | The second Overpass query returned HTTP 502. | §6.3 | Overpass is a shared, best-effort service. Prefer an extract file (e.g. Geofabrik) for repeatable ingestion (**proposed**). |
| A11 | 48 % of OSM buildings were last edited in 2023. | §6.3 | Probably a bulk edit or import (**assumption**). OSM edit dates must not be read as construction dates; the [measurement spec](measurement-spec.md) already says so. |
| A12 | WorldCover is delivered in geographic EPSG:4326, not a projected CRS. | §6.3 | It must be reprojected before computing areas or statistics. |

## 8. Limitations

- The test box is about 50 % sea, so it is not representative of the land AOI. Stage 04 re-measures coverage on the chosen AOI.
- Bytes for windowed reads are system-wide upper bounds. Exact per-request accounting was not instrumented.
- Each step used a small sample (6 S2 items, 4 S1 items and 1 CDSE asset). No SCL accuracy check was done, and no S1 calibration was applied.
- CDSE S1 pixels were not read; only sizes were checked. Earth Search S1 was read only as a 1 KB header.
- The DN differences between the PB 02.12 and PB 05.x samples are **consistent with** the documented +1000 offset ([S2]). They are not a controlled test, because the scenes and dates differ.
- Very-high-resolution basemap terms and a free tide-data source were **not** researched in this probe. See the gaps in the [source register](source-register.md).

## 9. Web Sources Used (accessed 2026-11-14)

- Copernicus Sentinel data legal notice (rev. 1): <https://ecds.ecmwf.int/licences/ec-sentinel>. The ESA-hosted copy (`sentinel.esa.int/documents/247904/690755/Sentinel_Data_Legal_Notice`) did not resolve (DNS failure).
- CDSE STAC: <https://documentation.dataspace.copernicus.eu/APIs/STAC.html>; S3: <https://documentation.dataspace.copernicus.eu/APIs/S3.html>; quotas: <https://documentation.dataspace.copernicus.eu/Quotas.html>
- Planetary Computer collection JSON: <https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a>, `…/sentinel-1-grd`, `…/sentinel-1-rtc`, `…/esa-worldcover`, `…/io-lulc-annual-v02`
- Earth Search collections: <https://earth-search.aws.element84.com/v1/collections>, `…/sentinel-1-grd`
- AWS Registry, Sentinel-1: <https://registry.opendata.aws/sentinel-1/>; Sentinel-2 COGs: <https://registry.opendata.aws/sentinel-2-l2a-cogs/>
- GHSL use conditions: <https://human-settlement.emergency.copernicus.eu/GHSLhowToCite.php>; tiles: <https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S_GLOBE_R2023A/>
- OSM copyright: <https://www.openstreetmap.org/copyright>
