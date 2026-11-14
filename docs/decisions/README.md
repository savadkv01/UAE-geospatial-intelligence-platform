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
