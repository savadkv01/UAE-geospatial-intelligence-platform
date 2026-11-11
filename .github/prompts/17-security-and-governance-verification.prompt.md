---
description: "Stage 17: Verify the approved security and governance controls with scanning, configuration review, lineage queries and an honest residual-risk report."
agent: "agent"
---

# Stage 17: Security and Governance Verification

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/governance-security.md` (control-to-check table)
- `docs/source-register.md`
- `docs/serving.md`
- The Compose files
- The repository contents

**Prerequisites:** Stages 01–16 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** audit and verify every control approved in Stage 07. Most controls should already be built into earlier stages. Close the gaps and document the residual risks.

**Non-goals:**
- Introducing new security architecture without approval.
- Penetration testing beyond the local scope.
- Legal certification.

## 2. Domain-learning Objective

Explain the following:

- Why STAC metadata and fixtures can leak signed URLs or restricted data.
- How licence notices for derived geospatial data differ from code licence files.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Scanning tools:** choose from open-source candidates such as gitleaks or trufflehog for secrets, pip-audit or osv-scanner for dependencies, and Trivy or Grype for images. Verify their current status, and ask before installing anything.
2. **Severity policy:** decide which findings block, which are accepted with justification, and which are deferred to the backlog.
3. **Residual-risk acceptance:** the user explicitly accepts or rejects each residual risk.

## 4. Evidence Plan

Run the approved scanners over the repository, the dependencies and the images. Record the tool versions, commands and summarized results, and never paste secret values.

## 5. Approval Gate

Get approval for the tools, the installation and the severity policy before scanning. Get approval again before remediation that changes any public contract.

## 6. Work Steps

1. Walk the Stage 07 control-to-check table and run each check. Record pass, fail or not-implemented, with evidence. Cover these areas:
   - Credential redaction
   - Bind addresses
   - Least privilege, including database roles and container users
   - Service separation
   - Licence notices and attribution
   - Lineage queries, such as tracing a gold record back to its bronze assets
   - Retention and deletion safeguards that protect provenance
2. Review the public STAC links, the fixtures, the documentation and the screenshots for credential leakage or restricted data.
3. Remediate the approved findings with focused changes and tests.
4. Write `docs/security-verification.md` with the control results, scan summaries, remediations and **residual risks**, including the user's acceptance decisions.

## 7. Deliverables

- Scan outputs, summarized
- Remediations
- `docs/security-verification.md`
- Updates to project state

## 8. Acceptance Checks

- No unresolved blocking findings remain.
- Every control has evidence.
- The lineage query succeeds end to end.
- No secret is found in tracked files or published metadata.

**What falsifies success:** a passing claim without evidence, or a control first introduced here that should have existed earlier and is not flagged as such.

## 9. Failure and Blocker Handling

If a tool cannot be installed or run, record the gap and offer manual alternatives. Do not claim coverage that was not achieved.

## 10. State and Completion Report

Update project state and the Stage 07 control statuses.

## 11. Handoff

- Suggested commit subject (propose only): `chore(security): verify governance controls and document residual risks`
- Next prompt: `18-performance-and-resource-finops.prompt.md`. Do not run it automatically.
