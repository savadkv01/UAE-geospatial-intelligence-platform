# Source Guide: Understanding the Data We Use

- Stage: 03 — Source discovery and profiling (learning companion)
- Date: 2026-11-14
- Audience: a data engineer who is new to satellite and geospatial data
- Companions: [Source register](source-register.md) (authoritative facts and licences), [Profiling report](profiling-report.md) (measurements), [Domain glossary](domain-glossary.md) (definitions)

This guide explains **what each data source is, where it comes from, what is inside it, how we access it and why, and how to read it**. It is a learning document. If it ever disagrees with the source register, the register wins.

**Fact labels:**
- **verified:** from official documentation; the source is in §11
- **measured:** from our probe; the command is in the profiling report or §8
- **assumption:** not yet checked
- **candidate:** a storage option that has not been decided

Every code output quoted here was produced on 2026-11-14 by running `.scratch/stage03/guide_examples.py` in the Stage 03 probe environment: Python 3.13.14, rasterio 1.5.2 / GDAL 3.12.2, pystac-client 0.9.1. The run took 26 s and transferred ≈ 20 MB.

---

## Part A — Primer: How Satellite Data Works

### A1. How the satellites collect data

Our two main sources measure the ground in physically different ways. That is why they answer different questions.

| | Sentinel-2 (optical) | Sentinel-1 (radar) |
| --- | --- | --- |
| Sensing principle | **Passive.** The Multi-Spectral Instrument (MSI) records **sunlight reflected** from the surface in 13 spectral bands. | **Active.** A C-band synthetic aperture radar (SAR) **sends microwave pulses** (5.405 GHz, ≈ 5.55 cm wavelength) and records the echo. |
| Works at night or through cloud? | No. It needs daylight, and clouds block it. | Yes, day and night, through cloud. |
| What a pixel "sees" | Colour and spectral reflectance. Chlorophyll absorbs red and leaf structure reflects near-infrared, which is the basis of NDVI. | Surface **roughness, geometry and moisture**, not colour. Walls next to flat ground make a strong "double-bounce" return, so buildings look bright. |
| Orbit | Sun-synchronous, 786 km altitude, 98.62° inclination | Sun-synchronous, 693 km altitude, 98.18° inclination, 98.6 min period |
| Local time of pass | 10:30 local solar time (descending node) | 18:00 at the ascending node, so passes are around dawn (descending) and dusk (ascending) |
| Swath | 290 km | 250 km in Interferometric Wide (IW) mode, our mode |
| Repeat | 10-day cycle per satellite; 5-day revisit at the Equator with two satellites | 12-day cycle per satellite; 6 days with two |
| Satellites | S2A (2015), S2B (2017), S2C (2024). S2C replaced S2A on 21 Jan 2025; S2A has continued in an extension campaign since March 2025. | S1A (2014), S1B (2016; failed 23 Dec 2021), S1C (Dec 2024), S1D (Nov 2025) |
| Label | verified (SentiWiki S2 Mission) | verified (SentiWiki S1 Mission; ESA Instrument page) |

**What we measured over Abu Dhabi:**
- **Sentinel-2:** sensing times of about 06:52–07:13 UTC, which is 10:52–11:13 local time (UTC+4). This is consistent with the 10:30 solar-time orbit.
- **Sentinel-1:** ascending passes at about 14:24 UTC (18:24 local) and descending passes at about 02:15 UTC (06:15 local).

**Why sun-synchronous matters:** the satellite crosses each place at the same local solar time every time. Illumination is therefore comparable between dates, which change detection depends on.

**Why radar needs "same track":** the radar looks **sideways**, always to the right of its flight path. A building seen from an ascending pass is lit from a different side than from a descending pass. Comparing different tracks therefore creates false change. Over our test box we measured four tracks: ascending 28 and 130, descending 64 and 166 (profiling report §4.2). [ADR 0006](decisions/0006-temporal-comparability-policy.md) requires comparisons within one track.

### A2. The processing chain: from raw signal to a usable pixel

```
satellite ──downlink──► Level-0  raw instrument data             (ESA; not distributed for our use)
                          │
                          ▼
                        Level-1  geolocated, calibrated-ready     S2: L1C top-of-atmosphere reflectance
                          │                                       S1: GRD (detected, ground-range) ◄── WE START HERE for S1
                          ▼
                        Level-2  surface/geophysical product      S2: L2A bottom-of-atmosphere reflectance + SCL ◄── WE START HERE for S2
                          │                                       (atmospheric correction by ESA's Sen2Cor processor)
                          ▼
                  ── our pipeline (Stages 09–12) ──
                        calibration (S1 σ⁰), masking, reprojection, compositing, indices, change products
```

