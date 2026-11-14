# Domain Glossary

- Status: Approved for writing by the user on 2026-11-14 (Stage 02 approval gate); Stage 02 outcome awaiting user acceptance.
- Stage: 02 — Domain and measurement
- Companion: [Measurement specification](measurement-spec.md)

Concise definitions for the Earth-observation terms used in this project, with Abu Dhabi examples. Evidence labels follow the shared workflow contract: **verified** (source and access date), **measured**, **assumption** or **proposed target**. Sources named here are **candidates** until Stage 03 verifies their availability and licensing.

## 1. Sensors and Data

| Term | Definition | Abu Dhabi example / why it matters | Evidence |
| --- | --- | --- | --- |
| Optical sensing | A passive sensor measures reflected sunlight in spectral bands. Clouds, haze, smoke and shadow block or distort the signal. | Summer dust and haze reduce the number of usable Sentinel-2 looks. | Verified [S1] |
| Surface reflectance (BOA) | Fraction of incident sunlight reflected by the surface after atmospheric correction ("bottom of atmosphere"); unitless, nominally 0–1. Sentinel-2 L2A stores it as scaled integers. | Bright desert sand has high reflectance in most bands, which drives several confounders below. | Verified [S1] |
| Sentinel-2 bands used | B4 red (665 nm, 10 m), B8 NIR (842 nm, 10 m), B3 green (560 nm, 10 m), B11 SWIR-1 (1610 nm, 20 m), B12 SWIR-2 (2190 nm, 20 m). | Vegetation indices use 10 m bands; SWIR-based indices are limited to 20 m native resolution. | Verified [S1] |
| Processing baseline (PB) | Version of the ESA processing algorithms applied to a product. Since PB 04.00 (from 25 Jan 2022), L1C/L2A digital numbers carry an additive radiometric offset of −1000; reflectance = (DN + offset) / quantification value, read from product metadata. | A time series spanning 2021–2023 shows a false reflectance jump if the offset is ignored. | Verified [S2] |
| Collection-1 | ESA's reprocessing of the Sentinel-2 archive with a uniform processing baseline for consistent time series. | Prefer a consistently processed archive for multi-year comparison; Stage 03 verifies what is available. | Verified [S3] |
| Scene Classification Layer (SCL) | Per-pixel class map in Sentinel-2 L2A (Sen2Cor): 0 no data, 1 saturated/defective, 2 dark area, 3 cloud shadow, 4 vegetation, 5 not vegetated, 6 water, 7 unclassified, 8 cloud medium probability, 9 cloud high probability, 10 thin cirrus, 11 snow/ice. Provided at 20 m. | Primary input to cloud/shadow masking. Its reliability over bright sand is an **assumption** to test in Stage 04. | Verified [S1] |
| Synthetic aperture radar (SAR) | An active sensor that transmits microwave pulses and records the returned energy. It works day and night and through cloud. | Sentinel-1 gives observations in conditions when Sentinel-2 is blocked by cloud or haze. | Verified [S4] |
| C-band | Microwave band around 5.405 GHz (wavelength ≈ 5.5 cm) used by Sentinel-1. C-band can penetrate dry sand to some depth. | Some returns over dry desert can come from below the visible surface. | Verified [S4], [S5] |
| Backscatter coefficient (σ⁰, sigma-nought) | Calibrated radar return per unit ground area, usually expressed in decibels (dB). It depends on roughness, geometry, moisture and viewing geometry, **not** on colour. | Smooth sand and calm water look dark; towers and walls look bright. | Verified [S4], [S5] |
| Polarisation (VV, VH) | Transmit/receive orientation. VV is co-polarised; VH is cross-polarised and more sensitive to volume scattering, such as vegetation. | VH increases can come from vegetation growth rather than construction. | Verified [S5] |
| Scattering mechanisms | *Specular*: a smooth surface reflects energy away from the sensor (dark). *Rough surface*: diffuse return (brighter). *Volume*: multiple scattering inside vegetation. *Double bounce*: wall–ground corner reflection that sends strong energy back to the sensor (brightest; typical of buildings). | Construction on smooth desert turns dark pixels bright. This is why SAR is the primary urban-expansion signal (see [ADR 0004](decisions/0004-mvp-indicator-families.md)). | Verified [S5], [S6] |
| Speckle | Granular, multiplicative noise inherent to coherent SAR imaging. It is reduced by spatial filtering or temporal averaging, and compared using ratios or logs rather than differences. | Single-date SAR comparisons in Abu Dhabi produce many false "changes" unless speckle is reduced. | Verified [S7] |
| Ground Range Detected (GRD) | Sentinel-1 Level-1 product: multi-looked, detected intensity projected to ground range. | The candidate SAR product type for this project; Stage 03 verifies access. | Verified [S4] |
| Raster | A grid of cells (pixels) holding values, e.g. reflectance, NDVI, σ⁰ or masks. | All indices and change layers in this project are rasters. | Verified (standard definition) |
| Vector | Geometries (points, lines, polygons) with attributes. | The AOI boundary, OSM features and candidate-change polygons. | Verified (standard definition) |

