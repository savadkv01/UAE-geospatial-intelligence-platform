# 0017. Raster and Spark Responsibilities

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 08, 10–13, 18

## Question
Which engine owns raster math and which owns relational/spatial tables?

## Options considered
1. Python/rasterio for raster work; Spark/Sedona for tabular and spatial work.
2. Sedona raster functions as well; larger JVM raster working set, still needs Python for S1 preparation.
3. Spark coordinates Python raster partitions; more parallelism demonstrations but adds orchestration and serialization overhead.

## User selection
Q2(a): Python/rasterio for raster work; Spark/Sedona for vector, zonal tables, joins and incremental tables.

## Rationale
Windowed array I/O fits the raster processing pattern; partitioned rows fit joins and aggregation.

## Evidence
[Pilot](../feasibility-pilot.md) §5: measured 1.48 GB peak pilot RSS. [Sedona platform matrix](https://sedona.apache.org/latest/setup/platform/), checked 2026-11-25, covers Spark 4.1.

## Consequences
Use Spark 4.1 local with Sedona 1.9, Java 17 and Scala 2.13, subject to pin verification. Python performs zonal extraction and polygonization, not Spark. No distributed-scale inference.