- **Sentinel-2 L2A:** ESA has already removed the atmosphere's effect, so pixel values approximate the reflectance of the ground itself. ESA also adds a per-pixel scene classification layer (SCL) of clouds, shadows, water and so on. **We do not do atmospheric correction.**
- **Sentinel-1 GRD (Ground Range Detected):** ESA has already formed the radar image, combined several looks to reduce speckle, and projected it from slant range onto an Earth ellipsoid. Pixel values are still **uncalibrated amplitude numbers**, and the image has no map projection. **We do the calibration to σ⁰ and the geocoding** (Stage 10, [ADR 0010](decisions/0010-sentinel-1-grd-mvp-source-and-level.md)).
- ESA also publishes radar **SLC** (complex, for interferometry) and **Level-2 OCN** (ocean wind and waves). We don't use them.

**Processing baselines:** ESA versions its processing software. The version is the `Nxxyy` in a product name, for example `N0511` means baseline 05.11. Newer baselines change pixel values. "Collection-1" is ESA's reprocessing of the whole archive with a uniform recent baseline, so that all years are comparable. This is why [ADR 0009](decisions/0009-sentinel-2-l2a-mvp-source.md) uses Collection-1 data.

### A3. Where pixels are: grids, tiles and coordinate systems

- **CRS (coordinate reference system):** the rules that turn pixel row and column into a place on Earth. Definitions are in [glossary §2](domain-glossary.md).
- **Sentinel-2 tiles (MGRS):** Sentinel-2 L1C/L2A data is cut into fixed **110 × 110 km tiles** on a UTM grid with a 100 km step, so neighbouring tiles overlap by 10 km. Each tile has a code such as `39RZH`, made of UTM zone 39 + latitude band R + 100 km square ZH (verified, SentiWiki S2 Products).
- **Three tiles cover our test box:** 39RZH (EPSG:32639), and 40RBN and 40QBM (EPSG:32640) (measured). Because tiles overlap and the 39/40 zone boundary is at 54°E, **the same spot near Abu Dhabi island is delivered in two different CRSs**. For example, tile 39RZH extends east of 54°E (measured bounds up to x = 909,780 m in EPSG:32639). Before combining tiles, the pipeline must reproject them to one target CRS (decided in Stage 04/10).
- **Sentinel-1 GRD has no CRS (measured):** it is georeferenced with about 200 **ground control points (GCPs)**, each a pixel → lon/lat/height tie point. Tools can warp the image with these GCPs. Accurate geocoding uses the orbit and a DEM (Stage 10).
- **Other sources use their own CRSs (measured):**
  - WorldCover: EPSG:4326, latitude/longitude in degrees, not metres
  - GHSL: Mollweide (ESRI:54009), an equal-area world projection
  - OSM: EPSG:4326 coordinates
- **Rule:** never compute areas in degrees. Reproject to a projected CRS in metres first.

### A4. What a pixel value means

A raw pixel is a **digital number (DN)**, an integer chosen to store the measurement compactly. Each source has its own conversion into a physical quantity:

| Source | Stored as | Conversion | Physical meaning |
| --- | --- | --- | --- |
| S2 L2A (Collection-1) | uint16 DN, nodata 0 | `reflectance = DN × 0.0001 − 0.1` (scale and offset from the STAC `raster:bands`; measured) | Fraction of sunlight reflected, normally 0–1 |
| S1 GRD | uint16 DN, nodata 0 | `σ⁰ = DN² / A_σ²`, where A_σ comes from the calibration lookup table (LUT) supplied with each scene; then `σ⁰[dB] = 10·log₁₀(σ⁰)` | Radar backscatter per unit area. The formula follows ESA technical note ESA-EOPG-CSCOP-TN-0002, which is cited by the PC collection description; the full text was not retrieved, so Stage 10 should cross-check against GDAL's `SENTINEL1_CALIB` output. |
| WorldCover | uint8 class code | Lookup table (10 = tree cover … 95 = mangroves) | Category, not a measurement |
| GHSL BUILT-S | uint16 | None needed | m² of built-up surface in each 100 m cell (0–10,000) |

**The offset trap (measured).** The −0.1 offset can make very dark pixels, such as water or deep shadow, **slightly negative**. Computing NDVI on such pixels gives impossible values:

```
NAIVE NDVI p2/p50/p98 (no reflectance check): [-3.143  0.042  2.023]   ← outside the valid range [-1, 1]
share of SCL-valid pixels with red<=0 or nir<=0: 0.1849
NDVI p2/p50/p98 after masking reflectance <= 0: [-0.914  0.043  0.707]
```

Mask (or clip) non-positive reflectance before computing any normalised index. Most of the affected pixels were sea in this test box.

### A5. STAC: how we find data

STAC is a JSON standard for describing geospatial data. It is like a data catalogue with a search API.

| STAC object | Analogy | Example |
| --- | --- | --- |
| **Catalog** / API root | database | `https://earth-search.aws.element84.com/v1` |
| **Collection** | table | `sentinel-2-c1-l2a` |
| **Item** | row: one scene or tile at one time | `S2A_T39RZH_20250112T065236_L2A` |
| **Asset** | file attached to the row | `red` → `…/B04.tif` |
| **Extensions** | typed columns | `eo:cloud_cover`, `proj:code`, `raster:bands` (scale, offset, nodata), `sar:polarizations`, `sat:relative_orbit` |

