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
- **Next action:** run `02-domain-and-measurement` when ready; it is not started automatically.

## Stage Status

| # | Stage | Status | Approved outputs / evidence | Notes |
| --- | --- | --- | --- | --- |
| 01 | Business requirements | complete | [Approved requirements](requirements.md); [ADR 0001](decisions/0001-audience-and-mvp-priorities.md); [ADR 0002](decisions/0002-batch-observation-window-cadence.md); [ADR 0003](decisions/0003-acceptance-target-frameworks-and-non-goals.md) | Document review passed and user accepted the Stage 01 outcome. |
| 02 | Domain and measurement | not started | — | — |
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
- Analyst workflow details and whether secondary stakeholder personas are needed; validate in Stage 02.

## Invalidated Approvals

_None._

## Evidence Links

- [Business requirements](requirements.md)
- [Decision index](decisions/README.md)

## Checks Run

| Date | Stage | Command / review | Environment | Result |
| --- | --- | --- | --- | --- |
| 2026-11-11 | 01 | Document review against Stage 01 acceptance checks and user acceptance | Repository files; no external data or downloads | Passed; Stage 01 accepted |

## Blockers

_None._
