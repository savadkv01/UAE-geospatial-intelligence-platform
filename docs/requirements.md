# Business Requirements

- Status: Approved by the user on 2026-11-11.
- Stage: 01 — Business requirements
- Date: 2026-11-11

## Context

- **Verified (shared workflow contract, read 2026-11-11):** this is a public Abu Dhabi geospatial pilot with five candidate capabilities: vegetation change, surface-water extent change, candidate urban expansion, broad coastal change, and multi-year environmental indicators.
- **Approved decision:** frame the product as an analyst-facing monitoring tool with an engineering showcase.
- **Approved decision:** deliver batch analyses by observation window. The exact window (for example, monthly or seasonal) remains open for later evidence and approval.
- These requirements do not select an AOI, dates, sources, algorithms, or architecture.

## Personas

| Persona | Need | Status |
| --- | --- | --- |
| Geospatial analyst (primary) | Review and interpret candidate change signals and their coverage and uncertainty. | Approved audience; workflow details remain an assumption. |

Other stakeholders, such as planning/environment reviewers and engineering or portfolio reviewers, are candidates to validate, not approved primary personas.

## Analyst Workflow

**Assumption A-01 (to validate in Stage 02):** an analyst discovers a product for an observation window, reviews its candidate signal and valid-data coverage, compares it with other windows, and interprets it alongside reference evidence. Product interaction and any annotation workflow are not yet specified.

## Business Questions

The platform should help analysts investigate, not assert as ground truth:

1. Where are candidate signals of urban expansion?
2. Where and when has vegetation potentially changed?
3. Where and when has surface-water extent potentially changed?
4. Where are broad coastal-change signals that warrant review?
5. How do selected environmental indicators vary across multiple years?

## Capability Priority

| Priority | Capability | Increment |
| --- | --- | --- |
| 1 | Candidate urban expansion | MVP |
| 2 | Vegetation change | MVP |
| 3 | Surface-water extent change | Later increment |
| 4 | Broad coastal change | Later increment |
| 5 | Multi-year environmental indicators | Later increment |

This ordering and MVP set are user-approved. Urban expansion is a candidate signal with known potential confounders in arid and coastal settings; its feasibility and interpretation must be evaluated before making claims.

## MVP

- Analyst-facing monitoring narrative with an engineering showcase.
- Batch products by observation window; the exact window is deferred.
- Candidate urban-expansion and vegetation-change capabilities.
- Present outputs as signals for analyst interpretation, with their coverage and uncertainty made visible.

## Later Increments

The first MVP defers surface-water extent change, broad coastal change, and multi-year environmental indicators. Their deferral is not a rejection.

## Non-goals

- No parcel-level claims.
- No real-time alerting.
- No causal attribution.
- No claims that satellite-derived outputs are equivalent to ground truth.
- No unsupported assertion that a candidate signal is a confirmed change.

## Reliability Criteria

Reliability describes dependable platform behavior (such as freshness, idempotency, recovery, and lineage), not whether an analytical result is correct.

| ID | Kind | Proposed target | Verification evidence |
| --- | --- | --- | --- |
| AC-01 | Reliability | A rerun with the same inputs and configuration produces zero duplicate published products. | Repeat-run evidence and a duplicate check over product identifiers. |
| AC-02 | Reliability | A failed task can be recovered, demonstrated by a controlled failure followed by a successful recovery. | Run/task history and verification that output state is consistent. |
| AC-03 | Reliability | A freshness deadline is defined and measured for the chosen observation-window cadence. The deadline is **to be determined** after operational constraints are understood. | Agreed deadline and timestamp evidence for a representative run. |

AC-01 and AC-02 are user-approved **proposed targets**, not verified platform performance. AC-03's target value is deferred.

## Analytical Criteria

Analytical accuracy describes agreement with reference evidence; it is distinct from platform reliability. Satellite-derived change is a candidate signal that can be affected by observation conditions, seasonality, and other confounders. It requires interpretation and must not be presented as a fact or a causal explanation.