**Finding is not the same as fetching (measured).** Searching the catalogue was anonymous for all three providers. Downloading the files was not:

| Provider | Asset access |
| --- | --- |
| Planetary Computer | URLs must be **signed** with a temporary token: unsigned → HTTP 409, signed → 206 |
| CDSE | Needs an **account** and S3 keys: anonymous → 401 |
| Earth Search | Open |

Ingestion therefore has a separate "asset access" layer for each provider ([ADR 0008](decisions/0008-upstream-stac-providers-and-access-model.md)).

**A STAC Item is metadata, not data.** It tells you the date, footprint, cloud cover and file URLs. The pixels stay in the asset files.

### A6. File formats you will meet

| Format | What it is | Where we meet it | Why it matters |
| --- | --- | --- | --- |
| **COG** (Cloud-Optimised GeoTIFF) | A normal GeoTIFF whose pixels are stored in **tiles** (e.g. 512 or 1,024 px blocks) with **overviews** (pre-computed lower resolutions), arranged so a client can fetch only the bytes it needs with HTTP range requests (verified, cogeo.org) | Earth Search S2, PC S2/S1, all S1 providers, WorldCover | We can read a 20 km box out of a 110 km tile without downloading the whole file. Measured: 4–17 MB per S2 item instead of 77 MB+ per band |
| **JPEG 2000** (`.jp2`) | Wavelet-compressed image format used inside ESA's original products | CDSE S2 | Compact, but not designed for partial remote reads, so we download whole bands (76.9 MB measured) |
| **SAFE** | ESA's product **folder** format: a `manifest.safe`, plus `measurement/` (images), `annotation/` (XML metadata, including calibration and noise) and `preview/` | The original packaging of S1 and S2 products (CDSE `Product` asset) | Providers like PC and Earth Search expose the important SAFE files as individual STAC assets |
| **XML annotation** | Per-scene metadata: calibration LUTs, noise vectors, geometry | S1 assets `schema-calibration-vv`, etc. | Required to calibrate S1 to σ⁰ |
| **Zipped GeoTIFF** | Ordinary GeoTIFF inside a `.zip` | GHSL tiles | GDAL/rasterio can read it in place with a `zip://` path |
| **OSM JSON / PBF** | Vector features (nodes, ways, relations) with free-form `key=value` tags | Overpass API (JSON); Geofabrik extracts (PBF) | Vector data, not raster; geometry must be assembled from nodes |

### A7. Three ways to read the data

1. **Look at it in QGIS** (free desktop GIS). This is the fastest way to build intuition. Use *Layer → Add Raster Layer → Protocol: HTTP(S)* and paste an Earth Search COG URL. COGs open directly over HTTP (verified, cogeo.org). Add the OSM basemap via *XYZ Tiles*. (QGIS was not installed or tested in this session.)
2. **Python** with `pystac-client` (search) and `rasterio` (pixels), as in Part D. This is how the pipeline will work.
3. **Command line:** `rio info <url>` comes with rasterio. The following was measured on the Earth Search B04 COG:

   ```
   "crs": "EPSG:32639", "dtype": "uint16", "nodata": 0.0, "res": [10.0, 10.0],
   "shape": [10980, 10980], "blockxsize": 1024, "compress": "deflate", "tiled": true
   ```

   The GDAL equivalent is `gdalinfo /vsicurl/<url>`. GDAL's command-line tools are not installed in our environment (rasterio bundles the GDAL library, not its CLI), so that command is untested here.

---

## Part B — Source Cards

Each card answers the same questions. Licence details are summarised; the authoritative text is in the [source register](source-register.md).

### B1. Sentinel-2 Level-2A (optical): MVP vegetation signal and masks

| Question | Answer |
| --- | --- |
| **What is it?** | Multispectral images of sunlight reflected from the surface, corrected for the atmosphere (bottom-of-atmosphere reflectance). |
| **Who provides it?** | Produced by **ESA** for the EU's **Copernicus** programme. Hosted as copies by Element 84 / AWS (Earth Search), Microsoft (Planetary Computer) and CDSE, the official Copernicus distribution service (verified). |
| **How is it collected?** | Passive optical imaging from the S2 satellites (A1). ESA processes it to Level-1C, then to Level-2A with the Sen2Cor atmospheric-correction processor, and cuts it into 110 km MGRS tiles (A2, A3). |
| **What does it contain?** | 13 spectral bands at 10, 20 or 60 m (four at 10 m), plus quality and helper layers. The ones we use are listed in the band table below. |
| **Why do we access it?** | NDVI and SAVI for vegetation change (MVP 2). Cloud, shadow and water masks from SCL. Masks for the urban signal (vegetation, water). Later, the water indices for surface-water change. |
| **How do we access it?** | **Primary:** Earth Search `sentinel-2-c1-l2a`: anonymous COGs, windowed reads. **Fallback:** CDSE `sentinel-2-l2a`: free account and S3 keys, whole-band JP2 downloads, used for gaps in 2017–2018 and 2022 ([ADR 0009](decisions/0009-sentinel-2-l2a-mvp-source.md)). |
| **Format on access** | Earth Search: COG, uint16, deflate, 1,024 px blocks, nodata 0, scale 0.0001, offset −0.1. CDSE: JPEG 2000, uint16, nodata **not set**, scale and offset **not declared** in the file (measured). |
| **Volume** | Measured: 3.8–16.6 MB per item for a windowed read of B04 + B08 + SCL over the ≈ 20 × 15 km box; 76.9 MB per full CDSE band. About 430–520 items per year over the box across three tiles (measured). **Estimate:** 1.6–8.6 GB per year for those three bands at test-box size. |
| **Licence** | Copernicus Sentinel data terms: free, full and open. When publishing, include "Contains modified Copernicus Sentinel data [Year]" (verified). |