## 2. Spatial Reference and Grids

| Term | Definition | Abu Dhabi example / why it matters | Evidence |
| --- | --- | --- | --- |
| Coordinate reference system (CRS) | Defines how coordinates map to locations on Earth. | Every raster and vector must have an explicit CRS; mixing CRSs silently misaligns data. | Verified (standard definition) |
| Geographic CRS | Angular coordinates (latitude/longitude), e.g. EPSG:4326. One degree is not a constant ground distance. | Do not compute areas or buffers in degrees. | Verified (standard definition) |
| Projected CRS | Planar coordinates in metres, e.g. UTM. | Required for pixel-area statistics and distances. | Verified (standard definition) |
| UTM zones 39N / 40N | Zone 39N covers 48°E–54°E (EPSG:32639); zone 40N covers 54°E–60°E (EPSG:32640). Abu Dhabi city (~54.4°E) falls in 40N; much of Al Dhafra (west of 54°E) falls in 39N. | Sentinel-2 tiles arrive in their native zone. An AOI that crosses 54°E needs an explicit common target CRS, decided in Stage 04 or 10. | Verified (UTM zone formula: zone = ⌊(lon + 180) / 6⌋ + 1) |
| Area distortion | Map projections distort area away from their central meridian, and geographic CRSs do not preserve area. | Areas of change must be computed in a suitable projected or equal-area CRS, with that CRS recorded. | Verified (standard definition) |
| Pixel spacing | Distance between pixel centres on the delivered grid. | Sentinel-1 IW GRD-HR is delivered at 10 m spacing. | Verified [S4] |
| Spatial resolution | The smallest separation at which two objects can be distinguished. It can be coarser than the pixel spacing. | Sentinel-1 IW GRD-HR resolution is ≈ 20 m × 22 m despite 10 m spacing. Some secondary sources conflate the two. | Verified [S4] |
| Geometric accuracy | How closely pixel positions match true ground positions. It is independent of resolution. | A 10 m pixel with a several-metre geolocation error cannot support parcel-level claims ([ADR 0003](decisions/0003-acceptance-target-frameworks-and-non-goals.md)). | Verified (concept); exact values to be profiled in Stage 03 |
| Layover / radar shadow | SAR geometric distortions on tall or steep targets: tall objects lean towards the sensor (layover), and areas behind them receive no signal (shadow). | They affect the high-rise districts of Abu Dhabi island; mask or flag them. | Verified [S5] |

## 3. Observation Quality and Comparability

| Term | Definition | Abu Dhabi example / why it matters | Evidence |
| --- | --- | --- | --- |
| Observation window | The batch period over which observations are composited ([ADR 0002](decisions/0002-batch-observation-window-cadence.md)). Its length is deferred. | — | User decision |
| Composite | One per-pixel value summarising the valid observations in a window, e.g. a median. | Reduces the effect of residual cloud, haze and speckle. The compositing method is a **proposed target**. | Assumption |
| Valid-observation count | Number of unmasked observations contributing to a pixel's composite. | A low count means a weak composite. It is reported per product ([ADR 0007](decisions/0007-uncertainty-communication.md)). | User decision |
| Cloud / haze / shadow / nodata | Conditions that make optical pixels invalid or biased. Nodata also includes swath edges and SAR border noise. | Dust events can survive cloud masks as haze; this is an **assumption** to profile in Stage 04. | Verified [S1]; haze behaviour is an assumption |
| Seasonality | Recurring within-year variation in surface state, sun angle and atmosphere. | Summer: high sun, heavy irrigation, frequent dust. Winter: lower sun, longer tower shadows, occasional rain green-up. | Assumption (domain knowledge; to be measured in Stage 04) |
| Same-season comparison | Comparing a window with the equivalent window in other years. | This is the project's comparability policy ([ADR 0006](decisions/0006-temporal-comparability-policy.md)). | User decision |
| Acquisition geometry | For SAR: relative orbit, pass direction (ascending/descending) and incidence angle. Backscatter changes with geometry. | Compare only same-orbit, same-pass composites. | Verified [S5] |
| Tide state | Water level at acquisition time. | Intertidal flats and mangroves along the Abu Dhabi coast look different at high and low tide. Products only **flag** tide relevance for now ([ADR 0006](decisions/0006-temporal-comparability-policy.md)). | Assumption (no tide source verified yet) |
| Uncertainty sources | Sensor noise and speckle, residual cloud and haze, mask errors, geolocation error, compositing choice, confounders, low observation counts, and reference-data error. | Each product reports its counts and variability. | Verified (concepts); quantities to be measured |

## 4. Arid and Coastal Confounders

