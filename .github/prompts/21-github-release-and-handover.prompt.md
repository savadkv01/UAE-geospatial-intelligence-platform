---
description: "Stage 21: Run the publication-readiness review, agree licensing and release metadata, and hand over with a final evidence checklist and backlog."
agent: "agent"
---

# Stage 21: GitHub Release and Handover

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md), especially its Git policy
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md`
- `docs/security-verification.md`
- `docs/e2e-validation.md`
- The README and the documentation set

**Prerequisites:** Stages 01–20 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:**
- Confirm that the repository is safe and ready to publish.
- Agree the licensing and release metadata.
- Hand over a final evidence checklist and a prioritized backlog.

**Non-goals:**
- Pushing, tagging, creating a remote or publishing a release without explicit, operation-specific authorization.
- Rewriting history.

## 2. Domain-learning Objective

Explain why the code licence (for example, MIT or Apache-2.0) is independent of the source-data terms (Copernicus, GHSL and ODbL), and how to state both clearly.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Code licence:**
   - (a) Apache-2.0, which includes a patent grant.
   - (b) MIT.
   - (c) Another licence.

   This is a separate decision from the data terms. The user must choose; the agent does not.
2. **Repository metadata:** the name, description, topics and social preview. The agent proposes them and the user approves.
3. **Release scope:** the version number (for example, `v0.1.0`), the release-notes content and the included artifacts (code only, no bulk data).
4. **Remote operations:** for each operation the user wants, such as creating the remote, pushing, tagging or creating a GitHub release, the user gives explicit authorization. Otherwise, provide manual steps.

## 4. Evidence Plan

Run the publication-readiness checks:

- Secret scan
- Large-file scan (tracked file sizes)
- Data and dependency licence review
- Reproducibility from the Stage 19 evidence
- CI status, if CI exists
- Documentation link check

## 5. Approval Gate

Present the readiness report. Get explicit approval for each of the following:
- The licence choice
- The metadata
- Each Git or remote operation, under the user-selected Git policy: no Git operations unless the user specifically asks to commit or merge, and the same rule applies to pushes, tags and releases.

## 6. Work Steps

1. Run the readiness checks and write `docs/release-readiness.md`.
2. With approval, add the `LICENSE` file and a data-attribution section or `NOTICE` file.
3. Review the incremental commit history with `git --no-pager log`. Report any history concerns honestly. Never fabricate, backdate, squash or rewrite history without explicit permission.
4. Draft the release notes and a concise portfolio narrative, using only the measured and verified claims.
5. Perform only the Git or remote operations that the user explicitly requested. If tooling or authentication is unavailable, provide exact manual steps instead.
6. Produce the **final requirement/evidence checklist** from the traceability table, and a **prioritized backlog** covering the deferred capabilities, the unverified gates, the residual risks and the improvements.

## 7. Deliverables

- `docs/release-readiness.md`
- `LICENSE` and the attribution notice (after approval)
- The release notes draft
- The final checklist
- The backlog, for example, `docs/backlog.md`
- Updates to project state

## 8. Acceptance Checks

- No secrets or oversized files are tracked.
- The licence and the data terms are stated separately.
- Every requirement has a final status with evidence.
- Only the authorized Git operations were performed.

**What falsifies success:** an unrequested push, tag or release, a missing data attribution, or a checklist item marked verified without evidence.

## 9. Failure and Blocker Handling

If a check fails, stop the release and report the failure. Fix it within an approved scope, or record it in the backlog with the user's decision.

## 10. State and Completion Report

Mark all stages with their final status. Record the release status, which is either published or ready-for-manual-publish, and the backlog link.

## 11. Handoff

- Suggested commit subject (propose only): `chore(release): add licence, attribution and release readiness report`
- This is the final stage, so there is no next prompt. To start iterating from the backlog, revisit the relevant stage prompt.
