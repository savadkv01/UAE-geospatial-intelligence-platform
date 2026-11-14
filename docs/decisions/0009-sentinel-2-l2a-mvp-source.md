# 0009. Sentinel-2 L2A MVP Source

- Status: accepted
- Date: 2026-11-14
- Stage: 03-source-discovery-and-profiling
- Affected stages: 04, 05, 06, 09, 10, 12, 18

## Question

Which Sentinel-2 L2A collection should supply the MVP vegetation signal and the S2-derived masks? Radiometric consistency across processing baselines is required by the [measurement spec](../measurement-spec.md). It is easy to break by mixing collections.

## Options considered

1. Earth Search `sentinel-2-c1-l2a` primary, with CDSE `sentinel-2-l2a` as fallback for missing periods (recommended): both use Collection-1 processing baselines (05.xx). Earth Search serves anonymous COGs that support cheap windowed reads. CDSE fills the 2017–2018 and 2022 gaps but needs full JPEG 2000 band downloads and an account.
2. CDSE only: one consistent, complete archive, but about 77 MB per band per tile, no windowed remote reads, and an account dependency on every run.
3. Custom.

Planetary Computer `sentinel-2-l2a` was profiled and is excluded as a primary source. It mixes baselines 02.12–05.13, publishes no scale or offset metadata, and appears to contain duplicates in 2022–2023.

## User selection

"(Recommended) Earth Search c1 primary (anonymous COGs) + CDSE fallback for 2017–18 and 2022 gaps."

## Rationale

This keeps one radiometric processing chain (Collection-1) across both providers and minimises laptop transfer through windowed COG reads. CDSE is used only where Earth Search lacks data.

## Evidence

All entries come from the [profiling report](../profiling-report.md) §4.1 and §6.1, dated 2026-11-14.

- **Measured: items over the test box.**

  | Provider | 2017 | 2018 | 2019–2026 | 2022 |
  | --- | --- | --- | --- | --- |
  | Earth Search c1 | 9 | 147 | 339–519 | **36** |
  | CDSE | 192 | 417 | 432–519 | 435 |

  Both providers return only baselines 05.00–05.13.
- **Measured: Earth Search assets.** `raster:bands` scale 0.0001, offset −0.1, nodata 0. Windowed B04/B08/SCL reads cost 3.8–16.6 MB per item. Same-scene DN percentiles match the Planetary Computer copies for PB ≥ 05.
- **Measured: CDSE asset.** The B04 10 m JPEG 2000 file is 76.9 MB and downloaded in 7.9 s. It has no nodata value set and declares no scale or offset.
- **Verified:** the AWS Registry states that L2A has been available "globally since December 2018", which is consistent with Earth Search's sparse 2017–2018. The 2022 gap is unexplained.
- **Verified ([S2]):** the PB 04.00 offset of −1000 DN applies from 25 Jan 2022.

## Consequences

- Stage 09 ingests Earth Search `sentinel-2-c1-l2a` by default. It falls back to CDSE for any window with no Earth Search items, and records the provider in lineage.
- Reflectance is (DN + offset) / 10000 for both providers. Earth Search declares the offset in STAC. For CDSE it must be read from the product metadata, because the JP2 file has no scale or offset and no nodata value.
- **Never** mix Planetary Computer S2 items, or Earth Search `sentinel-2-pre-c1-l2a`, into the same series without per-item baseline handling.
- CDSE items need a spatial post-filter, because one spurious antimeridian item was measured.
- Asset keys differ by provider (`red` vs `B04_10m`), so Stage 06 contracts need a band-mapping table.
- Stage 04 should re-measure Earth Search coverage for the chosen AOI and seasons, including whether the 2022 gap affects anniversary baselines.
