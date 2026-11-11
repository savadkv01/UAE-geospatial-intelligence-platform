---
description: "Stage 05: Design and approve the medallion, compute, storage, orchestration, STAC and serving architecture, with ADRs and Mermaid diagrams."
agent: "agent"
---

# Stage 05: Solution and Data Architecture

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md) and all accepted ADRs
- `docs/requirements.md`
- `docs/measurement-spec.md`
- `docs/source-register.md`
- `docs/feasibility-pilot.md`

**Prerequisites:** Stages 01â€“04 must be `complete`, with a `go` outcome. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** design an architecture that satisfies the requirements within the measured laptop envelope. The architecture covers:

- Medallion layers
- Raster versus vector compute responsibilities
- Storage
- Orchestration
- Upstream and local STAC
- Serving
- Observability
- Deployment profiles

**Non-goals:**
- Implementation. This stage produces no Compose files and no code.
- Detailed table schemas. Stage 06 owns these.
- Security controls. Stage 07 designs them, but this stage identifies the trust boundaries.

## 2. Domain-learning Objective

Explain:
- Why raster processing (windowed array I/O with GDAL/rasterio) and tabular or vector processing (Spark/Sedona) suit different engines.
- What a COG is and why HTTP range reads matter.
- How a STAC API differs from a tile server.
- Why Spark local mode demonstrates the programming model and partitioning, not distributed-scale performance.

## 3. Decision Checkpoints

Ask at most 2â€“4 related questions per interaction and wait for each answer. Present each option with its trade-offs and its effect on RAM and disk.

1. **Medallion layer semantics:**
   - Bronze: acquired originals plus manifests.
   - Silver: analysis-ready, aligned rasters and clean vectors.
   - Gold: indicators, change candidates and aggregates.

   Confirm these semantics or propose a variant.
2. **Raster versus Spark responsibility split:**
   - (a) Python/rasterio for raster processing; Spark/Sedona for vector, zonal-summary tables, joins and incremental tables. This option is recommended.
   - (b) Spark for raster tiling as well, for example, through Sedona raster functions. Note the memory risk.
   - (c) Custom split.
3. **Storage and table format:**
   - Object storage: (a) the local filesystem with bind or named volumes, or (b) MinIO with S3 semantics.
   - Table format: (a) GeoParquet only, (b) Delta Lake or (c) Apache Iceberg, with a note on spatial support and maturity.
   - Metadata store: PostgreSQL/PostGIS for the STAC API backend.
4. **Local STAC API and serving:**
   - Local STAC API: (a) stac-fastapi-pgstac or (b) a lighter alternative. Verify current project status first.
   - Raster tiles: (a) TiTiler, or (b) static COG previews only.
   - Analyst user interface: (a) a lightweight web map, (b) a notebook or Streamlit-style app, or (c) a minimal API only.
5. **Airflow deployment shape:**
   - (a) LocalExecutor with Postgres. This is recommended for laptops.
   - (b) CeleryExecutor. This is heavier.

   Also choose the Airflow version after checking the current documentation.
6. **Deployment profiles:** for example, `core` (minimal), `serving` and `monitoring`, with per-profile memory envelopes taken from the Stage 04 measurements.

Do not remove required technologies (Python, Spark, upstream and local STAC, Airflow) without an explicit user decision and an ADR.

## 4. Evidence Plan

Verify the current versions, maintenance status, licences and Windows/WSL2 compatibility of the candidate components from official sources, with access dates. A small disposable probe is optional, for example, measuring the idle RAM of an image. It requires approval.

## 5. Approval Gate

Present the proposed architecture as a short summary plus the draft diagrams. Get approval for each material decision before writing the ADRs and documents.

## 6. Work Steps

1. Create `docs/architecture.md` with these sections:
   - Context
   - Quality attributes
   - Layer semantics
   - Component responsibilities and limits, including what Spark, Airflow and STAC each do **not** do
   - Interfaces
   - Error paths
   - **Publication consistency**: how gold outputs and STAC items are published atomically or in a safely ordered way
   - Resource envelopes
   - Deployment profiles
   - Deferred options
2. Add Mermaid diagrams: system context, components, data flow from bronze to silver to gold to STAC and serving, and local deployment with Compose services and profiles. Validate the diagram syntax.
3. Record one ADR per material decision.
4. Update the traceability by mapping the requirements to components.

## 7. Deliverables

- `docs/architecture.md` with four Mermaid diagrams
- ADRs
- Updates to project state

## 8. Acceptance Checks

- Each requirement maps to a component.
- Each component has an owner stage.
- The memory envelope per profile is at most the approved budget, using measured or explicitly estimated values.
- The diagrams render.
- No claim about distributed performance appears.

**What falsifies success:** an architecture that needs more RAM than measured, an unexplained required technology, or a missing publication-consistency design.

## 9. Failure and Blocker Handling

If a required technology does not fit the budget, present the trade-offs. Options include an optional profile, a smaller footprint or a user-approved revision. Let the user decide.

## 10. State and Completion Report

Update project state and summarize the accepted ADRs and the deferred items.

## 11. Handoff

- Suggested commit subject (propose only): `docs: add approved solution architecture and ADRs`
- Next prompt: `06-data-modelling-and-contracts.prompt.md`. Do not run it automatically.