**The bands we use (verified wavelengths from the collection metadata):**

| Asset key (ES / CDSE) | Band | Centre wavelength | Pixel size | Used for |
| --- | --- | --- | --- | --- |
| `blue` / `B02_10m` | B02 | 0.490 µm | 10 m | True-colour images |
| `green` / `B03_10m` | B03 | 0.560 µm | 10 m | True colour; NDWI (later) |
| `red` / `B04_10m` | B04 | 0.665 µm | 10 m | NDVI, SAVI |
| `nir` / `B08_10m` | B08 | 0.842 µm | 10 m | NDVI, SAVI |
| `swir22` / `B12_20m` | B12 | 2.190 µm | 20 m | Optional built-up and moisture checks |
| `scl` / `SCL_20m` | SCL | — | 20 m | Cloud, shadow and water mask ([classes in the glossary](domain-glossary.md)) |
| `visual` / `TCI_10m` | True-colour image | — | 10 m | Visual interpretation (reference candidate R13) |

**Pitfalls:**
- Mixing processing baselines. PC's collection mixes 02.12–05.13 without offset metadata.
- The negative-reflectance trap (A4).
- SCL is only 20 m, so resample it with nearest-neighbour to 10 m.
- Scene `eo:cloud_cover` is a tile-wide figure, not one for your AOI.
- The same location may arrive in two UTM zones.
- SCL reliability over bright sand is an **assumption** to test in Stage 04.

### B2. Sentinel-1 GRD (radar): MVP urban-expansion signal

| Question | Answer |
| --- | --- |
| **What is it?** | Radar backscatter images: how much of the transmitted microwave energy returns to the satellite from each ground cell, in two polarisations. **VV** is sent and received vertically. **VH** is sent vertically and received horizontally, which is sensitive to volume scattering such as vegetation. |
| **Who provides it?** | **ESA / Copernicus**. Hosted by Planetary Computer (primary), Earth Search (AWS bucket `sentinel-s1-l1c`) and CDSE (verified). |
| **How is it collected?** | Active C-band SAR in IW mode: three sub-swaths scanned with the TOPSAR technique, 250 km swath, single-look resolution 5 × 20 m (verified, ESA). ESA processes it to GRD: multi-looked (resolution ≈ 20 × 22 m, delivered on a 10 m pixel grid), detected (amplitude only), and projected to ground range. Each pass is cut into **slices of about 25 s** along track (verified, SentiWiki S1 Products). |
| **What does it contain?** | Per scene: `vv` and `vh` amplitude images (uint16 DN, about 16,700 × 25,800 px), plus XML files: `schema-calibration-*` (LUTs to σ⁰, β⁰, γ), `schema-noise-*` (thermal-noise vectors) and `schema-product-*` (geometry and timing). There is **no CRS**, only about 200 GCPs (measured). |
| **Why do we access it?** | A persistent rise in backscatter is consistent with new vertical structures (MVP 1, [measurement spec](measurement-spec.md)). Radar works through cloud and dust and is not affected by sun angle. |
| **How do we access it?** | **Primary:** Planetary Computer `sentinel-1-grd`, with URLs signed by the `planetary-computer` package (anonymous tokens), read as windows. **Fallbacks:** Earth Search (anonymous; its metadata wrongly says requester-pays), then CDSE (account) ([ADR 0010](decisions/0010-sentinel-1-grd-mvp-source-and-level.md)). |
| **Format on access** | COG, uint16, zstd compression, 1,024 px blocks, overviews 2–64, nodata 0 (measured). CDSE: COG, about 513 MB (VV) and 434 MB (VH) per full scene (measured). |
| **Volume** | Measured: 5.7–21.5 MB per scene for a VV + VH windowed read over the box; about 123–147 scenes per year until 2024, 323 in 2025 (S1C joined). **Estimate:** 0.7–6.9 GB per year at test-box size. |
| **Licence** | Copernicus Sentinel data terms (as B1). |

