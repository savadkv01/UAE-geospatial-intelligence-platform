# 0028. titiler-pgstac for Dynamic Tiles

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 08, 15, 17, 18
- Supersedes: [0022](0022-titiler.md)

## Question
Which dynamic tiler should serve published rasters?

## Options considered
1. Plain TiTiler (ADR 0022): renders any COG URL it is given, so the catalogue boundary would have to be enforced elsewhere.
2. titiler-pgstac: TiTiler with a PgSTAC backend that renders by STAC Item or search, so only indexed releases render. Estimated RAM is similar.
3. Static previews only: no tiler.

## User selection
After the Stage 05 review the user said "proceed with changes", which approved option 2 as recommended.

## Rationale
It aligns tile access with the STAC publication boundary ([ADR 0027](0027-stac-visibility-publication-boundary.md)), supports multi-Item mosaics for window comparison, and is the component the eoAPI reference stack uses with stac-fastapi-pgstac.

## Evidence
- **Verified (2026-11-25):** [titiler-pgstac 3.2.2](https://github.com/stac-utils/titiler-pgstac/releases), released 2026-11-18, MIT licence; [eoAPI](https://github.com/developmentseed/eoAPI), MIT licence, active.
- **Estimate:** about 1.0 GB with a capped GDAL cache, the same allowance as before.

## Consequences
- It runs in the `serving` profile and reads PgSTAC with a read-only role (Stage 07).
- Stage 08 pins a version pair compatible with pgSTAC 0.10 and stac-fastapi-pgstac.
