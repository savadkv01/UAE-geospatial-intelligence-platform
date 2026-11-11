---
description: "Stage 11: Implement Spark/Sedona vector processing, grid and zone aggregation, and incremental lakehouse tables, with an honest benchmark."
agent: "agent"
---

# Stage 11: Spatial Transformation and Lakehouse

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/architecture.md`
- `docs/data-model.md`
- The contract files
- `docs/governance-security.md`
- The Stage 10 silver outputs

**Prerequisites:** Stages 01–10 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** use Spark with Apache Sedona, or the approved engine, for these jobs:

- Process the approved vector sources, for example, OSM features and GHSL-derived zones.
- Build the analysis grid.
- Run spatial joins.
- Run grid and zone aggregations of silver raster statistics.
- Maintain incremental, schema-checked lakehouse tables in the approved format.

**Non-goals:**
- Defining indicator thresholds. Stage 12 owns this.
- Orchestration. Stage 13 owns this.

## 2. Domain-learning Objective

Explain the following:

- Spatial join predicates, such as intersects versus within, and their edge effects at cell borders.
- Spatial partitioning and indexing in Sedona.
- How zonal statistics bridge raster and vector data. Raster-to-table summaries can be computed in Python and loaded into Spark, or computed with Sedona raster functions.
- The small-file problem.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Zonal-statistics path:**
   - (a) Compute per-cell statistics with rasterio or exactextract in Python, write them to GeoParquet, and then aggregate and join in Spark. This option is recommended for memory safety.
   - (b) Use Sedona raster functions.
   - (c) A hybrid.
2. **Incremental strategy:**
   - Merge or upsert keyed by the Stage 06 deterministic IDs, versus partition overwrite per observation window.
   - The compaction and small-file policy.
3. **OSM extraction scope:** which tags and layers to use, for example, buildings, landuse and the coastline. Decide them under the ODbL handling from Stage 07.
4. **Benchmark design:** pick one meaningful operation, for example, a grid-to-features spatial join. Compare it with a simpler baseline, such as GeoPandas or DuckDB spatial, measured under the same conditions.

## 4. Evidence Plan

Run the benchmark only with approval and on a bounded sample. Record the hardware, versions, data sizes, runtime and peak memory. Make no claims beyond local-mode scale.

## 5. Approval Gate

Get approval for the path, the incremental strategy, the OSM scope and the benchmark plan before you implement.

## 6. Work Steps

1. Implement Spark jobs as package modules with thin entry points. Configure the Spark session from versioned config with explicit memory limits.
2. Build these tables according to the contracts:
   - Grid
   - Feature summaries
   - Joins and aggregations
3. Apply schema validation on write. Add partitioning and compaction.
4. Verify that the Python code and the planned serving layer can read the tables. For example, read GeoParquet with GeoPandas or DuckDB, and check that the geometry encoding and CRS metadata are correct.
5. Write tests using a local Spark session and tiny fixtures:
   - Join correctness on boundary cases
   - Idempotent rerun
   - Schema-drift rejection

   Run the first test right after the first job.
6. Run the benchmark and write `docs/benchmarks/spatial-join.md`. Explain honestly why Spark remains in the portfolio architecture: incremental table management, scale-out readiness and the transferable skill. Include where the simpler baseline won.

## 7. Deliverables

- The Spark/Sedona modules
- The lakehouse tables (local)
- Tests
- The benchmark report
- Updates to project state

## 8. Acceptance Checks

- The tests pass.
- A rerun yields identical row counts and keys.
- The file counts per partition are within the policy.
- Tables written by Spark are readable from Python with the correct CRS.
- The benchmark numbers are reproducible from the recorded commands.

**What falsifies success:** duplicate keys after a rerun, lost CRS metadata, or benchmark claims without measurements.

## 9. Failure and Blocker Handling

If a Spark job runs out of memory or a Sedona version is incompatible, record the error. Propose a smaller partitioning or a pinned version, and get approval if this changes the architecture.

## 10. State and Completion Report

Update project state, traceability and the measured resources.

## 11. Handoff

- Suggested commit subject (propose only): `feat(spatial): add Sedona grid aggregation and incremental lakehouse tables`
- Next prompt: `12-change-products-and-indicators.prompt.md`. Do not run it automatically.