**Pitfalls:**
- **Uncalibrated DN:** calibrate before comparing anything.
- **Speckle:** grainy noise inherent to radar. Average over time or space before deciding anything about a single pixel.
- **Slices:** one pass over Abu Dhabi can be split across two consecutive slices. We measured 4 % and 98 % coverage of the box from the two slices of 27 Dec 2025.
- **Track mixing:** compare only scenes from the same track (A1).
- **Thermal noise:** it biases dark areas such as water and smooth sand, especially in VH. Noise vectors are supplied; removal is a Stage 10 decision.
- **Sparse revisit before 2025:** only 4 S1B scenes over the box in 2017–2021 (measured; cause not investigated). S1B failed on 23 Dec 2021 (verified).
- **Platform name case:** `SENTINEL-1A` vs `sentinel-1a` differs between providers.

### B3. GHSL GHS-BUILT-S R2023A: context only

| Question | Answer |
| --- | --- |
| **What is it?** | A global grid of **built-up surface area** (m² per cell) for epochs 1975–2030 in 5-year steps. |
| **Who provides it?** | The **European Commission's Joint Research Centre (JRC)**, Global Human Settlement Layer project, Copernicus Emergency Management Service (verified). |
| **How is it collected?** | It is not observed directly. It is **modelled** from Sentinel-2 composites and Landsat imagery (verified, product page). Epochs between and beyond the observed years are interpolated or extrapolated; 2025 and 2030 are projections ([S10] in the glossary). |
| **What does it contain?** | One uint16 band: m² of built-up surface in each 100 m cell (0–10,000), nodata 65535. Over the test box: median 0, p98 4,421 m², 31.8 % of cells > 0 (measured). |
| **Why do we access it?** | Coarse context so analysts can see whether a candidate signal falls in an already built-up area. **Never** an input to our signal, and never treated as ground truth. |
| **How do we access it?** | Anonymous HTTPS download of 1,000 km Mollweide tiles (e.g. `…_R7_C24.zip`, 3.2 MB measured). There is no STAC catalogue; we compute the tile row and column from Mollweide coordinates. |
| **Format on access** | Zipped GeoTIFF in ESRI:54009 Mollweide, 100 m (measured). |
| **Licence** | **CC BY 4.0.** Must cite Pesaresi et al. (2024) and the product (verified). |

### B4. OpenStreetMap: context only

| Question | Answer |
| --- | --- |
| **What is it?** | A crowd-sourced map database: roads, buildings, land use and points of interest as vector features with free-form tags. |
| **Who provides it?** | The **OpenStreetMap Foundation**. Data is contributed by volunteers (verified, OSM copyright page). Mapping methods vary, e.g. tracing imagery, GPS surveys and bulk imports (**assumption** for this area). |
| **How is it collected?** | Edits by many people over time. Each feature records only who last edited it and when. A `start_date` tag (construction date) is optional, and present on only 0.01 % of buildings in the test box (measured). |
| **What does it contain?** | 26,044 buildings in the test box (measured). Tag coverage: `building:levels` 13 %, `height` 4.6 %, `name` 3.5 %. 48 % of buildings were last edited in 2023, probably a bulk edit (**assumption**). |
| **Why do we access it?** | Context for analysts: what is mapped there, such as roads, parks and building outlines. Possibly a stratification aid. **Edit dates are not construction dates.** |
| **How do we access it?** | Probe: the Overpass API (anonymous, shared, best-effort; one HTTP 502 measured). For the pipeline, a **dated extract file** (e.g. Geofabrik PBF) is proposed, for repeatability (Stage 09). |
| **Format on access** | JSON (Overpass) or PBF (extracts); EPSG:4326 coordinates. |
| **Licence** | **ODbL 1.0.** Credit "© OpenStreetMap contributors". A distributed database derived from OSM must also be ODbL (**share-alike**), so we keep OSM-derived layers separate from our products (verified; [ADR 0011](decisions/0011-context-layers-and-reference-candidates.md)). |

### B5. ESA WorldCover: reference and stratification candidate

| Question | Answer |
| --- | --- |
| **What is it?** | A global 10 m **land-cover classification** for 2020 and 2021, with 11 classes. |
| **Who provides it?** | **ESA**, produced by a consortium led by VITO; hosted on Planetary Computer (verified). |
| **How is it collected?** | Machine-learning classification of Sentinel-1 and Sentinel-2 time series. An `input_quality` asset records how many S1 and S2 observations were used per pixel (verified, collection metadata). 2020 uses algorithm v100 and 2021 uses v200, so **differences between the two years mix real change with algorithm change** (verified). |
| **What does it contain?** | Class codes: 10 tree cover, 20 shrubland, 30 grassland, 40 cropland, 50 built-up, 60 bare / sparse vegetation, 70 snow and ice, 80 permanent water, 90 herbaceous wetland, 95 mangroves, 100 moss and lichen. Test-box shares: water 0.45, bare 0.25, built-up 0.20, trees 0.04, mangroves 0.03 (measured). |
| **Why do we access it?** | A candidate for stratifying validation samples and as reference context (Stage 12 decides). It is a model output, not ground truth. |
| **How do we access it?** | Planetary Computer `esa-worldcover`, signed URLs, windowed read. |
| **Format on access** | COG, uint8, **EPSG:4326** (≈ 10 m in degrees), nodata 0 (measured). Reproject before computing areas. |
| **Licence** | **CC BY 4.0** (verified). |

