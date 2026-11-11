---
description: "Stage 06: Define grains, keys, spatial and temporal semantics, formats, partitions and data contracts for all layers and entities."
agent: "agent"
---

# Stage 06: Data Modelling and Contracts

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md`
- `docs/measurement-spec.md`
- `docs/source-register.md`
- `docs/feasibility-pilot.md`
- `docs/architecture.md`

**Prerequisites:** Stages 01–05 must be `complete`. Otherwise, stop and list what is missing.

## 1. Objective, Boundaries and Non-goals

**Objective:** specify the logical and physical data model and the machine-checkable contracts for these entities:

- Source items and assets
- AOIs
- Processing runs
- Observation windows
- Analysis grids
- Feature summaries
- Change candidates
- Quality results
- Lineage
- Resource usage

**Non-goals:**
- Building pipelines.
- Choosing indicator thresholds. Stage 12 owns these.

## 2. Domain-learning Objective

Explain the following concepts:

- **Grain:** why the default must not be one row per raster pixel, and how to use grid cells or zones with aggregates instead.
- **Analysis grid choice:** a projected regular grid in a local UTM zone, H3, or administrative or planning zones. Cover their area and distortion implications.
- **Footprints:** modelling them as geometries.
- **Nodata denominators:** for example, `valid_pixel_count` versus `total_pixel_count`. This avoids false "zero change" results.
- **Times:** the difference between observation time, ingestion time and processing time.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Analysis grid:**
   - (a) A projected regular grid, for example, 100 m or 1 km cells in the approved UTM zone. This is recommended because it gives equal-area cells.
   - (b) H3 at a chosen resolution.
   - (c) Admin or planning zones, subject to the licence.
   - (d) A combination.
2. **Storage CRS policy:**
   - Raster processing CRS: native UTM versus a single common CRS for the AOI.
   - Vector storage CRS: EPSG:4326 plus a projected copy, or projected only.
3. **Identity and incrementality:**
   - Deterministic IDs: hashes of source item ID, asset, AOI version, window and code/config version.
   - Upsert or merge keys.
   - Late-arriving and reprocessed items.
   - Whether reprocessing creates a new version or replaces the old one.
4. **Partitioning and schema evolution:**
   - Partition keys: for example, by product and observation-window date.
   - Table formats, applying the Stage 05 ADR.
   - Compatibility policy: additive changes only, versus versioned contracts.

## 4. Evidence Plan

Use the Stage 03 and Stage 04 sample metadata to validate field types and cardinalities. Optionally, with approval, run a small disposable estimate of rows and bytes per window for each grid option.

## 5. Approval Gate

Present the entity list, grains, keys and the grid, CRS and partition choices. Get approval before writing the contract files.

## 6. Work Steps

1. Create `docs/data-model.md` with:
   - An entity-relationship Mermaid diagram.
   - For each entity: grain, primary and natural keys, deterministic-ID recipe, required fields, spatial semantics (geometry type, CRS, footprint versus AOI clip), temporal semantics (observation, ingestion and processing times), nullability, nodata handling and partitions.
2. Define machine-readable contracts in a place that later code will consume, for example, `contracts/*.yaml` or JSON Schema. Use the format the user selects. Do not introduce a contract framework without approval.
3. Add **source-to-target mappings** from source STAC fields and assets to the bronze, silver and gold fields.
4. Document the rules for incremental updates, idempotency, schema evolution and lineage linkage, such as `run_id` and input item IDs.
5. Record ADRs.

## 7. Deliverables

- `docs/data-model.md`
- The contract files
- The source-to-target mapping
- ADRs
- Updates to project state

## 8. Acceptance Checks

- Every gold product in the measurement spec maps to an entity with a defined grain.
- Every entity has a deterministic key.
- Every coverage-based metric has a valid-pixel denominator.
- The contract files parse. Validate them with an available YAML or JSON parser.
- The ER diagram renders.

**What falsifies success:** a per-pixel default grain, an ambiguous time field, or a key that changes across identical reruns.

## 9. Failure and Blocker Handling

If a source lacks a field that the contract needs, flag the gap and propose a derivation or a deferral. The user decides.

## 10. State and Completion Report

Update project state and traceability. Report the key modelling choices and their implications for Stages 09–12.

## 11. Handoff

- Suggested commit subject (propose only): `docs: add data model, contracts and source-to-target mappings`
- Next prompt: `07-governance-and-security-design.prompt.md`. Do not run it automatically.
