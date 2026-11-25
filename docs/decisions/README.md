# Architecture and Project Decision Records

This folder holds numbered decision records (ADRs) for material project decisions. Record a decision only after the user selects an option. The agent never fills in a user's answer.

## Conventions

- File name: `NNNN-short-kebab-title.md`, numbered sequentially from `0001`.
- Status: `proposed`, `accepted`, `superseded` or `rejected`.
- To change an accepted decision, create a new ADR that supersedes it. Then set the old ADR's status to `superseded by NNNN` and leave its content unchanged. Also record any invalidated downstream approvals in [project-state](../project-state.md).

## Index

| ADR | Title | Status | Stage | Date |
| --- | --- | --- | --- | --- |
| [0001](0001-audience-and-mvp-priorities.md) | Audience and MVP Priorities | accepted | 01 | 2026-11-11 |
| [0002](0002-batch-observation-window-cadence.md) | Batch Observation-Window Cadence | accepted | 01 | 2026-11-11 |
| [0003](0003-acceptance-target-frameworks-and-non-goals.md) | Acceptance Target Frameworks and Non-goals | accepted | 01 | 2026-11-11 |
| [0004](0004-mvp-indicator-families.md) | MVP Indicator Families | accepted | 02 | 2026-11-14 |
| [0005](0005-persistence-confirmed-change-semantics.md) | Persistence-Confirmed Change Semantics | accepted | 02 | 2026-11-14 |
| [0006](0006-temporal-comparability-policy.md) | Temporal Comparability Policy | accepted | 02 | 2026-11-14 |
| [0007](0007-uncertainty-communication.md) | Uncertainty Communication | accepted | 02 | 2026-11-14 |
| [0008](0008-upstream-stac-providers-and-access-model.md) | Upstream STAC Providers and Access Model | accepted | 03 | 2026-11-14 |
| [0009](0009-sentinel-2-l2a-mvp-source.md) | Sentinel-2 L2A MVP Source | accepted | 03 | 2026-11-14 |
| [0010](0010-sentinel-1-grd-mvp-source-and-level.md) | Sentinel-1 GRD MVP Source and Product Level | accepted | 03 | 2026-11-14 |
| [0011](0011-context-layers-and-reference-candidates.md) | Context Layers and Reference-Evidence Candidates | accepted | 03 | 2026-11-14 |
| [0012](0012-laptop-constraints-and-data-budgets.md) | Laptop Constraints and Data Budgets | accepted | 04 | 2026-11-24 |
| [0013](0013-pilot-aoi.md) | Pilot AOI | accepted | 04 | 2026-11-24 |
| [0014](0014-observation-period-and-window.md) | Observation Period and Window | accepted | 04 | 2026-11-24 |
| [0015](0015-feasibility-pilot-gates-and-outcome.md) | Feasibility Pilot Gates and Outcome (go with waiver) | accepted | 04 | 2026-11-24 |
| [0016](0016-persisted-medallion.md) | Persisted Medallion | accepted | 05 | 2026-11-25 |
| [0017](0017-raster-and-spark-responsibilities.md) | Raster and Spark Responsibilities | accepted | 05 | 2026-11-25 |
| [0018](0018-wsl2-filesystem-storage.md) | WSL2 Filesystem Storage | accepted | 05 | 2026-11-25 |
| [0019](0019-delta-and-geoparquet.md) | Delta and GeoParquet | accepted | 05 | 2026-11-25 |
| [0020](0020-shared-postgres.md) | Shared PostgreSQL/PostGIS | accepted | 05 | 2026-11-25 |
| [0021](0021-local-stac-api.md) | Local STAC API | superseded by 0027 (boundary detail) | 05 | 2026-11-25 |
| [0022](0022-titiler.md) | Dynamic Raster Tiles | superseded by 0028 | 05 | 2026-11-25 |
| [0023](0023-analyst-web-map.md) | Analyst Web Map | accepted | 05 | 2026-11-25 |
| [0024](0024-airflow-localexecutor.md) | Airflow LocalExecutor | accepted | 05 | 2026-11-25 |
| [0025](0025-airflow-version.md) | Airflow Release Line | accepted | 05 | 2026-11-25 |
| [0026](0026-deployment-profiles.md) | Deployment Profiles and Resource Verification | accepted | 05 | 2026-11-25 |
| [0027](0027-stac-visibility-publication-boundary.md) | STAC Visibility as the Publication Boundary | accepted | 05 | 2026-11-25 |
| [0028](0028-titiler-pgstac.md) | titiler-pgstac for Dynamic Tiles | accepted | 05 | 2026-11-25 |
| [0029](0029-built-in-lineage.md) | Built-in Lineage | accepted | 05 | 2026-11-25 |
| [0030](0030-stac-as-product-catalog.md) | STAC as the Product Catalog | accepted | 05 | 2026-11-25 |
| [0031](0031-data-products-and-contracts.md) | Data Products and Contracts | accepted | 05 | 2026-11-25 |
| [0032](0032-layered-quality-gates.md) | Layered Quality Gates | accepted | 05 | 2026-11-25 |

## Template

```markdown
# NNNN. <Decision title>

- Status: proposed | accepted | superseded by NNNN | rejected
- Date: YYYY-MM-DD
- Stage: NN-<stage-name>
- Affected stages: <list>

## Question
<The decision the user was asked to make, and why it was material.>

## Options considered
1. <Option A>: trade-offs, laptop/resource impact, delivery impact
2. <Option B>: ...
3. <Custom / other>: ...

## User selection
<The user's exact selection, quoted or faithfully paraphrased, including any custom details.>

## Rationale
<Why this option was chosen.>

## Evidence
<Links to source documentation (with access dates), measurements, probe outputs and commands. Label each item as verified, measured or assumption.>

## Consequences
<What this enables or constrains, follow-up work, risks and residual uncertainty.>
```
