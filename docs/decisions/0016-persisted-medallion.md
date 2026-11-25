# 0016. Persisted Medallion

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 06, 09–15, 19

## Question
Which outputs are kept as restart points and which are published?

## Options considered
1. Persist bronze and silver; publish only gold. Uses more disk but retains replay and restart points.
2. Keep silver ephemeral. Saves roughly 2.8 GB on the pilot-derived estimate but repeats calibration/warping on recovery.

## User selection
Q1(a): Persist bronze and silver; publish gold only.

## Rationale
Keep per-date recovery points while separating acquired data, standardized data and analyst-facing products.

## Evidence
[Stage 04 pilot](../feasibility-pilot.md) §6: measured per-date sizes and estimated full-scope volume; not a measurement of complete gold releases.

## Consequences
Bronze retains immutable native-grid acquired bytes/subsets and manifests, silver retains aligned rasters and clean vectors, and gold carries composites, change candidates, evidence and summaries. Use COG for raster deliverables; preserve originals and source metadata when subsetting or conversion cannot preserve replay semantics.