### B6. Other reference candidates (Stage 12 decides; not profiled)

| Candidate | What it is | Status |
| --- | --- | --- |
| Impact Observatory / Esri annual LULC v02 | 10 m, 9-class annual land cover, 2017–2023, derived from S2 | CC BY 4.0 (verified from metadata); not profiled |
| S2 true-colour composites | Our own visual-interpretation imagery made from B1 | Redistributable under Copernicus terms |
| User-reviewed labels | Labels we create in Stage 12 | Licence decided in Stage 07 |
| Very-high-resolution basemaps | Detailed imagery for viewing only | **Terms not verified.** Never redistribute or derive published labels from it until they are. |

---

## Part C — Which Format We Save In, and Why (candidates only)

**Not decided.** Storage formats belong to Stages 05 (architecture), 06 (contracts), 09 (bronze) and 10 (silver). This section explains the realistic options so those decisions are informed.

| Data | Candidate formats | Trade-offs |
| --- | --- | --- |
| Raw downloads (bronze) | **Keep as delivered** (COG / JP2 / XML / zip), or **convert JP2 → COG** at ingestion | Keeping as delivered gives exact provenance and is simple. Converting gives one read path for all S2 data, at the cost of an extra step and a decision about compression |
| Analysis-ready rasters (silver: calibrated σ⁰, masked reflectance, all in one target CRS) | **COG** per scene and band, or **Zarr** data cubes (time × y × x arrays in chunks) | COG is universal and readable by QGIS, GDAL and STAC tools, but there are many files. Zarr suits time-series operations with xarray / dask, but is less friendly to desktop GIS and STAC asset conventions |
| Change and indicator products (gold) | **COG** with internal overviews | Directly servable and viewable; fits the required local STAC API |
| Per-window statistics, coverage tables, sample labels | **GeoParquet** / Parquet, possibly in a table format (Delta Lake / Iceberg) | Columnar, works with Spark and Sedona; a table format adds versioning and ACID at the cost of complexity |
| Context vectors (OSM, GHSL-derived outlines) | **GeoParquet**, kept **separate** from our products | Keeps the ODbL share-alike obligation contained |
| Metadata for everything we publish | **STAC Items and Collections (JSON)** in our local STAC API | Required by the project; records lineage (source item IDs, provider, baseline, processing version) |

One principle applies whatever we choose: **record lineage**. Every derived file should be traceable to its source STAC Item IDs, provider, processing baseline and our code version. This is what makes AC-01 (no duplicates on rerun) and the analytical claims auditable.

---

## Part D — Worked Example: One Pixel's Journey (verified output)

The code blocks below were extracted from this document and run exactly as written, with only `print` statements added. They reproduced the values shown: item, window shape, valid fraction, pixel NDVI 0.696, A_σ 638.2 and the σ⁰ percentiles. The longer outputs come from the fuller example script named at the top of this guide.

### D1. Find a scene (STAC search)

```python
from pystac_client import Client

BBOX = [54.30, 24.38, 54.50, 24.52]            # lon/lat test box, not the AOI
es = Client.open("https://earth-search.aws.element84.com/v1")
items = list(es.search(
    collections=["sentinel-2-c1-l2a"], bbox=BBOX, datetime="2025-01-01/2025-01-31",
    query={"eo:cloud_cover": {"lt": 5}, "mgrs:grid_square": {"eq": "ZH"}},
    sortby=[{"field": "properties.eo:cloud_cover", "direction": "asc"}], max_items=3,
).items())
item = items[0]
print(item.assets["red"].extra_fields["raster:bands"])
```

```
S2A_T39RZH_20250112T065236_L2A 2025-01-12T07:02:42.258000Z cloud=0.23 baseline=05.11 epsg=EPSG:32639
red asset href: https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/39/R/ZH/2025/1/S2A_T39RZH_20250112T065236_L2A/B04.tif
red raster:bands: [{'nodata': 0, 'data_type': 'uint16', 'spatial_resolution': 10, 'scale': 0.0001, 'offset': -0.1}]
```

### D2. Read only the window we need, convert, mask and compute NDVI

