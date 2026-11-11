---
description: "Stage 13: Orchestrate the tested package entry points in Airflow with bounded concurrency, backfills, safe publication and a demonstrated recovery."
agent: "agent"
---

# Stage 13: Airflow Orchestration and Recovery

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/architecture.md`
- `docs/data-model.md`
- The runbooks
- The package entry points from Stages 09–12

**Prerequisites:** Stages 01–12 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** schedule and recover the pipeline per observation window by orchestrating tested package entry points.

**Non-goals:**
- Business logic inside DAG files.
- Passing rasters or large data through XCom. Pass only references and IDs.
- Distributed executors beyond the approved architecture.

## 2. Domain-learning Objective

Explain the following:

- Data intervals versus run time in Airflow.
- Mapping observation windows to data intervals.
- Why satellite freshness depends on the acquisition date plus the provider's publication latency.
- Backfill semantics for imagery.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **DAG topology:**
   - (a) One DAG per window with task groups for ingest, silver, spatial, products, quality and publish.
   - (b) Separate DAGs linked by datasets or assets.
   - (c) Custom.
2. **Concurrency and resource controls:**
   - Pools.
   - `max_active_runs` and task concurrency within the memory budget.
   - Timeouts and retries per task type.
3. **Freshness semantics and schedule:** for example, check for new items weekly, and close a window only after N days of publication latency.
4. **Safe publication:** how to stage outputs and promote them atomically, and how to prevent double publication. Options include a publication lock or record keyed by window and product version, an idempotent STAC upsert, and a single-active-run constraint.

## 4. Evidence Plan

Use a tiny-window configuration for fast DAG tests. Measure the scheduler and worker memory under the `core` profile.

## 5. Approval Gate

Get approval for the topology, the controls, the freshness rules and the publication design before you implement.

## 6. Work Steps

1. Write DAGs that call package entry points through operators. Choose the operator type based on the approved architecture: Python callable, Bash, or Docker. Read the configuration from versioned files and Airflow connections or variables. Never put secrets in the DAG code.
2. Implement checkpoints and skip-if-done behaviour using the Stage 09–12 manifests and keys.
3. Implement publish-gating: the publish step runs only if the quality gates pass. Stage 14 extends this; here, add the hook and a minimal check.
4. Write tests:
   - DAG import and integrity
   - Task dependencies
   - No top-level heavy imports or I/O

   Run them right after the first DAG.
5. **Recovery demo:** with approval, inject a failure, for example, a task that raises on a flag. Show the retry and failure, fix the cause, clear the task and rerun it. Show that the outputs and STAC records are not duplicated.
6. **Double-publish demo:** trigger two concurrent runs for the same window, and show that only one publishes.
7. Run a bounded backfill for at least two windows.
8. Write `docs/runbooks/orchestration.md` covering triggering, backfill, recovery, clearing tasks and pausing.

## 7. Deliverables

- The DAGs
- Tests
- The recovery and backfill evidence log
- The orchestration runbook
- Updates to project state

## 8. Acceptance Checks

- The DAG tests pass.
- The failure demo recovers with no duplicate outputs, shown by key counts before and after.
- The concurrent publish produces a single publication.
- The backfill completes within the budget.
- XCom payloads contain only small references.

**What falsifies success:** duplicate gold rows or STAC items after a replay, or business logic only reachable through Airflow.

## 9. Failure and Blocker Handling

If Airflow exceeds the memory budget, propose fewer services, LocalExecutor or SequentialExecutor for the demo, or reduced parallelism. The user decides.

## 10. State and Completion Report

Update project state with the demo evidence and the commands used.

## 11. Handoff

- Suggested commit subject (propose only): `feat(orchestration): add Airflow DAGs with safe publication and recovery`
- Next prompt: `14-quality-and-validation-gates.prompt.md`. Do not run it automatically.
