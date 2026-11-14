# 0004. MVP Indicator Families

- Status: accepted
- Date: 2026-11-14
- Stage: 02-domain-and-measurement
- Affected stages: 03, 04, 09, 10, 11, 12, 14, 15, 18

## Question

Which indicator family should measure each MVP capability (candidate urban expansion, vegetation change), and how much detail should the measurement specification give the deferred capabilities? The choice determines the sensors, data volume and the confounders each product must handle in arid, coastal Abu Dhabi.

## Options considered

**Candidate urban expansion**

1. Optical built-up index (NDBI-type) only: simplest and uses only Sentinel-2. Bright sand and built-up surfaces have similar SWIR/NIR behaviour, which risks many false positives in desert.
2. SAR backscatter increase (Sentinel-1 VV/VH, from double bounce) as the primary signal, optical masks for confounders, and GHSL as reference context only (recommended): suits the desert and is unaffected by cloud. It adds a second sensor, larger scenes (~1 GB per GRD scene, an **assumption** to measure in Stage 03) and speckle handling.
3. GHSL epoch comparison only: cheapest, but its epochs are modelled at 5-year steps, so it cannot monitor per observation window.
4. Custom.

**Vegetation change**

1. NDVI only: simplest and widely understood, but sensitive to soil background.
2. SAVI/MSAVI only: handles bright soil better, but is less familiar.
3. NDVI as the published indicator plus SAVI (L = 0.5) as an arid check (recommended): uses the same bands, so the extra compute is small.
4. Custom.

**Detail for deferred capabilities**

1. Full rows for the MVP plus provisional rows for the deferred capabilities (recommended).
2. Full rows for all five capabilities now.
3. MVP rows only.

## User selection

- Urban: “SAR backscatter primary + optical masks + GHSL as reference.”
- Vegetation: “NDVI primary + SAVI arid check.”
- Deferred scope: “Full MVP rows + provisional deferred rows.”

## Rationale

The user accepted the recommendations. C-band SAR responds to the structural change (double bounce) that construction introduces on smooth desert surfaces, and it is not blocked by cloud or haze. Optical built-up indices are prone to sand/built-up confusion. NDVI keeps the published vegetation indicator interpretable, while SAVI makes the arid soil-background effect visible at negligible cost. Provisional rows keep the deferred capabilities' "cannot claim" boundaries explicit without committing to designs early.

## Evidence

- **Verified (2026-11-14):** ASF HyP3 "Introduction to SAR" and the SAR Handbook (doi:10.25966/nr2c-s697) on scattering mechanisms; Sentinel-1 GRD spacing and resolution from the ESA Product Definition; NDVI (Rouse et al. 1974), SAVI (Huete 1988, doi:10.1016/0034-4257(88)90106-X), NDBI (Zha et al. 2003); GHSL R2023A interpolated/extrapolated epochs (doi:10.2905/9F06F36F-4B11-47EC-ABB0-4F8B7B1D72EA). Full list: [glossary sources](../domain-glossary.md#sources).
- **Assumption:** that SAR backscatter increase is a usable urban-expansion signal in the pilot AOI; to be tested in Stage 04 (feasibility) and Stage 12 (evaluation).
- **Assumption:** S1 GRD scene size and the laptop storage impact; to be measured in Stages 03 and 18.

## Consequences

- Stage 03 must verify Sentinel-1 IW GRD and Sentinel-2 L2A access, licensing and volumes, and GHSL and OSM terms for use as reference context.
- The urban pipeline needs SAR calibration, speckle reduction and same-orbit comparison, plus an optical-derived vegetation and water mask.
- GHSL and OSM must not be presented as observations of change or as construction dates.
- The deferred capabilities each require a new decision checkpoint and ADR when they enter scope.
- Detailed definitions are in [measurement-spec.md](../measurement-spec.md).