```python
import numpy as np, rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from rasterio.enums import Resampling

with rasterio.open(item.assets["red"].href) as r, rasterio.open(item.assets["nir"].href) as n:
    bounds = transform_bounds("EPSG:4326", r.crs, *BBOX)          # lon/lat box -> UTM metres
    win = from_bounds(*bounds, transform=r.transform).round_offsets().round_lengths()
    red_dn, nir_dn = r.read(1, window=win).astype("float32"), n.read(1, window=win).astype("float32")
with rasterio.open(item.assets["scl"].href) as s:                   # SCL is 20 m: resample to 10 m grid
    scl = s.read(1, window=from_bounds(*bounds, transform=s.transform).round_offsets().round_lengths(),
                 out_shape=red_dn.shape, resampling=Resampling.nearest)

red = np.where(red_dn == 0, np.nan, red_dn * 0.0001 - 0.1)          # DN -> reflectance (nodata 0)
nir = np.where(nir_dn == 0, np.nan, nir_dn * 0.0001 - 0.1)
bad = np.isin(scl, [0, 1, 3, 8, 9, 10]) | (red <= 0) | (nir <= 0)   # SCL mask + offset trap
ndvi = np.where(bad, np.nan, (nir - red) / (nir + red))
```

```
CRS: EPSG:32639 | pixel size: (10.0, 10.0) | window shape: (1602, 2068)
valid NDVI fraction: 0.783
SCL histogram: {3: 106440, 4: 108348, 5: 1714472, 6: 1356692, 7: 2440, 8: 15952, 9: 8592}
SCL-4 pixels with valid NDVI: 108341; their NDVI p10/p50/p90 = [0.538 0.696 0.803]
```

### D3. Follow one typical vegetation pixel

| Step | Value |
| --- | --- |
| Pixel in the window | row 672, column 1296 |
| Map coordinates (EPSG:32639) | x = 847,365 m, y = 2,709,575 m |
| Longitude / latitude | 54.42618 °E, 24.46103 °N |
| Raw DN | red 1,411, NIR 3,296 |
| SCL class | 4 (vegetation) |
| Reflectance | red 0.0411, NIR 0.2296. Leaves absorb red light and reflect near-infrared. |
| NDVI | (0.2296 − 0.0411) / (0.2296 + 0.0411) = **0.696**, the median of all SCL-vegetation pixels |
| For contrast: bare soil (SCL 5) | red 0.1156, NIR 0.2246 → NDVI 0.320 |
| For contrast: water (SCL 6) | red 0.0027, NIR 0.0014 → NDVI −0.317 |

Bare desert soil reaches an NDVI of about 0.3 here because bright soil reflects NIR. This is why the [measurement spec](measurement-spec.md) adds SAVI as an arid check. These values are single-date observations and say nothing about change.

### D4. Sentinel-1: from DN to σ⁰ in dB

```python
import planetary_computer, requests, xml.etree.ElementTree as ET
from rasterio.transform import rowcol

pc = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)
s1 = next(pc.search(collections=["sentinel-1-grd"],
                    ids=["S1A_IW_GRDH_1SDV_20251227T142434_20251227T142459_062502_07D505"]).items())
with rasterio.open(s1.assets["vv"].href) as src:                     # no CRS: use the GCPs
    gcps, _ = src.gcps
    row, col = (int(v[0]) for v in rowcol(gcps, [54.37], [24.47]))
    dn = src.read(1, window=((row - 50, row + 50), (col - 50, col + 50))).astype("float64")

cal = ET.fromstring(requests.get(s1.assets["schema-calibration-vv"].href).content)
vecs = cal.findall(".//calibrationVector")                           # LUT sampled on a sparse grid
lines = np.array([int(v.find("line").text) for v in vecs])
pix = np.array([int(x) for x in vecs[0].find("pixel").text.split()])
sig = np.array([[float(x) for x in v.find("sigmaNought").text.split()] for v in vecs])
a_sigma = np.interp(row, lines, [np.interp(col, pix, s) for s in sig])   # bilinear interpolation
sigma0_db = 10 * np.log10(dn**2 / a_sigma**2)
```

```
S1A_IW_GRDH_1SDV_20251227T142434_20251227T142459_062502_07D505 ascending rel_orbit=130 ['VV', 'VH']
CRS: None | GCPs: 210 EPSG:4326 | shape: (16728, 25816)
native pixel for lon=54.37 lat=24.47: row=16190 col=3833; DN window mean=520.8
calibration LUT: 27 vectors x 647 pixels; sigmaNought range 557.5-662.1
A_sigma at pixel = 638.2; sigma0 dB window p2/p50/p98 = [-13.   -4.2  10.1]
```

A median of −4.2 dB and a p98 of +10 dB over a 1 km window of dense city blocks are **plausible** for urban double-bounce scattering. That is a sanity check, not validation. This simplified example uses one LUT value for the whole window and skips noise removal, speckle filtering and geocoding. Those steps are Stage 10.

---

## Part E — Decoding Product Names

**Sentinel-2 (ESA compact naming, verified SentiWiki):** `S2B_MSIL2A_20260102T065159_N0511_R020_T39RZH_20260102T091615`

