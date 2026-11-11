---
description: "Stage 14: Consolidate executable quality contracts and promotion gates across bronze, silver and gold, and prove that bad data cannot reach serving."
agent: "agent"
---

# Stage 14: Quality and Validation Gates

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md`
- `docs/data-model.md`
- The contract files
- `docs/measurement-spec.md`
- The evaluation reports
- The existing tests and checks from Stages 08–13

**Prerequisites:** Stages 01–13 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** consolidate the existing per-stage checks into auditable, layered quality contracts and promotion gates, and wire them into the publication gate.

**Non-goals:**
- Writing the first tests for earlier stages. Those tests must already exist. If any are missing, report this as a gap in that stage.
- Replacing working checks with a new framework without approval.

## 2. Domain-learning Objective

Explain the geospatial quality dimensions:

- Geometry validity
- CRS and alignment
- Valid-pixel coverage
- Physically plausible ranges, such as reflectance and index bounds
- Temporal coverage
- Source drift, such as baseline changes and collection version changes

Explain also why missing evidence must be distinguished from no change.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Quality tooling:**
   - (a) Extend the existing pytest-style checks plus a small check registry in the package. This option is recommended because it adds no new dependency.
   - (b) Adopt a data-quality framework, such as Great Expectations, Soda or pandera. Verify that it fits the stack.
   - (c) A hybrid.
2. **Severity and actions:** for each check family, decide what triggers **warn**, **fail (block promotion)** and **quarantine (isolate and continue)**.
3. **Thresholds:** for example, the minimum valid coverage per window, the alignment tolerance and the drift detection rules. These start as proposed targets and require approval.
4. **Audit storage:** where to persist quality results, according to the Stage 06 quality-results entity, and how to show them in serving.

## 4. Evidence Plan

Run the candidate checks over the existing outputs, and report their pass, warn and fail rates before the user approves the thresholds.

## 5. Approval Gate

Get approval for the tooling, severities, thresholds and audit storage before you implement.

## 6. Work Steps

1. Build an inventory of the existing checks per layer and identify the gaps.
2. Implement or extend the checks to cover these areas:
   - Spatial validity
   - Completeness and coverage
   - Alignment
   - Ranges
   - Schema
   - Duplicates and key uniqueness
   - Temporal coverage
   - Source drift
   - Analytical evaluation thresholds
3. Persist the results with the `run_id`, the check ID, the severity, the outcome, the observed value and the threshold.
4. Wire the gates into the bronze-to-silver and silver-to-gold promotion and into the Airflow publish step:
   - A failure blocks promotion.
   - Quarantined data goes to a quarantine location.
   - Products with insufficient evidence are marked, not published as zero change.
5. **Bad-input proof:** inject deliberately bad inputs, such as a misaligned raster, an invalid geometry, an all-nodata window and a schema drift. Show that each one is blocked or quarantined and never reaches serving.
6. Write `docs/quality.md`, covering the contracts, gates, severities, the audit query examples and the bad-input proof.

## 7. Deliverables

- The checks
- The gate wiring
- The quality results table
- `docs/quality.md`
- Tests
- Updates to project state

## 8. Acceptance Checks

- Every bad-input case is blocked or quarantined, and the evidence is recorded.
- Every gate result is queryable by `run_id`.
- No gold record exists with unknown coverage.

**What falsifies success:** any bad input visible in serving or STAC, or zero change published for an unobserved area.

## 9. Failure and Blocker Handling

If a gate would block most real data, report the measurements. Let the user choose whether to adjust the method, the threshold or the scope.

## 10. State and Completion Report

Update project state and the traceability for the quality requirements.

## 11. Handoff

- Suggested commit subject (propose only): `feat(quality): add layered quality gates with quarantine and audit results`
- Next prompt: `15-stac-api-and-analyst-serving.prompt.md`. Do not run it automatically.
