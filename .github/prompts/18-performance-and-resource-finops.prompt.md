---
description: "Stage 18: Measure actual resource use per unit of work, benchmark optimizations, and add budget guardrails and safe cleanup."
agent: "agent"
---

# Stage 18: Performance and Resource FinOps

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/feasibility-pilot.md` (budgets)
- `docs/architecture.md`
- `docs/governance-security.md` (retention)
- The benchmark reports
- The metrics from Stage 16

**Prerequisites:** Stages 01–17 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:**
- Measure the resource use of the agreed workloads: downloaded bytes, disk growth, wall time, CPU time and peak memory.
- Normalize each measure per meaningful unit, for example, per km² per observation window.
- Benchmark the selected optimizations.
- Add guardrails and safe cleanup.

**Non-goals:**
- Inventing cloud bills.
- Treating hypothetical cloud estimates as actual costs.
- Treating wall time as CPU time.

## 2. Domain-learning Objective

Explain the following:

- How AOI area, resolution, band selection, window count and COG overviews drive cost.
- Why cache locality and chunk alignment with COG internal tiles matter.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Workloads to measure:** for example, one full window end to end, an incremental rerun and a backfill of N windows.
2. **Optimization candidates to benchmark:** choose at most 2–3, for example:
   - Remote windowed reads versus a full download
   - Chunk size and tiling
   - Partition granularity
   - Cache retention
3. **Guardrails:**
   - The maximum download per run.
   - The disk high-water mark.
   - Whether to abort or only warn.
   - The cleanup policy and protected paths. Bronze manifests and provenance are never auto-deleted.
4. **Hypothetical cloud estimate:** decide whether to include it. If so, it must be clearly labelled hypothetical, with a cited pricing source and access date.

## 4. Evidence Plan

Use reproducible measurement commands, such as `/usr/bin/time -v`, `docker stats`, `du`, and process CPU time from the metrics. Run each measurement at least twice and report the variance.

## 5. Approval Gate

Get approval for the workloads, benchmarks and guardrail design before running long measurements or implementing guardrails.

## 6. Work Steps

1. Measure the baseline workloads and record the hardware and versions.
2. Run the approved benchmarks under the same conditions. Adopt an optimization only after the user approves it based on the results.
3. Implement the guardrails, such as pre-run budget checks from the dry-run estimates, and safe cleanup with dry-run mode and protected-path tests.
4. Write `docs/resource-economics.md` with these sections: units, measurements, benchmarks, adopted changes, guardrails, the cleanup policy and an optional, clearly separated hypothetical cloud estimate.

## 7. Deliverables

- Measurement scripts and records
- The guardrail and cleanup code with tests
- `docs/resource-economics.md`
- Updates to project state

## 8. Acceptance Checks

- Every reported number has a command and an environment.
- The cleanup dry-run test proves that protected paths survive.
- A guardrail triggers on a simulated over-budget run.
- CPU time and wall time are reported separately.

**What falsifies success:** invented costs, a single-run number presented as stable, or cleanup that can delete provenance.

## 9. Failure and Blocker Handling

If a measurement is not possible on the platform, for example, because a tool is missing on Windows, use an alternative such as Docker or the WSL2 tooling, or mark the measurement `not measured`.

## 10. State and Completion Report

Update project state with the measured unit costs and the adopted guardrails.

## 11. Handoff

- Suggested commit subject (propose only): `perf: measure unit resource costs and add budget guardrails`
- Next prompt: `19-end-to-end-and-reproducibility.prompt.md`. Do not run it automatically.
