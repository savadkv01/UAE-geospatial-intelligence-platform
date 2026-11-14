# 0010. Sentinel-1 GRD MVP Source and Product Level

- Status: accepted
- Date: 2026-11-14
- Stage: 03-source-discovery-and-profiling
- Affected stages: 04, 05, 06, 09, 10, 12, 18

## Question

Which Sentinel-1 product level and provider should supply the MVP urban-expansion signal? The level determines who performs radiometric calibration and geocoding. The provider determines access, volume and resilience.

## Options considered

**Product level** (asked before profiling):

1. GRD only; calibrate to σ⁰ ourselves in Stage 10 (recommended): no account needed. Abu Dhabi is mostly flat, so terrain flattening adds little.
2. GRD plus Planetary Computer RTC (γ⁰, terrain-flattened, CC BY 4.0): ready-made, but needs a Planetary Computer account.
3. Custom.

**Provider** (asked after profiling):

1. Planetary Computer primary; Earth Search, then CDSE, as fallbacks (recommended): the only provider whose windowed pixel reads were measured.
2. Earth Search primary: anonymous, no signing; only a 1 KB header was read; its requester-pays metadata contradicts the measured access.
3. CDSE primary: official source; about 0.5 GB COG per polarisation per scene; needs an account.
4. Custom.

## User selection

Product level: "GRD only." Provider: "(Recommended) Planetary Computer primary (windowed reads measured), Earth Search then CDSE as fallbacks."

## Rationale

GRD avoids an account dependency. It keeps the calibration step under our control and reproducible, which supports the σ⁰ log-ratio specified in the [measurement spec](../measurement-spec.md). Planetary Computer gave measured, efficient windowed reads. Earth Search and CDSE give two independent fallbacks with the same assets.

## Evidence

All entries come from the [profiling report](../profiling-report.md) §4.2 and §6.2, dated 2026-11-14.

- **Measured (Planetary Computer):**
  - COG, zstd, 1,024 px blocks, overviews 2–64.
  - **No CRS**: georeferenced by 189–210 GCPs in EPSG:4326.
  - uint16 DN; nodata 0.
  - `schema-calibration-*` and `schema-noise-*` XML files available as assets.
  - Windowed VV+VH reads: 5.7–21.5 MB per scene, 0.8–2.7 s per band.
- **Measured:** four tracks cover the test box (asc 28, asc 130, desc 64, desc 166). There were about 123–147 IW scenes a year up to 2024, almost all from S1A (4 S1B items), and 323 in 2025 once S1C arrived. Earth Search and CDSE counts are comparable.
- **Measured:** one pass can span two consecutive slices (non-zero fractions of 0.04 and 0.98 for the two slices on 27 Dec 2025).
- **Measured:** CDSE serves S1 GRD COGs of 512.9 MB (VV) and 433.7 MB (VH) per scene.
- **Verified:** Planetary Computer `sentinel-1-rtc` requires an account to obtain SAS tokens (collection description).

## Consequences

- The open decision "σ⁰ vs terrain-flattened γ⁰" is resolved for the MVP in favour of **σ⁰ derived from GRD**. Stage 10 owns the method: calibration LUT, optional thermal-noise removal, geocoding from GCPs or orbit plus a DEM, and speckle handling.
- Stage 10 must assemble consecutive slices per pass before compositing. Comparisons stay within the same relative orbit and pass direction ([ADR 0006](0006-temporal-comparability-policy.md)).
- Before 2025 the revisit is about 12 days per track. Stage 04/12 must check whether N-window persistence ([ADR 0005](0005-persistence-confirmed-change-semantics.md)) has enough scenes per window.
- Ingestion normalises `platform` case and records the provider in lineage.
- RTC can be reconsidered by a superseding ADR if terrain or geocoding quality proves insufficient.
