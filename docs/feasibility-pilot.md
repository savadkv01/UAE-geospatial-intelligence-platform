# Feasibility Pilot — AOI, Period and Go/No-go

- Stage: 04 — AOI and feasibility pilot
- Date: 2026-11-24 (all probes and pilots ran 2026-11-24, local time UTC+4)
- Status: outcome **go with recorded waiver**; accepted by the user on 2026-11-24
- Decisions: [ADR 0012](decisions/0012-laptop-constraints-and-data-budgets.md) (constraints and budgets), [ADR 0013](decisions/0013-pilot-aoi.md) (AOI), [ADR 0014](decisions/0014-observation-period-and-window.md) (period), [ADR 0015](decisions/0015-feasibility-pilot-gates-and-outcome.md) (gates and outcome)
- AOI file: [config/aoi/abu-dhabi-pilot-v1.geojson](../config/aoi/abu-dhabi-pilot-v1.geojson)
- Evidence tools: [stage04_aoi_compare.py](../tools/probes/stage04_aoi_compare.py), [stage04_pilot.py](../tools/probes/stage04_pilot.py), [stage04_pilot2.py](../tools/probes/stage04_pilot2.py)

Every value is labelled **verified** (source + access date), **measured** (command + environment), **estimate** (formula + measured inputs), **assumption** or **proposed target**. Byte counts are system-wide `psutil` `bytes_recv` deltas, so they are **upper bounds** on the scripts' own traffic. Visual checks are **same-source review of Sentinel-2 true-colour imagery, not ground truth**.

## 1. Constraints

| Item | Value | Label |
| --- | --- | --- |
| CPU | Intel i7-10610U, 4 cores / 8 threads | measured (`Get-CimInstance`, 2026-11-24) |
| RAM | 31.8 GB | measured |
| Free disk | 467 GB on `C:` | measured (`Get-PSDrive`) |
| OS / WSL2 | Windows 11; WSL2 default; Ubuntu-24.04 running, Ubuntu-22.04 stopped | measured (`wsl --status`, `wsl -l -v`) |
| Docker | Docker Desktop 29.9.3; VM sees 15.5 GB and 8 CPUs; no `.wslconfig` (WSL default 50 % RAM) | measured (`docker info`) |
| Network | No data cap; ≈ 10 MB/s typical (9.7 MB/s measured in Stage 03) | user-confirmed; measured |
| Time | < 5 hours per week | user-stated |
| Budget | Pilot ≤ 2 GB download (raised to 2.6 GB cumulative for pilot 2); full scope ≤ 50 GB download, ≤ 100 GB disk; single job ≤ 60 min | user-approved ([ADR 0012](decisions/0012-laptop-constraints-and-data-budgets.md)) |

## 2. Candidates

### 2.1 Candidate AOIs (comparison probe, measured)

Command: `.scratch/stage03/venv/Scripts/python .scratch/stage04/compare.py` (copy: [stage04_aoi_compare.py](../tools/probes/stage04_aoi_compare.py)). It ran for 312 s and transferred 6.9 MB, using catalogue searches with the STAC `fields` extension plus WorldCover 2021 windowed reads. Areas are geodesic (pyproj `Geod`, WGS84).

| | (a) Coastal islands | (b) Al Ain inland | (c) Mainland growth corridor |
| --- | --- | --- | --- |
| Box (EPSG:4326) | 54.30–54.65 E, 24.40–24.60 N | 55.60–55.85 E, 24.05–24.30 N | 54.55–54.80 E, 24.25–24.45 N |
| Area | 786 km² | 703 km² | 562 km² |
| WorldCover 2021 water / built / bare | 50.4 % / 15.2 % / 25.0 % | 0.1 % / 24.7 % / 63.5 % | 0.7 % / 25.5 % / 71.6 % |
| Tree + cropland + shrub | 4.0 % (+ 4.2 % mangrove) | 11.6 % | 1.8 % |
| S2 MGRS tiles | 39RZH, 40RBN (each covers the box) | 40QCM (covers the box) | 39QZG, 40QBM, 39RZH, 40RBN (31–48 % each) |
| S2 Dec–Feb items ≤ 30 % cloud, 2019/20–2025/26 | 44–60 per winter | 13–17 | 88–125 |
| S1 tracks covering ≥ 99 % | asc 130, desc 166 | asc 130 | asc 130 |
| Documented change | Island developments (geocoded only) | Not documented | **Riyadh City**: ≈ 8,000 ha, infrastructure works from 28 Apr 2019, final phases due Q4 2024 (verified: Abu Dhabi Housing Authority news, 2024-08-20; Argaam, 2022-08-03; accessed 2026-11-24) |
| Main drawback | Half sea; tide and high-rise layover | Crosses into Oman (Buraimi); SAR layover on Jebel Hafeet | Little vegetation; four-tile junction |