| Part | Meaning |
| --- | --- |
| `S2B` | Satellite: Sentinel-2B |
| `MSIL2A` | Instrument MSI, Level-2A |
| `20260102T065159` | Sensing start, UTC |
| `N0511` | Processing baseline 05.11 |
| `R020` | Relative orbit 20 (of 143) |
| `T39RZH` | MGRS tile |
| `20260102T091615` | Product discriminator: distinguishes products from the same datatake |

Earth Search uses its own shorter IDs, for example `S2A_T39RZH_20250112T065236_L2A`.

**Sentinel-1 (verified SentiWiki):** `S1A_IW_GRDH_1SDV_20251227T142434_20251227T142459_062502_07D505`

| Part | Meaning |
| --- | --- |
| `S1A` | Satellite |
| `IW` | Interferometric Wide mode |
| `GRD` + `H` | Product type + High resolution class |
| `1` | Level 1 |
| `S` | SAR standard product |
| `DV` | Dual polarisation, VV + VH |
| `20251227T142434` / `…142459` | Start and stop times, UTC (a ≈ 25 s slice) |
| `062502` | Absolute orbit number |
| `07D505` | Mission datatake ID: the **same value for both slices of one pass** |

ESA's full name ends with a 4-character product unique ID (a CRC checksum). PC drops it; CDSE adds `_COG` (measured).

---

## Part F — Pitfalls Checklist

| # | Pitfall | Applies to | Guard |
| --- | --- | --- | --- |
| 1 | Mixing processing baselines (the PB 04.00 offset) | S2 | Use Collection-1 only ([ADR 0009](decisions/0009-sentinel-2-l2a-mvp-source.md)) |
| 2 | Negative reflectance after the offset | S2 | Mask reflectance ≤ 0 before computing indices |
| 3 | Using tile-wide cloud cover as AOI cloud cover | S2 | Measure valid pixels in the AOI from SCL |
| 4 | Combining tiles in different UTM zones | S2 | Reproject to one target CRS (Stage 04/10) |
| 5 | Treating DN as backscatter | S1 | Calibrate with the per-scene LUT |
| 6 | Comparing different tracks or pass directions | S1 | Group by `sat:relative_orbit` and `sat:orbit_state` |
| 7 | Using one slice of a pass | S1 | Group slices by datatake ID |
| 8 | Computing areas in degrees | WorldCover, OSM | Reproject to metres |
| 9 | Treating modelled layers as observations | GHSL, WorldCover | Context only; record caveats |
| 10 | Treating OSM edit dates as construction dates | OSM | Never use them as evidence of change |
| 11 | Trusting provider metadata blindly | Earth Search S1 `requester_pays` | Re-verify access in Stage 09 |
| 12 | Publishing third-party data without notices | All | Attribution table in Stage 20/21 |
| 13 | Bulk-downloading full scenes | CDSE | Prefer windowed COG reads; respect quotas |

---

## Part G — Licence Obligations at a Glance

| Source | Licence | What we must do when publishing |
| --- | --- | --- |
| Sentinel-1 / Sentinel-2 | Copernicus Sentinel data terms | State "Contains modified Copernicus Sentinel data [Year]" |
| GHSL | CC BY 4.0 | Cite Pesaresi et al. (2024) and the product, and indicate changes |
| OpenStreetMap | ODbL 1.0 | Credit "© OpenStreetMap contributors" and link the licence. Share-alike applies to derived databases |
| WorldCover / IO LULC | CC BY 4.0 | Credit the producer and indicate changes |
| Very-high-resolution basemaps | Unverified | Do not redistribute |

---

## Sources (accessed 2026-11-14)

- ESA SentiWiki, S2 Mission: <https://sentiwiki.copernicus.eu/web/s2-mission>; S2 Products (tiling, naming): <https://sentiwiki.copernicus.eu/web/s2-products>
- ESA SentiWiki, S1 Mission (orbit, satellites, launch history): <https://sentiwiki.copernicus.eu/web/s1-mission>; S1 Products (levels, slicing, naming): <https://sentiwiki.copernicus.eu/web/s1-products>
- ESA, Sentinel-1 Instrument (IW swath and resolution): <https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Instrument>
- ESA technical note ESA-EOPG-CSCOP-TN-0002, *Radiometric Calibration of S-1 Level-1 Products* (cited via the PC `sentinel-1-rtc` collection description; PDF text not extracted in this session)
- GDAL SAFE driver (Sentinel-1 GCPs and calibration subdatasets): <https://gdal.org/en/stable/drivers/raster/safe.html>
- Cloud Optimized GeoTIFF: <https://cogeo.org/>
- GHS-BUILT-S R2023A product page: <https://human-settlement.emergency.copernicus.eu/ghs_buS2023.php>
- Planetary Computer `esa-worldcover` collection (classes, algorithm versions): <https://planetarycomputer.microsoft.com/api/stac/v1/collections/esa-worldcover>
- All licence, access and quota sources: see the [source register](source-register.md) and [profiling report §9](profiling-report.md)
