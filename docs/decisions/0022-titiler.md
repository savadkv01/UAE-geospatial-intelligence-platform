# 0022. Dynamic Raster Tiles

- Status: superseded by 0028
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 07, 08, 15, 17, 18

## Question
Should the laptop render map tiles dynamically?

## Options considered
1. Optional TiTiler: interactive display at an estimated 0.3–1 GB with bounded cache and concurrency.
2. Static quicklooks only: no tile service RAM, less interactive styling and comparison.

## User selection
Q4b(a): TiTiler with capped GDAL cache in the serving profile.

## Rationale
Provide interactive map tiles without a pre-generated tile pyramid.

## Evidence
[TiTiler 2.4.1](https://pypi.org/project/titiler-core/), checked 2026-11-25. Memory is an estimate.

## Consequences
Read only approved published COGs. Tile styling is not an authoritative indicator computation.
