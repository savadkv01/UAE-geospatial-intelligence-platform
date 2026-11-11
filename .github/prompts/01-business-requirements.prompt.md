---
description: "Stage 01: Elicit and approve business requirements, MVP boundaries and measurable acceptance criteria for the Abu Dhabi geospatial pilot."
agent: "agent"
---

# Stage 01: Business Requirements

## Required Context

Read these files explicitly before doing anything else. A Markdown link does not guarantee that the file's full content is loaded.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md): follow all of its decision, approval-gate, safety and Git rules.
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- Any existing `docs/requirements.md` or root `README.md`. If they exist, update them; do not replace them.

This is the first stage and has no predecessor. If project state shows that this stage is already in progress or complete, summarize the recorded state and ask whether to resume, revise or stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** agree on who the platform serves, which questions it answers and what "done" means for the MVP. Make each requirement traceable to a later stage.

**In scope:**
- Personas: for example, a geospatial analyst, an urban-planning or environment reviewer, a data-platform engineer reviewing the portfolio, and a hiring manager.
- The analyst workflow, business questions and the priority order of the five capabilities: vegetation change, surface-water extent change, candidate urban expansion, broad coastal change and multi-year environmental indicators.
- MVP versus later increments, non-goals and measurable acceptance criteria.

**Non-goals:** choosing the AOI, dates, sources or architecture, designing algorithms, and writing code. Later stages own these decisions.

## 2. Domain-learning Objective

Explain the difference between **platform reliability** and **analytical accuracy**:
- Platform reliability covers properties such as freshness, idempotency, recovery and lineage.
- Analytical accuracy covers properties such as precision and recall against reference evidence.

Explain why satellite-derived "change" is a candidate signal that needs interpretation, not a fact. Explain why acceptance criteria for EO products need uncertainty and coverage terms, for example, "valid observations ≥ X% of AOI".

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Primary audience and narrative:**
   - (a) Analyst-facing monitoring tool with an engineering showcase. This is recommended because it supports both a business narrative and an engineering demonstration.
   - (b) Engineering-platform showcase with thin analytics.
   - (c) Analytics-first study with a minimal platform.
   - (d) Custom.
2. **Capability priority and MVP set:** the user ranks all five capabilities and chooses which ones are in the MVP. A recommended start is vegetation plus surface water, because their optical indices are well understood. Explain that urban expansion and coastal change carry more confounders in arid and coastal Abu Dhabi.
3. **Delivery cadence semantics:**
   - (a) Batch analysis by observation window, such as a monthly or seasonal composite.
   - (b) Near-real-time per new scene.
   - (c) Annual multi-year only.

   Explain the effect of each option on data volume and laptop runtime.
4. **Acceptance-criteria style:** compare the following two styles. Ask the user to propose or approve concrete thresholds as **proposed targets** that later stages will validate.
   - Reliability service-level objectives (SLOs), for example, a rerun produces no duplicates or a failed task recovers.
   - Analytical targets, for example, agreement with a labelled sample, with a stated reference source.

Also elicit hard non-goals. Examples include no parcel-level claims, no causal attribution and no real-time alerting.

## 4. Evidence Plan

No downloads are needed. If the user wants examples of real-world analyst questions, offer to cite public sources such as published UAE environmental and urban-planning themes, and record their access dates. Do not imply that any organisation endorses this work.

## 5. Approval Gate

Summarize the draft requirements, MVP, non-goals and acceptance criteria. Ask for explicit approval before writing `docs/requirements.md`.

## 6. Work Steps

1. Draft `docs/requirements.md` with these sections: context, personas, analyst workflow, business questions, capability priority, MVP, later increments, non-goals, reliability criteria, analytical criteria, assumptions and open questions.
2. Give every requirement a stable ID, such as `BR-01`, `NFR-01` or `AC-01`.
3. Add a **requirement-to-stage traceability table** with these columns: requirement ID, description, owning stage(s), evidence expected and status. Map every requirement to at least one of stages 02–21.
4. Record ADRs for the material choices, such as the MVP capability set, audience and cadence.

## 7. Deliverables

- `docs/requirements.md`, owned by this stage and updated by later stages only through the traceability status.
- ADRs in `docs/decisions/`.
- Updates to `docs/project-state.md`.

## 8. Acceptance Checks (Document Review)

- Every one of the five capabilities appears either in the MVP or as an explicitly deferred item.
- Each acceptance criterion is measurable and labels its kind: reliability or analytical.
- Analytical criteria name a reference-evidence approach, or mark it as "to be determined in Stage 12".
- The traceability table has no orphan requirements.
- Non-goals explicitly exclude causal claims and claims of ground-truth equivalence.

**What falsifies success:** any criterion such as "accurate change detection" without a metric, reference or coverage condition, or any requirement chosen by the agent without user selection.

## 9. Failure and Blocker Handling

If the user is unsure about a decision, record it as unresolved in project state with the options presented. Do not pick a default. If later stages reveal infeasibility, they must return here through an ADR supersession.

## 10. State, ADR and Completion Report

Update project state with the stage status, approved requirements link, unresolved decisions and next action. Report what was decided, what remains open and any assumptions.

## 11. Handoff

- Suggested commit subject (propose only; follow the Git policy): `docs: add approved business requirements and traceability`
- Next prompt: `02-domain-and-measurement.prompt.md`. Do not run it automatically.
