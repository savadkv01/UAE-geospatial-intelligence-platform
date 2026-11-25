# 0013. Pilot AOI

- Status: accepted
- Date: 2026-11-24
- Stage: 04-aoi-and-feasibility-pilot
- Affected stages: 05, 06, 09, 10, 11, 12, 14, 15, 18, 19, 20

## Question

Which bounded area of interest should the platform monitor? The AOI determines which change can be shown, the data volume, the tiling and CRS complexity, and the confounders.

## Options considered

1. **(a) Coastal islands** (786 km²): the most varied change, but half sea, with tide and high-rise layover; vegetation is weak and tide-confounded.
2. **(b) Al Ain inland** (703 km², clipped to the UAE): the strongest vegetation; crosses into Oman, has SAR layover on Jebel Hafeet, and its urban change is undocumented.
3. **(c) Mainland growth corridor** (562 km², recommended): mostly land, with the best-documented urban change (Riyadh City); little vegetation and a four-tile MGRS junction.
4. Custom polygon, e.g. (c) plus a small Al Ain patch.

After pilot 1 failed the vegetation gate, the user was offered three choices: keep (c) and record vegetation as weak; add an Al Ain farm/oasis patch and re-pilot; or defer vegetation from the MVP.

## User selection

AOI preference: "(c) Mainland corridor alone, 562 km² (recommended)". After pilot 1, for vegetation: "Add an Al Ain farm/oasis patch and re-pilot vegetation (budget increase to ~2.6 GB)". The user then approved the pilot 2 plan, including the patch-selection rule, and chose "go with waiver" ([ADR 0015](0015-feasibility-pilot-gates-and-outcome.md)).

**Final AOI:** [config/aoi/abu-dhabi-pilot-v1.geojson](../../config/aoi/abu-dhabi-pilot-v1.geojson), a MultiPolygon in EPSG:4326 with two parts:

1. **Mainland corridor:** 54.55–54.80 E, 24.25–24.45 N (561.98 km²).
2. **Al Ain vegetation patch:** an exact 10 × 10 km square on the EPSG:32640 grid, x = 359,100–369,100 m and y = 2,670,500–2,680,500 m (100.03 km²).

**Processing CRS:** EPSG:32640 (WGS 84 / UTM 40N), 10 m grid.

## Rationale

The corridor contains a documented, large construction programme with a pre-construction-era baseline, established urban controls, and mostly land pixels. The Al Ain patch supplies interpretable, field-level vegetation change that the corridor lacks. Both parts lie east of 54° E, so a single UTM 40N grid serves the whole AOI.

## Evidence

- **Measured:** the comparison probe (WorldCover 2021 class shares, Earth Search item counts, S1 track coverage) and pilot gates ([feasibility pilot](../feasibility-pilot.md) §2, §5).
- **Verified (accessed 2026-11-24):** Riyadh City is ≈ 8,000 ha with infrastructure works from 28 Apr 2019 (Argaam, 2022-08-03), and its final phases were due in Q4 2024 (Abu Dhabi Housing Authority, 2024-08-20). Place locations come from OpenStreetMap Nominatim.
- **Measured:** the Al Ain patch was selected by a fixed rule (highest WorldCover tree + cropland share, 0.195, in 55.40–55.74 E, 23.95–24.40 N). All five check points reverse-geocoded to `ae`.
- **Measured (shapely 2.2.0):** the geometry is valid and simple; both rings are closed and counter-clockwise; the parts are disjoint.

## Consequences

- Stages 09–11 handle two AOI parts. The corridor needs a per-date mosaic of tiles 39QZG, 39RZH, 40QBM and 40RBN, with the 39N tiles reprojected. The Al Ain part uses tile 40QCM only.
- S1 uses relative orbit 130 (ascending), which covers both parts fully.
- Products report coverage and statistics per part as well as per AOI.
- The OSM-derived geocoding is used only for site descriptions; nothing OSM-derived is redistributed.
- Changing the AOI requires a new versioned file (`-v2`) and a superseding ADR.
