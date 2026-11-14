# Project State

> The single source of truth for workflow progress. Stage prompts read this file first and update it at the end of each session.
> Allowed states are `not started`, `in progress`, `blocked`, `awaiting approval` and `complete`. Mark a stage `complete` only when the user accepts its outcome.
> Creating the prompt pack approved **no** project decisions.

## Workflow Settings

| Setting | Value | Source |
| --- | --- | --- |
| Workflow granularity | 21 stages (one prompt per stage) | User selection during prompt-pack generation |
| Learning interaction | Guided explanations with approval at each material decision | User selection during prompt-pack generation |
| Git policy | No Git operations unless the user specifically asks to commit or merge; agent proposes commits only | User selection during prompt-pack generation |

## Active Stage

- **Active stage:** none
- **Next action:** run `03-source-discovery-and-profiling` when ready; it is not started automatically.

## Stage Status

| # | Stage | Status | Approved outputs / evidence | Notes |
| --- | --- | --- | --- | --- |
| 01 | Business requirements | complete | [Approved requirements](requirements.md); [ADR 0001](decisions/0001-audience-and-mvp-priorities.md); [ADR 0002](decisions/0002-batch-observation-window-cadence.md); [ADR 0003](decisions/0003-acceptance-target-frameworks-and-non-goals.md) | Document review passed and user accepted the Stage 01 outcome. |
| 02 | Domain and measurement | complete | [Domain glossary](domain-glossary.md); [Measurement spec](measurement-spec.md); [ADR 0004](decisions/0004-mvp-indicator-families.md); [ADR 0005](decisions/0005-persistence-confirmed-change-semantics.md); [ADR 0006](decisions/0006-temporal-comparability-policy.md); [ADR 0007](decisions/0007-uncertainty-communication.md) | Document review passed and user accepted the Stage 02 outcome on 2026-11-14. |
| 03 | Source discovery and profiling | not started | — | — |
| 04 | AOI and feasibility pilot | not started | — | — |
| 05 | Solution and data architecture | not started | — | — |
| 06 | Data modelling and contracts | not started | — | — |
| 07 | Governance and security design | not started | — | — |
| 08 | Repository and local infrastructure | not started | — | — |
| 09 | Source ingestion and bronze | not started | — | — |
| 10 | Raster standardization and silver | not started | — | — |
| 11 | Spatial transformation and lakehouse | not started | — | — |
| 12 | Change products and indicators | not started | — | — |
| 13 | Airflow orchestration and recovery | not started | — | — |
| 14 | Quality and validation gates | not started | — | — |
| 15 | STAC API and analyst serving | not started | — | — |
| 16 | Observability and operational runbooks | not started | — | — |
| 17 | Security and governance verification | not started | — | — |
| 18 | Performance and resource FinOps | not started | — | — |
| 19 | End-to-end and reproducibility | not started | — | — |
| 20 | Documentation and portfolio story | not started | — | — |
| 21 | GitHub release and handover | not started | — | — |

## Approved Requirements

[Approved requirements](requirements.md) — accepted by the user on 2026-11-11.

## Unresolved Decisions

- Exact observation-window length and freshness deadline; resolve with source/runtime evidence in Stages 03, 13 and 18.
- Analytical reference source, metric selection, and numeric agreement and coverage thresholds; resolve in Stage 12, informed by Stages 03–04.
- Persistence N (proposed 2–3), minimum mapping unit, compositing method, confidence-class rules, and whether to mask SCL class 2; resolve with evidence in Stages 04 and 12.
- Common target CRS for an AOI spanning UTM 39N/40N; resolve in Stage 04 or 10.
- SAR calibration choice (σ⁰ vs terrain-flattened γ⁰); resolve in Stage 03 or 10.
- Index families for the deferred capabilities (water, coastal, multi-year) and tide normalisation; decide when each enters scope.

**Open questions for Stage 03 (source verification):** Sentinel-1 IW GRD and Sentinel-2 L2A (Collection-1 / harmonised) access, licensing, archive depth, revisit over Abu Dhabi and per-scene volume; GHSL R2023A and OSM terms for use as reference context; candidate reference imagery for labelling (licence); any free tide data source.

## Invalidated Approvals

_None._

## Evidence Links

- [Business requirements](requirements.md)
- [Domain glossary](domain-glossary.md)
- [Measurement specification](measurement-spec.md)
- [Decision index](decisions/README.md)

## Checks Run

| Date | Stage | Command / review | Environment | Result |
| --- | --- | --- | --- | --- |
| 2026-11-11 | 01 | Document review against Stage 01 acceptance checks and user acceptance | Repository files; no external data or downloads | Passed; Stage 01 accepted |
| 2026-11-14 | 02 | Web verification of index formulas, sensor specifications and GHSL epoch semantics (ESA SentiWiki, ESA STEP forum, ASF HyP3, JRC GHSL catalogue, peer-reviewed citations) | Web search and fetch; no data downloads | Citations verified; MDPI full text blocked (HTTP 403), not relied on |
| 2026-11-14 | 02 | Document review against Stage 02 acceptance checks | Repository files | Passed: both MVP rows complete including "cannot claim"; every formula cited; arid and coastal confounders addressed; no threshold presented as validated |

## Blockers

_None._