Place locations came from OpenStreetMap Nominatim (verified 2026-11-24). Riyadh City is at 24.32–24.39 N, 54.72–54.80 E, and Mohamed Bin Zayed City at 24.29–24.39 N, 54.52–54.60 E.

### 2.2 Earth Search Collection-1 coverage gaps (measured; resolves a Stage 03 open item)

- **2022:** no `sentinel-2-c1-l2a` items in Jan–Feb or Apr–Nov 2022, and only a few in Mar. Dec 2022 is complete. CDSE has every month (44–52 items per month for (c)).
- **Winter 2018/19:** thin (for (c), 4 items in Dec 2018, 8 in Jan 2019, 0 in Feb 2019).
- **Dec 2021** is present (44 items for (c), 30 of them ≤ 30 % cloud).

### 2.3 Candidate periods (estimates at selection time)

| Period | Windows | Estimate | Note |
| --- | --- | --- | --- |
| **P1** Dec–Feb anniversary, 2019/20–2025/26, with 2021/22 = Dec 2021 only | Baseline + 6 | ≈ 10–14 GB (superseded by §6) | Selected |
| P1b As P1, Jan–Feb 2022 filled from CDSE JP2 | Baseline + 6 | + ≈ 3–15 GB | Not selected |
| P2 Dec–Feb 2022/23–2025/26 | Baseline + 3 | ≈ 6–8 GB | Misses the main 2019–2022 build |
| Monthly | — | — | Ruled out: only ≈ 2–3 S1 passes per track per month before 2025 (measured) |

## 3. Chosen AOI and Period

- **AOI** ([ADR 0013](decisions/0013-pilot-aoi.md)): a MultiPolygon of corridor (c) (562 km²) plus an **Al Ain vegetation patch**, an exact 10 × 10 km square on the EPSG:32640 grid (100 km²; envelope 55.612–55.712 E, 24.141–24.232 N). Stored in EPSG:4326. **Processing CRS: EPSG:32640 (UTM 40N), 10 m**. Both parts lie east of 54° E, which resolves the open common-CRS question for this AOI.
  - Geometry check (measured, shapely 2.2.0): MultiPolygon valid and simple; both rings closed, simple and counter-clockwise; parts disjoint; geodesic areas 561.98 and 100.03 km². The Al Ain corners convert back to x = 359,100–369,100 m and y = 2,670,500–2,680,500 m in EPSG:32640.
  - Al Ain patch selection rule (fixed before its results): the 10 km box with the highest WorldCover 2021 tree + cropland share in 55.40–55.74 E, 23.95–24.40 N (score 0.195). All five check points (corners and centre) were reverse-geocoded to `country_code = ae` (Nominatim, 2026-11-24).
- **Period** ([ADR 0014](decisions/0014-observation-period-and-window.md)): **P1**, a Dec–Feb anniversary window per year from baseline 2019/20 to 2025/26. Winter 2021/22 is a **reduced window** (Dec 2021 only, flagged) because of the Earth Search gap.

## 4. Method

All runs used Windows 11 and Python 3.13.14 with rasterio 1.5.2 (GDAL 3.12.2), pystac-client 0.9.1, planetary-computer 1.0.0, shapely 2.2.0, pyproj 3.8.0 and psutil 7.2.2. They used the Stage 03 disposable venv, with no new installs.

**Pilot 1 — corridor (c)** (`.scratch/stage04/pilot.py`)

- **Grid:** EPSG:32640, 10 m, 2,575 × 2,259 px (5,623,062 AOI pixels).
- **Windows:** baseline 2019/20, then 2024/25 and 2025/26 (two consecutive windows test persistence with N = 2).
- **S2 (Earth Search c1):**
  - Dates qualify if their footprints cover ≥ 98 % of the AOI and every item has ≤ 30 % scene cloud. The 6 clearest qualifying dates per window are used.
  - Red, NIR and SCL are read through `WarpedVRT` onto the target grid (nearest neighbour, which also reprojects the 39N tiles).
  - Scale and offset come from item `raster:bands` (0.0001, −0.1).
  - Masks: SCL {0, 1, 3, 8, 9, 10}; reflectance ≤ 0 masked before NDVI.
  - Median NDVI composite per window.
