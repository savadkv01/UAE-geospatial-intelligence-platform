---
description: "Stage 20: Polish the documentation and portfolio narrative from the implemented reality, measured results and honest limitations."
agent: "agent"
---

# Stage 20: Documentation and Portfolio Story

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- All files in `docs/`
- The root `README.md`, if present
- The Compose files
- The package layout

**Prerequisites:** Stages 01–19 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** make the repository understandable and credible to reviewers in 5 minutes, and usable by developers in 30 minutes. Base everything on what is actually implemented and measured.

**Non-goals:**
- Inventing achievements, metrics, users or endorsements.
- Adding features.
- Claiming employer affiliation.

## 2. Domain-learning Objective

Explain how to present EO results responsibly:

- Uncertainty and coverage
- Attribution
- Cannot-claim statements
- The difference between a candidate signal and a confirmed change

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **README narrative structure:**
   - (a) Problem, solution, architecture, results, engineering trade-offs and quickstart. This option is recommended for hiring reviewers.
   - (b) Quickstart-first developer README with a separate portfolio page.
   - (c) Custom.
2. **Visual evidence:** which small screenshots or GIFs to include. Each must be lawful with attribution, and generated from real outputs.
3. **Documentation layout:** keep the existing `docs/` structure, or consolidate it. Prefer updating existing documents over creating duplicates.

## 4. Evidence Plan

Collect the measured results only from the existing evidence documents, such as the feasibility, evaluation, resource-economics and end-to-end reports.

## 5. Approval Gate

Get approval for the outline and the visual-evidence list before writing.

## 6. Work Steps

1. Update the root `README.md`. Cover:
   - The business value
   - The capabilities, with their status and limitations
   - The architecture diagram
   - Key measured results
   - Senior trade-offs, including what was deferred and why
   - A quickstart (tiny demo)
   - Attribution
2. Ensure that these documents exist and are current, updating rather than duplicating:
   - Developer guide
   - Data dictionary (from the contracts)
   - Source register
   - Methodology
   - ADR index
   - Runbooks
   - Limitations
   - Mermaid architecture diagrams
3. Check that every documented command runs, or mark it with the conditions it needs.
4. Check that all relative links resolve and that the Mermaid diagrams render.
5. Check the consistency between the architecture and the code: every documented component exists, and every major module is documented.

## 7. Deliverables

- The updated README and documentation
- Screenshots or GIFs (small and lawful)
- A link-check result
- Updates to project state

## 8. Acceptance Checks

- The link check passes.
- The documented commands have been executed, or carry a stated condition.
- Every metric in the README traces to an evidence document.
- Attribution is present.
- The limitations section exists and is specific.

**What falsifies success:** any number without a source document, a broken link, or a component in the documentation that does not exist in the code.

## 9. Failure and Blocker Handling

If evidence for a claim is missing, remove or qualify the claim. Do not create evidence retroactively without actually running the work.

## 10. State and Completion Report

Update project state with the documentation checks run.

## 11. Handoff

- Suggested commit subject (propose only): `docs: polish README, guides and portfolio narrative from measured results`
- Next prompt: `21-github-release-and-handover.prompt.md`. Do not run it automatically.
