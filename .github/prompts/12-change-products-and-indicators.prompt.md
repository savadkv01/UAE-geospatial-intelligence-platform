---
description: "Stage 12: Deliver the approved change products and indicators in prioritized increments, each with a measurement contract, controls and evaluation."
agent: "agent"
---

# Stage 12: Change Products and Indicators

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md` (capability priority and analytical criteria)
- `docs/measurement-spec.md`
- `docs/feasibility-pilot.md` (control and change sites)
- `docs/data-model.md`
- `docs/governance-security.md` (label publication rules)
- The Stage 10 and Stage 11 outputs

**Prerequisites:** Stages 01–11 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** deliver the gold products **one increment at a time**, in the approved priority order. Each product must have user acceptance before the next product starts.

The products are:
1. Vegetation baseline and change
2. Surface-water extent baseline and change
3. Candidate urban expansion
4. Broad coastal change
5. Multi-year environmental indicators

**Non-goals:**
- Causal attribution
- Parcel or building-level claims
- Treating the products as authoritative ground truth

## 2. Domain-learning Objective

For each increment, explain the following:

- How the index and the threshold or classification work.
- Why persistence rules reduce false positives.
- How to estimate uncertainty.
- Why same-source visual review is **not** independent ground truth.
- The increment-specific caveats:
  - GHSL interpolated or projected epochs are not observations.
  - OSM edit dates are not construction dates.
  - A tide-affected shoreline is not erosion.
  - Irrigation cycles are not land-cover change.

## 3. Decision Checkpoints (per Product Increment)

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Product method:** for example, for water:
   - (a) A fixed MNDWI threshold.
   - (b) A per-window adaptive threshold, such as Otsu.
   - (c) Optical plus SAR agreement.

   Show each option's error modes in Abu Dhabi conditions.
2. **Change rule and persistence:** the minimum magnitude, the number of consecutive windows required and the minimum mapping unit, in cells or m².
3. **Masks and exclusions:** for example, the intertidal zone, active construction sites flagged separately, and permanent water.
4. **Evaluation design:**
   - Controls: the stable and change sites from Stage 04.
   - A held-out labelled sample, if labels can be created. Define who labels, which imagery they use and how independence is limited.
   - Metrics: for example, precision and recall for candidates, and the stability of the controls.
   - Publication of labels under the Stage 07 rules.

## 4. Evidence Plan

Before the full run, run the method on the control and change sites. Report the measured results, including the failures, before asking the user to accept the thresholds.

## 5. Approval Gate

For each increment, get approval for the method, the rule and the evaluation plan before implementing. Then get **product acceptance** before you start the next increment.

## 6. Work Steps (Repeat per Increment)

1. Write or update the product's **measurement contract** in `docs/measurement-spec.md` and `docs/methodology/<product>.md`. Cover:
   - Inputs
   - Formula
   - Masks
   - Thresholds and persistence
   - Units
   - Uncertainty fields
   - Cannot-claim statements
2. Implement the reusable product functions in the package, and the gold tables and rasters according to the Stage 06 contracts. The gold outputs include:
   - Valid coverage
   - Confidence and uncertainty
   - An `insufficient_evidence` status, used instead of zero change when coverage is too low
3. Write tests with fixtures:
   - Known-change and no-change synthetic cases
   - All-masked windows producing `insufficient_evidence`
   - Threshold edges
   - Persistence logic

   Run the first test immediately.
4. Run the method on the approved scope and evaluate it against the controls and held-out labels. Write `docs/evaluation/<product>.md` with the measured metrics, confusion examples, limitations and the independence caveats.
5. Record ADRs for the methods and thresholds, and update the traceability.

## 7. Deliverables

For each product:
- Methodology document
- Code and tests
- Gold outputs
- Evaluation report
- ADRs
- Updates to project state

## 8. Acceptance Checks

- The tests pass.
- The controls stay within the approved tolerance.
- The evaluation metrics are computed from recorded labels with a recorded procedure.
- Low-coverage areas are marked `insufficient_evidence`.
- The product documentation includes the cannot-claim statements.

**What falsifies success:** zero change published for masked areas, same-source review called ground truth, GHSL epochs treated as observations, or metrics without labels.

## 9. Failure and Blocker Handling

If a product fails its criteria, present the options: revise the method, narrow the scope, mark the product experimental, or defer it to the backlog. The user decides, and the decision is recorded in an ADR.

## 10. State and Completion Report

Update the per-product status in project state. The stage is complete only when all MVP products are accepted or explicitly deferred.

## 11. Handoff

- Suggested commit subject per increment (propose only): `feat(products): add <product> with evaluation and measurement contract`
- Next prompt: `13-airflow-orchestration-and-recovery.prompt.md`. Do not run it automatically.