| Confounder | Effect | Abu Dhabi example | Evidence |
| --- | --- | --- | --- |
| Irrigation | Vegetation indices follow watering schedules rather than natural phenology. | Parks, road verges, farms and date plantations can green or brown abruptly. | Assumption (to observe in Stage 04) |
| Low-NDVI desert background | Bare sand has low, positive NDVI that varies with soil brightness and moisture. Small vegetation changes can be comparable in size to background variation. | Sparse shrubland across Al Dhafra. SAVI (L = 0.5) is computed as a check. | Verified [S8] (soil effect); local magnitude is an assumption |
| Sabkha moisture | Salt flats change brightness and radar backscatter when wet. | Coastal sabkha after rain or high water. | Assumption |
| Bright sand vs built-up | Sand and concrete have similar SWIR/NIR behaviour, so optical built-up indices confuse them. | This is why NDBI-type indices are not the primary urban signal. | Verified [S9] (index definition); confusion in arid areas is an assumption to observe |
| C-band sand penetration | Radar returns can include subsurface contributions in dry sand. | Unexpected brightness in dry desert that does not indicate surface construction. | Verified [S5] |
| Construction-stage disturbance | Excavation, stockpiles, fences and cranes change backscatter before (or without) completed buildings. | Large development sites on the urban fringe. | Assumption |
| Tide | Moves the land–water boundary and changes the background of intertidal vegetation. | Mangroves and intertidal flats; coastal-line "change". | Assumption |
| Turbidity | Sediment-laden water raises visible reflectance and can weaken water indices. | Dredging and reclamation plumes. | Assumption |
| Land reclamation | New land appears where there was water; σ⁰ and indices change strongly. | Reclaimed islands and waterfronts. New land is **not** the same as new built-up area. | Assumption |

## 5. Interpretation Terms

| Term | Definition | Evidence |
| --- | --- | --- |
| Candidate signal | A measured change that warrants analyst review, not a confirmed fact ([requirements BR-04](requirements.md)). | User decision |
| Persistence-confirmed candidate change | A change relative to a same-season baseline that recurs in N consecutive windows. N is a **proposed target** (2–3) ([ADR 0005](decisions/0005-persistence-confirmed-change-semantics.md)). | User decision |
| Surface-water area vs volume | Optical and SAR sensors measure the 2-D extent of water. They do not measure depth or volume. | Verified (physical definition) |
| Association vs causation | Co-occurrence of signals (e.g. new built-up area and vegetation loss) is not evidence that one caused the other. Causal attribution is a non-goal ([ADR 0003](decisions/0003-acceptance-target-frameworks-and-non-goals.md)). | User decision |
| Modelled vs observed (GHSL) | GHSL built-up surface epochs are "spatially-temporally interpolated or extrapolated from 1975 to 2030 in 5 year intervals", at 100 m. Projected epochs are not observations. | Verified [S10] |
| OSM edit date vs construction date | An OpenStreetMap edit timestamp records when a contributor mapped a feature, not when the feature was built. | Verified (OSM data model; Stage 03 to cite) |

## Sources

Accessed 2026-11-14 unless noted.

- [S1] ESA / Copernicus, Sentinel-2 Collection-1 L2A product page and SentiWiki S2 Products: <https://sentinels.copernicus.eu/sentinel-data-access/sentinel-products/sentinel-2-data-products/collection-1-level-2a>, <https://sentiwiki.copernicus.eu/web/s2-products>; GDAL Sentinel-2 driver documentation: <https://gdal.org/en/stable/drivers/raster/sentinel2.html>.
- [S2] ESA STEP Forum, "[INFO] Introduction of additional Radiometric Offset in PB04.00 products" (25 Mar 2022), with links to the ESA Processing Baseline page: <https://forum.step.esa.int/t/info-introduction-of-additional-radiometric-offset-in-pb04-00-products/35431>.
- [S3] ESA SentiWiki, S2 Processing (Collection-1 processing baseline): <https://sentiwiki.copernicus.eu/web/s2-processing>.
- [S4] ESA, Sentinel-1 Product Definition and Product Specification: <https://sentinels.copernicus.eu/documents/247904/1877131/Sentinel-1-Product-Definition.pdf>.
- [S5] Alaska Satellite Facility (NASA DAAC), HyP3 "Introduction to SAR": <https://hyp3-docs.asf.alaska.edu/guides/introduction_to_sar/> (figures credited to the SAR Handbook).
- [S6] Flores-Anderson, A.I. et al. (2019). *The SAR Handbook: Comprehensive Methodologies for Forest Monitoring and Biomass Estimation.* NASA SERVIR. doi:10.25966/nr2c-s697.
- [S7] Bazi, Y., Bruzzone, L., Melgani, F. (2005). An unsupervised approach based on the generalized Gaussian model to automatic change detection in multitemporal SAR images. *IEEE TGRS* 43(4), 874–887. doi:10.1109/TGRS.2004.842441.
- [S8] Huete, A.R. (1988). A soil-adjusted vegetation index (SAVI). *Remote Sensing of Environment* 25(3), 295–309. doi:10.1016/0034-4257(88)90106-X.
- [S9] Zha, Y., Gao, J., Ni, S. (2003). Use of normalized difference built-up index in automatically mapping urban areas from TM imagery. *International Journal of Remote Sensing* 24(3), 583–594.
- [S10] Pesaresi, M., Politis, P. (2023). GHS-BUILT-S R2023A. European Commission, JRC. doi:10.2905/9F06F36F-4B11-47EC-ABB0-4F8B7B1D72EA; catalogue description: <https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S>.
