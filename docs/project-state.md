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
- **Next action:** run `01-business-requirements` from the prompt picker or with `Chat: Run Prompt...`.

## Stage Status

| # | Stage | Status | Approved outputs / evidence | Notes |
| --- | --- | --- | --- | --- |
| 01 | Business requirements | not started | — | — |
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

_None yet. Stage 01 owns this list; link to `docs/requirements.md` after approval._

## Unresolved Decisions

_None recorded yet._

## Invalidated Approvals

_None._

## Evidence Links

_None yet._

## Checks Run

| Date | Stage | Command / review | Environment | Result |
| --- | --- | --- | --- | --- |

## Blockers

_None._