| ID | Kind | Proposed target | Verification evidence |
| --- | --- | --- | --- |
| AC-04 | Analytical | Evaluate candidate outputs against labelled reference evidence using suitable agreement metric(s). The specific reference source, metric selection, and numeric threshold are **to be determined in Stage 12**. | Evaluation report identifying the reference evidence, metric definitions, sample, and results. |
| AC-05 | Analytical | Report valid-observation coverage as a fraction of the AOI for each evaluated product/window, and report relevant uncertainty or limitations. The minimum acceptable coverage threshold is **to be determined in Stage 12**, informed by earlier profiling and feasibility evidence. | Per-product coverage and uncertainty metadata, plus a check against the subsequently approved threshold. |

AC-04 and AC-05 are user-approved **proposed target frameworks**, not claims of achieved accuracy. “Accurate change detection” without a metric, reference evidence, and coverage condition is not an acceptable success criterion.

## Assumptions and Open Questions

| ID | Item | Owner / resolution point | Status |
| --- | --- | --- | --- |
| A-01 | Validate the analyst workflow and whether secondary stakeholder personas are needed. | Stage 02 | Assumption |
| OQ-01 | Select the observation-window length and define freshness expectations using source and runtime evidence. | Stages 03, 13, 18 | Deferred |
| OQ-02 | Select reference evidence, suitable agreement metrics, and numeric analytical and coverage thresholds. | Stage 12, informed by Stages 03–04 | Deferred |

## Requirement-to-Stage Traceability

Statuses distinguish approved requirements and proposed targets from assumptions and items deferred for later evidence.

| Requirement ID | Description | Owning stage(s) | Evidence expected | Status |
| --- | --- | --- | --- | --- |
| BR-01 | Serve an analyst-facing monitoring use case with an engineering showcase. | 05, 15, 20 | Architecture and analyst-serving design aligned with the approved audience; portfolio narrative. | Approved |
| BR-02 | Preserve the user-approved priority order and represent all five capabilities as MVP or deferred. | 02, 04, 12, 15 | Domain definitions, feasibility decision, product coverage, and analyst catalogue. | Approved |
| BR-03 | Process by observation window; determine the exact window and freshness expectation using evidence. | 03, 05, 08, 09, 13, 18, 19 | Source cadence profile, architecture/orchestration configuration, and measured run evidence. | Approved; window deferred |
| BR-04 | Present satellite-derived change as a candidate signal requiring interpretation, not a fact or causal claim. | 02, 12, 14, 15, 20 | Domain definitions, product limitations, quality checks, and user-facing explanations. | Approved |
| BR-05 | Include candidate urban expansion and vegetation change in the MVP; defer the other three capabilities. | 04, 12 | Feasibility evidence and MVP product evaluation. | Approved |
| BR-06 | Exclude parcel-level claims, real-time alerting, causal attribution, and ground-truth equivalence claims. | 07, 12, 15, 20 | Governance constraints, analytical outputs, serving behavior, and documentation. | Approved |
| A-01 | Validate analyst workflow details and secondary personas. | 02, 15, 20 | Confirmed workflow/persona needs and serving design. | Assumption |
| AC-01 | Same-input/configuration rerun produces zero duplicate published products. | 08, 13, 14, 19 | Repeat-run and duplicate-check evidence. | Proposed target |
| AC-02 | Demonstrate recovery from a controlled task failure with consistent output state. | 08, 13, 14, 16, 19 | Failure/recovery run history and output consistency check. | Proposed target |
| AC-03 | Define and measure a freshness deadline for the selected cadence. | 03, 13, 16, 18 | Approved deadline and timestamp evidence. | Deferred |
| AC-04 | Evaluate candidate outputs against labelled reference evidence using suitable agreement metrics. | 02, 03, 04, 12, 14 | Evaluation report with source, sample, metric definitions, and results. | Proposed target; specifics to Stage 12 |
| AC-05 | Report valid-observation coverage and uncertainty; assess against a later-approved threshold. | 02, 04, 10, 12, 14, 15 | Per-product coverage/uncertainty metadata and threshold check. | Proposed target; threshold to Stage 12 |

## Decision Records

- [ADR 0001 — Audience and MVP priorities](decisions/0001-audience-and-mvp-priorities.md)
- [ADR 0002 — Batch observation-window cadence](decisions/0002-batch-observation-window-cadence.md)
- [ADR 0003 — Acceptance target frameworks and non-goals](decisions/0003-acceptance-target-frameworks-and-non-goals.md)
