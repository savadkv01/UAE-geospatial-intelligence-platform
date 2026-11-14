# Measurement Specification

- Status: Approved for writing by the user on 2026-11-14 (Stage 02 approval gate); Stage 02 outcome awaiting user acceptance.
- Stage: 02 — Domain and measurement
- Companion: [Domain glossary](domain-glossary.md)
- Decisions: [ADR 0004](decisions/0004-mvp-indicator-families.md), [ADR 0005](decisions/0005-persistence-confirmed-change-semantics.md), [ADR 0006](decisions/0006-temporal-comparability-policy.md), [ADR 0007](decisions/0007-uncertainty-communication.md)

This document defines what each capability's indicator physically measures, and what it **cannot claim**. It does not select final sources (Stage 03), an AOI (Stage 04) or algorithms (Stages 10–12).

- All sources are **candidates** until Stage 03 verifies their availability and licensing.
- Every threshold, N, minimum mapping unit and compositing method is a **proposed target** until Stage 04 or 12 provides evidence. None is validated.
- Source keys `[S#]` refer to the [glossary sources](domain-glossary.md#sources), accessed 2026-11-14.

## Cross-cutting Rules (all capabilities)

| Rule | Specification | Basis |
| --- | --- | --- |
| Change semantics | A **persistence-confirmed candidate change** is a change against a same-season baseline composite that recurs in N consecutive observation windows. N = 2–3 is a proposed target. | [ADR 0005](decisions/0005-persistence-confirmed-change-semantics.md) |
| Temporal comparability | Compare the same season across years (anniversary windows). Products near the coast carry a **tide-relevance flag**; tide is not normalised. | [ADR 0006](decisions/0006-temporal-comparability-policy.md) |
| Uncertainty | Publish per-pixel valid-observation counts and index variability as evidence, plus confidence classes derived from them by documented rules whose thresholds are proposed targets. | [ADR 0007](decisions/0007-uncertainty-communication.md) |
| Coverage | Report the valid-observation coverage fraction of the AOI for each product and window (AC-05). | [Requirements](requirements.md) |
| Radiometric consistency | Sentinel-2 reflectance = (DN + offset) / quantification value, both read from product metadata. Account for the PB 04.00 offset (−1000 from 25 Jan 2022) or use a consistently harmonised collection. | Verified [S2] |
| Spatial reference | Compute areas and statistics in a recorded projected CRS. The Abu Dhabi area spans UTM 39N/40N at 54°E; the common target CRS is decided in Stage 04 or 10. | Glossary §2 |
| Language | Outputs are candidate signals for analyst interpretation, not facts, causal explanations or ground truth. | [ADR 0003](decisions/0003-acceptance-target-frameworks-and-non-goals.md), BR-04 |

## MVP Capability 1 — Candidate Urban Expansion

| Field | Specification |
| --- | --- |
| Question answered | Where are persistent candidate signals of new built structures that warrant analyst review? |
| Physical quantity | Change in the radar backscatter coefficient σ⁰ (dB) in VV and VH. A persistent increase is consistent with new vertical or rough structures, especially wall–ground double bounce, on a previously smooth surface. |
| Candidate inputs | **Primary:** Sentinel-1 IW GRD (VV, VH) [S4]. **Masks:** Sentinel-2 L2A for vegetation, water and cloud masks. **Reference context only, not inputs to the signal:** GHSL GHS-BUILT-S R2023A [S10] and OpenStreetMap. |
| Index / formula | Log-ratio of speckle-reduced temporal composites: Δσ⁰ = 10·log₁₀(σ⁰_window / σ⁰_baseline) = σ⁰_window[dB] − σ⁰_baseline[dB] [S7]. The log-ratio suits SAR's multiplicative speckle [S7]. Calibration choice (σ⁰ vs terrain-flattened γ⁰) is deferred to Stage 03 or 10. |
| Unit and range | dB, unbounded. Positive values mean brighter than the baseline. Any candidate threshold is a **proposed target**. |
| Spatial grain | 10 m delivered pixel spacing, ≈ 20 × 22 m true resolution [S4], plus a minimum mapping unit for candidate objects (**proposed target**, Stage 04/12). |
| Temporal grain | Per observation window (length deferred, [ADR 0002](decisions/0002-batch-observation-window-cadence.md)), compared against a same-season baseline. |
| Comparability rules | Same season across years. Compare only composites from the **same relative orbit and pass direction** (backscatter depends on viewing geometry [S5]). Require persistence across N consecutive windows. |
| Masks needed | Sea and permanent water; dense or irrigated vegetation (an NDVI-based mask, because VH responds to vegetation volume scattering); swath nodata and border noise; layover and shadow near high-rise areas; optionally recently reclaimed land, flagged rather than suppressed. |
| Known confounders | Rain-wetted soil and sabkha moisture; excavation, stockpiles, fences and cranes; parked vehicles, equipment and ships; dune movement; building orientation relative to the look direction (affects double-bounce strength); C-band penetration of dry sand [S5]; vegetation growth (VH); land reclamation (new land ≠ new built-up area); speckle residual. |
| Uncertainty representation | Valid S1 observation count per window; temporal standard deviation of σ⁰ (dB) within each window; persistence count k of N; confidence class derived from these by documented rules ([ADR 0007](decisions/0007-uncertainty-communication.md)). |
| **Cannot claim** | It is **not** a building footprint, building height, building use or population. It is **not** a construction permit, a construction start date or a completion date. It makes no parcel-level claims. Land reclamation or ground disturbance is **not** proof of construction. GHSL epochs are spatially and temporally interpolated or extrapolated (2025 and 2030 are projections) and are **not** independent observations [S10]. An OSM edit date is **not** a construction date. No causal claim about why development occurred. |
| Validation idea | Stage 12: a stratified sample of candidate and non-candidate locations, labelled by visual interpretation of reference imagery (licence and source to be verified in Stage 03), with agreement metrics per AC-04. Use GHSL and OSM only as coarse, caveated context. |

## MVP Capability 2 — Vegetation Change

| Field | Specification |
| --- | --- |
| Question answered | Where and when has green vegetation cover potentially changed (gain or loss), relative to the same season in earlier years? |
| Physical quantity | The normalised contrast between red absorption by chlorophyll and near-infrared scattering by leaf structure. It is a proxy for the presence and density of green, photosynthetically active vegetation within a pixel. |
| Candidate inputs | Sentinel-2 L2A: B4 red (665 nm, 10 m), B8 NIR (842 nm, 10 m), SCL (20 m) [S1]. |
| Index / formula | **Published indicator:** NDVI = (B8 − B4) / (B8 + B4) (Rouse et al. 1974 [S11]). **Arid check:** SAVI = (1 + L)(B8 − B4) / (B8 + B4 + L), with L = 0.5 (Huete 1988 [S8]). Both use surface reflectance after the offset and scaling rule above. Change: ΔNDVI = NDVI_window − NDVI_baseline, on composites. |
| Unit and range | Unitless. NDVI and SAVI lie in [−1, 1] for reflectances in [0, 1]; ΔNDVI lies in [−2, 2]. Any change threshold is a **proposed target**. |
| Spatial grain | 10 m. |
| Temporal grain | Per observation window, as a per-pixel composite (median of valid observations is the proposed method), compared against a same-season baseline. |
| Comparability rules | Same season across years; consistent radiometric processing across processing baselines and across S2 platforms; persistence across N consecutive windows; tide-relevance flag on intertidal and mangrove areas. |
| Masks needed | SCL 0 (no data), 1 (saturated/defective), 3 (cloud shadow), 8 (cloud medium probability), 9 (cloud high probability) and 10 (thin cirrus) [S1]. Water (SCL 6, or an index-based water mask) is excluded from vegetation statistics. Whether to mask SCL 2 (dark area) is a **proposed target** to test in Stage 04. |
| Known confounders | Irrigation schedules (abrupt green-up or brown-down); seasonality; desert soil brightness and moisture shifting the low-NDVI background [S8]; wet sabkha; residual dust or haze; possible SCL misclassification over bright sand (**assumption**, to test in Stage 04); the PB 04.00 radiometric offset [S2]; cross-calibration between S2 platforms; sun-angle effects between seasons; tide in mangrove and intertidal areas. |
| Uncertainty representation | Valid-observation count per window; NDVI standard deviation within each window; persistence count k of N; an NDVI–SAVI agreement flag (does SAVI change in the same direction?); confidence class derived from these by documented rules ([ADR 0007](decisions/0007-uncertainty-communication.md)). |
| **Cannot claim** | NDVI is **not** biomass, carbon stock, leaf area, plant health, species or crop yield. ΔNDVI is **not** a cause: it does not show irrigation policy, drought, development or management. It is **not** a measure of water use. It makes no parcel-level claims. A green-up in a single window is **not** a persistent change. |
| Validation idea | Stage 12: a stratified sample (e.g. parks, farms, plantations, mangroves, desert background), labelled by visual interpretation of reference imagery, with agreement metrics per AC-04. NDVI–SAVI consistency serves as an internal plausibility check, not as validation. |

## Deferred Capabilities — Provisional Rows

These capabilities are later increments ([ADR 0001](decisions/0001-audience-and-mvp-priorities.md)). The rows below are **provisional**. The index family, inputs, grain and validation are **not yet decided** and require their own decision checkpoint, and ADR, when each capability enters scope.

| Field | Surface-water extent change | Broad coastal change | Multi-year environmental indicators |
| --- | --- | --- | --- |
| Question answered | Where and when has the 2-D extent of surface water potentially changed? | Where are broad coastal-change signals that warrant review? | How do selected indicators vary across multiple years? |
| Physical quantity | Water presence per pixel → water-covered **area** | Position of the land–water boundary at acquisition time | Long-term statistics of published indicators (e.g. NDVI, water area, built signal) |
| Candidate index families (not decided) | NDWI = (Green − NIR)/(Green + NIR) (McFeeters 1996 [S12]); MNDWI = (Green − SWIR)/(Green + SWIR) (Xu 2006 [S13]); SAR low-backscatter thresholding | Shoreline derived from water masks (optical or SAR) | Trend or anomaly statistics over the per-window series |
| Key confounders | Turbidity, sun glint, shadows of tall buildings, wet sabkha, tide | **Tide**, waves, turbidity, reclamation, dredging | Sensor and processing changes, varying observation counts, seasonality |
| **Cannot claim** | Water **area** is **not** water **volume** or depth. It is not water quality. | Shoreline change can reflect **tide state, not erosion**. Reclamation is not natural accretion. No causal attribution. | Co-variation is **association, not causation**. A trend is not a forecast. |
| Status | Provisional; decide at entry | Provisional; tide normalisation needs a verified tide source ([ADR 0006](decisions/0006-temporal-comparability-policy.md)) | Provisional; trend semantics to decide at entry |

## Additional Sources

Sources [S1]–[S10] are listed in the [glossary](domain-glossary.md#sources).

- [S11] Rouse, J.W., Haas, R.H., Schell, J.A., Deering, D.W. (1974). Monitoring vegetation systems in the Great Plains with ERTS. *Third ERTS Symposium*, NASA SP-351, Vol. 1, 309–317.
- [S12] McFeeters, S.K. (1996). The use of the Normalized Difference Water Index (NDWI) in the delineation of open water features. *International Journal of Remote Sensing* 17(7), 1425–1432.
- [S13] Xu, H. (2006). Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery. *International Journal of Remote Sensing* 27(14), 3025–3033.

Citation details for [S11]–[S13] were verified by web search on 2026-11-14. The original full texts were not retrieved; the formulas match the standard published definitions.