- **S1 (Planetary Computer GRD, asc 130 only):**
  - Up to 7 passes per window, evenly spaced. Slices are mosaicked per pass.
  - Geocoded from GCPs, then averaged as the temporal mean of DN² per window.
  - The Δ proxy is 10·log₁₀(DN²_window / DN²_baseline).
- **Sites, fixed before indicators were computed** (1 km² blocks):

| Site | Role | Location / rule |
| --- | --- | --- |
| U1 | Urban change | Riyadh City, 24.353 N 54.757 E |
| C1 | Urban control | Khalifa City A, 24.424 N 54.569 E |
| C2 | Urban control | MBZ City, 24.340 N 54.565 E |
| C3 | Desert control | Rule: WorldCover bare ≥ 0.99 and the greatest distance to blocks with built ≥ 0.05. Chosen block: 24.260 N 54.791 E |
| V1 | Vegetation | Rule: highest tree + grass + cropland share. Chosen block: 24.266 N 54.614 E |

Exploratory blocks (the largest persistent changes, picked after the results) are reported separately.

**Pilot 2** (`.scratch/stage04/pilot2.py`, approved after pilot 1's no-go)

- **Part A — calibrated σ⁰ at the same sites and passes:**
  - Read 100 × 100 px VV windows in native radar geometry. Site lon/lat is converted to row/column with `rowcol(gcps, …)`.
  - σ⁰ = (DN² − η) / A²σ. A²σ comes from the bilinearly interpolated `schema-calibration-vv` sigmaNought LUT; η is the `schema-noise-vv` range LUT × azimuth LUT.
  - Per-pixel temporal mean, then Δσ⁰ in dB, then the block median.
  - The G4 and G5a thresholds were unchanged.
- **Part B — Al Ain patch:**
  - Same windows and date-selection rule as pilot 1. NDVI additionally **excludes SCL 6 (water)**, as the [measurement spec](measurement-spec.md) requires.
  - Desert control C4 chosen by the C3 rule (block centre 24.227 N 55.637 E).
  - Evaluated with gate G5b′ (§5).

**Defect found and fixed during pilot 1 (measured):** an explicit target grid (`transform`/`width`/`height`) in `WarpedVRT` over a GCP-only S1 GRD returns a **constant array** (e.g. every pixel = 183). The fix nests two VRTs: first geocode to a native 10 m grid (`src_crs = gcps CRS`, `resolution = 10`), then warp that onto the target grid. The corrected values matched the Stage 03 pattern (p50 = 103 versus 103). Run 1 was stopped, its S1 cache deleted, and only the S2 cache reused. Stage 10 must keep this fix or use a proper geocoding method.

## 5. Gates and Outcomes

The user approved the gates as **proposed targets before seeing results**. G5b′ replaced G5b before pilot 2's results existed.

| Gate | Proposed target | Measured value | Outcome |
| --- | --- | --- | --- |
| G1 Coverage | ≥ 1 valid S2 obs on ≥ 95 % of land pixels and ≥ 3 on ≥ 80 %, per window | (c): ≥ 1 on 100 %, ≥ 3 on 99.99–100 %, median 6 obs. Al Ain: 100 % / 100 %. Bias: the 6 clearest dates were chosen. | **Pass** |
| G2 Runtime | Each step ≤ 60 min; peak RSS ≤ 8 GB | Longest step 156.5 s (S2 2019/20, pilot 1 run 1); peak RSS 1.48 GB (pilot 1), 0.31 GB (pilot 2) | **Pass** |
| G3 Volume | Pilot ≤ 2 GB (raised to 2.6 GB for pilot 2); full scope ≤ 50 GB download and ≤ 100 GB disk | Pilot cumulative 2.32 GB (run 1: 567.5 MB, run 2: 1,209.7 MB, diagnostics ≈ 5 MB not instrumented, pilot 2: 533.1 MB). Full scope **≈ 8.0 GB download** and **≈ 11.3 GB disk** (estimate, §6) | **Pass** |
| G4 Control drift | Median \|ΔNDVI\| ≤ 0.05 and median \|Δσ⁰ VV\| ≤ 1.0 dB at the controls in both windows | ΔNDVI: C1 0.014/0.007, C2 0.006/0.000, C3 0.015/0.008, C4 0.027/0.014. Proxy VV: C1 0.21/0.34, C2 0.29/0.29, **C3 1.44/1.19**. **Calibrated σ⁰ VV: C1 0.33/0.60, C2 0.33/0.47, C3 1.68/1.72 dB** | **Fail (C3)**, waived |
| G5a Urban | U1 median Δσ⁰ VV ≥ +3 dB in both windows and the quicklook agrees | Proxy +2.84/+3.43; **calibrated +2.95/+3.92 dB**. Quicklook: sparse plots in 2019/20, dense build-out in 2025/26 | **Fail (by 0.05 dB)**, waived |
| G5b Vegetation (pilot 1) | ≥ 1 site with persistent \|ΔNDVI\| ≥ 0.10 and quicklook agrees | V1 0.000/0.003; no pre-registered site qualified | Fail; replaced by G5b′ |
| G5b′ Vegetation (pilot 2) | ≥ 1.0 km² of valid, non-water pixels with same-sign \|ΔNDVI\| ≥ 0.10 in both windows; top block visually confirmed; C4 \|ΔNDVI\| ≤ 0.05 | Al Ain: **10.0 km²** (gain 3.2, loss 6.8). Top block (24.172 N 55.623 E, 3,753 px) shows a dark-green field turning bare. C4 0.027/0.014 | **Pass** |

Window columns are 2024/25 / 2025/26 versus baseline 2019/20.

**Outcome:** under the approved rules the result is **no-go** (G4 and G5a failed). The user selected **go with an explicit, recorded waiver** of G4 (C3) and G5a. This is not an unqualified go; see [ADR 0015](decisions/0015-feasibility-pilot-gates-and-outcome.md).

**Evidence behind the waiver:**

- **C3 drift is probably real surface change, not noise.** After thermal-noise removal the drift stayed at 1.7 dB. The noise share of measured power fell from 0.405 to 0.29–0.30 while σ⁰ rose from −21.8 to −19.7/−20.0 dB. The quicklook shows graded, rectilinear plots. A WorldCover-"bare" block inside a development corridor is therefore not a stable control (assumption on the cause; the drift itself is measured).
- **The urban signal is interpretable.** The established urban controls stay within 0.6 dB, while U1 rises steadily as the area is built. The exploratory block at 24.339 N 54.681 E rose +9.0/+9.5 dB (proxy). Its quicklooks show bare desert in 2019/20 and a complete residential street grid with houses in 2025/26. That block was chosen after the results, so it is weaker evidence than a pre-registered site.

**Informational findings:**

- **SCL class 2 (dark area) on bare land:** ≤ 0.001 % of bare pixels on every selected date (measured, winter, clearest dates). Masking class 2 makes negligible difference here.
- **Masked SCL share:** ≤ 0.77 % of the AOI on the selected dates.
- **Persistent NDVI change in (c), information only:** 15.4 km², using WorldCover water masking rather than SCL 6. The largest block is the Al Wathba Wetland lagoon (24.257 N 54.594 E). Its quicklooks show a change in water colour, a **water confounder**, not vegetation loss.

## 6. Scaling Estimates (full P1 scope)

**Inputs** (all measured):

| Input | Value |
| --- | --- |
| (c) eligible S2 dates, per P1 window | 10, 15, 3, 9, 10, 13, 16 (total **76**) |
| Al Ain eligible S2 dates, per P1 window | 16, 17, 3, 14, 13, 15, 17 (total **95**) |
| S1 asc-130 passes over (c), per P1 window | 7, 7, 2, 7, 7, 7, 15 (total **52**) |
| (c) S2 bytes per date | mean **53.1 MB** (30.9–102.0; ≈ 31 MB when 1–2 tiles cover the AOI, ≈ 96–102 MB when all 4 tiles are needed) |
| Al Ain S2 bytes per date | mean **20.5 MB** |
| S1 bytes per pass, full (c) VV+VH | mean **36.3 MB** (28.6–51.7) |
| Calibration + noise XML per polarisation | ≈ 1.44 MB (1,014,835 + 426,265 B for one product) |
| Per-date silver arrays | (c) NDVI 23.3 MB; (c) S1 13.7 MB; Al Ain 3.6 MB |
| (c) composites | 57.1 MB per window |

**Download (estimate):**

```text
D = 76 × 53.1 MB + 52 × 36.3 MB + 95 × 20.5 MB + 52 × 2 × 1.44 MB
  = 4,036 + 1,888 + 1,948 + 150 MB ≈ 8.0 GB      (budget 50 GB)
Capped at 6 S2 dates and 7 S1 passes per window:
  39 × 53.1 + 44 × 36.3 + 39 × 20.5 + 44 × 2 × 1.44 MB ≈ 2,071 + 1,597 + 800 + 127 MB ≈ 4.6 GB
```

**Disk (estimate):** bronze (≈ download) + per-date silver arrays + composites.

```text
Disk ≈ 8.0 GB + 76 × 23.3 MB + 52 × 13.7 MB + 95 × 3.6 MB + 7 × (57.1 + ≈ 8) MB
     ≈ 8.0 + 1.77 + 0.71 + 0.34 + 0.46 ≈ 11.3 GB        (budget 100 GB)
```

**Runtime (estimate):** the 18 + 18 S2 dates and 21 S1 passes took about 21.7 s per (c) date, 6–12 s per Al Ain date and 10–11 s per full-AOI S1 pass. The full P1 scope is ≈ 76 × 21.7 + 95 × 7 + 52 × 11 s ≈ **48 min** of sequential I/O. That fits the 60-minute single-job budget only if it is split per window, about 7 min per window.

Exclusions: Docker images, Spark/Airflow overheads, gold products and STAC metadata are not included (Stages 05, 08 and 18).

## 7. Risks and Hand-offs

| # | Risk / finding | Impact | Owner |
| --- | --- | --- | --- |
| R1 | Desert σ⁰ drift ≈ 1.7 dB at a rule-chosen "stable" control (G4 waived) | Change thresholds must clear the measured drift. Controls must avoid graded or disturbed land; consider multiple controls and per-window drift correction | Stage 12 (thresholds), Stage 14 (control monitoring) |
| R2 | U1 passed +3 dB in only one of two windows (G5a waived) | Persistence N and the dB threshold interact; a strict "N = 2 at +3 dB" rule can miss slow build-out | Stage 12 |
| R3 | Earth Search c1 gap (Jan–Nov 2022) makes 2021/22 a reduced, Dec-only window with only **3** eligible dates in each AOI part | Thin observation counts; persistence chains through 2021/22 carry lower confidence | Stages 09, 12 (confidence classes, [ADR 0007](decisions/0007-uncertainty-communication.md)) |
| R4 | Annual anniversary windows with N = 2–3 mean **2–3 years of detection latency** | Affects freshness (AC-03) and the analyst narrative | Stages 12, 13 |
| R5 | Corridor (c) sits on a four-tile, two-zone MGRS junction | Per-date mosaicking and reprojection of the 39N tiles; up to 102 MB per date | Stages 09, 10 |
| R6 | `WarpedVRT` with an explicit grid over a GCP-only S1 source returns a constant array | Silent corruption if repeated | Stage 10 |
| R7 | GCP polynomial geocoding only; no DEM or orbit terrain correction | Positional error not measured; acceptable over flat terrain for 1 km site medians, not validated per pixel | Stage 10 |
| R8 | S1C replaces S1A for part of 2025/26 | Cross-sensor calibration effect not isolated; the controls stayed within 0.6 dB | Stages 10, 14 |
| R9 | Planetary Computer catalogue shows asc 28 / desc 166 over (c) only from 2023/24, unlike over (a) | Catalogue footprint anomaly; not needed (asc 130 suffices) | Stage 09 |
| R10 | Water confounders (Al Wathba lagoon colour) in NDVI | Apply SCL 6 water exclusion consistently | Stages 10, 12 |
| R11 | G1 coverage measured on the 6 clearest dates only | Coverage with all eligible dates and the Dec-only window not measured | Stages 10, 14 |
| R12 | The visual review used saturated 10 m true colour | Bright sand saturates; small structures are not resolvable; not ground truth | Stage 12 (reference evidence) |
| R13 | Time budget under 5 h/week | Favours small increments and per-window jobs | All |

## 8. Requirements Traceability Updates

- BR-02 / BR-05: both MVP capabilities have feasibility evidence. Urban: (c) G5a waived at a 0.05 dB margin. Vegetation: Al Ain G5b′ passed.
- BR-03: window set to Dec–Feb anniversary (P1). The freshness deadline is still deferred (AC-03), with a latency note (R4).
- AC-04 / AC-05: pilot coverage and control-drift evidence recorded. Thresholds stay with Stage 12.

Detailed status changes are in the [requirements](requirements.md) traceability table.
