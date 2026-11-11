---
description: "Stage 07: Agree the threat model, data classification, licensing, lineage, retention and credential controls as implementable acceptance checks."
agent: "agent"
---

# Stage 07: Governance and Security Design

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md`
- `docs/source-register.md`
- `docs/architecture.md`
- `docs/data-model.md`

**Prerequisites:** Stages 01–06 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** design governance and security controls that are concrete enough to implement and test from Stage 08 onward.

**Non-goals:**
- Implementing scanners. Stages 08 and 17 do this.
- Legal advice. Flag questions that need the user's own judgement.

## 2. Domain-learning Objective

Explain the following:

- **Copernicus Sentinel data terms:** attribution requirements.
- **GHSL terms.**
- **OSM:** OSM data is under ODbL. A derived **database** carries share-alike obligations that differ from those for a produced work. These obligations are separate from the code licence.
- **Satellite-derived change at sensitive sites:** why publishing it can raise ethical considerations, even with open data.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Exposure model:**
   - (a) All services bound to localhost, with a public repository but no public service. This option is recommended.
   - (b) An optional demo exposed on the LAN.
   - (c) A public demo later. This would require a separate review.
2. **Data classification and publication:** classify each dataset class as one of the following:
   - Public: code and small fixtures.
   - Shareable with attribution.
   - Local-only: bulk imagery, OSM-derived databases and user labels.

   Also decide whether **user-reviewed labels and reference evidence** may be published, and in which form.
3. **Credentials:**
   - Which providers need credentials.
   - Storage: an untracked `.env` file versus Docker secrets versus an OS keychain.
   - Rotation and revocation steps.
   - Redaction in logs.
4. **Retention and deletion:**
   - Policies per layer.
   - Protected provenance: bronze manifests are never auto-deleted.
   - Reproducibility guarantees, such as pinned code and config hashes per run.

Additional topics to cover in a later interaction:
- Access roles: local admin, analyst read-only and service accounts.
- Dependency and image provenance policy.

## 4. Evidence Plan

Cite the official licence texts and attribution guidance, with access dates. If a term is ambiguous, record it as an open question. Do not interpret it as permission.

## 5. Approval Gate

Present a STRIDE-style threat-model summary and the control list. Get approval for each material decision before writing.

## 6. Work Steps

1. Create `docs/governance-security.md` with:
   - Threat model, covering assets, trust boundaries, threats and mitigations.
   - Data classification table.
   - Licence and attribution matrix, covering data versus code.
   - Lineage and reproducibility requirements.
   - Retention and deletion rules.
   - Roles.
   - Credential lifecycle.
   - Logging and redaction rules.
   - Dependency and image policy.
   - Residual risks.
2. For each control, add an **acceptance check** that a later stage can run. Example: "No service binds 0.0.0.0. The check inspects the Compose ports." Assign each check to an owning stage.
3. Update the Stage 06 contracts if lineage fields are missing. If this is a material change, ask first.
4. Record ADRs.

## 7. Deliverables

- `docs/governance-security.md` with a control-to-check-to-stage table
- ADRs
- Updates to project state

## 8. Acceptance Checks (Document Review)

- Every control has a testable check and an owner stage.
- The OSM database licence is treated separately from the code licence.
- No credential values appear anywhere.

**What falsifies success:** policy prose without checks, or an implied permission to republish third-party data.

## 9. Failure and Blocker Handling

For any licence question that the user is not comfortable answering, the default is to keep the data local-only and record an open question.

## 10. State and Completion Report

Update project state. List the controls that Stage 08 must implement from the start.

## 11. Handoff

- Suggested commit subject (propose only): `docs: add governance and security design with testable controls`
- Next prompt: `08-repository-and-local-infrastructure.prompt.md`. Do not run it automatically.
