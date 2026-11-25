# 0032. Layered Quality Gates

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 06, 09–15, 19

## Question
Where do data-quality checks run, and what happens when one fails? Stage 14 still selects the framework.

## Options considered
1. Layered gates at bronze, silver, gold and publish, with quarantine:
   - error-severity failures block the downstream step;
   - warnings are recorded;
   - results go to a Delta `quality_results` table, and summaries go into STAC Item properties.
2. A single gate before publication: simpler, but failures are found late and recovery costs more.
3. Custom.

## User selection
Q4(a): layered gates with quarantine.

## Rationale
Catching bad inputs at the layer where they appear limits recomputation and supports AC-02 recovery and AC-05 coverage reporting. Some checks must run early to be useful, such as the S1 GCP and LUT presence check and the constant-array regression check for risk R6.

## Evidence
- **Verified (2026-11-25):** GX Core 1.24.1 (Apache-2.0) and the move of Soda Core to the Elastic Licence 2.0 come from a secondary source; Stage 14 re-verifies them.
- **Measured:** the pilot defect R6 ([feasibility pilot](../feasibility-pilot.md) §4).

## Consequences
- The library shortlist for Stage 14 is GX Core and pandera.
- Raster checks use rasterio and COG validation.
- Gates check integrity, not analytical accuracy (AC-04).
