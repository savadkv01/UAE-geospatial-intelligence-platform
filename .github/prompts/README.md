# Prompt Pack: UAE Geospatial Intelligence & Urban Change Monitoring Platform

This folder contains a phase-by-phase VS Code GitHub Copilot prompt pack for building the platform interactively. Each stage prompt can run on its own in a fresh Copilot Agent chat. Every stage reads the shared contract and the project state, asks you to make the material decisions and waits for your approval before it implements anything.

- Shared contract: [geospatial-workflow.instructions.md](../instructions/geospatial-workflow.instructions.md)
- Project state: [project-state.md](../../docs/project-state.md)
- Decision records: [docs/decisions](../../docs/decisions/README.md)
- Generator, kept for regeneration: [00-generate-project-workflow.prompt.md](00-generate-project-workflow.prompt.md)

## How to Invoke a Stage

1. Open a **new** Copilot Chat in **Agent** mode.
2. Do one of the following:
   - Type `/` and pick the stage prompt, for example `/01-business-requirements`.
   - Run **`Chat: Run Prompt...`** from the Command Palette and select the file.
3. The agent checks the prerequisites. It then explains the stage and asks 2–4 option-based questions at a time.
4. Answer the questions, approve the plan, review the diffs, and accept the stage outcome.

## Stage Sequence

Each stage depends on all earlier stages being `complete`, unless you explicitly waive a prerequisite. The **effort figures are rough estimates** for a part-time learner, not commitments.

| # | Prompt | Main outputs | Est. effort |
| --- | --- | --- | --- |
| 01 | [Business requirements](01-business-requirements.prompt.md) | `docs/requirements.md`, traceability table | 0.5–1 day |
| 02 | [Domain and measurement](02-domain-and-measurement.prompt.md) | glossary, measurement spec | 1–2 days |
| 03 | [Source discovery and profiling](03-source-discovery-and-profiling.prompt.md) | source register, profiling report | 1–3 days |
| 04 | [AOI and feasibility pilot](04-aoi-and-feasibility-pilot.prompt.md) | AOI file, pilot report, go/no-go | 2–4 days |
| 05 | [Solution and data architecture](05-solution-and-data-architecture.prompt.md) | architecture doc, Mermaid diagrams, ADRs | 1–3 days |
| 06 | [Data modelling and contracts](06-data-modelling-and-contracts.prompt.md) | data model, contracts, mappings | 1–3 days |
| 07 | [Governance and security design](07-governance-and-security-design.prompt.md) | threat model, controls with checks | 1–2 days |
| 08 | [Repository and local infrastructure](08-repository-and-local-infrastructure.prompt.md) | package skeleton, Compose, setup runbook | 2–4 days |
| 09 | [Source ingestion and bronze](09-source-ingestion-and-bronze.prompt.md) | adapters, manifests, tests | 3–5 days |
| 10 | [Raster standardization and silver](10-raster-standardization-and-silver.prompt.md) | masking/compositing modules, silver COGs | 3–6 days |
| 11 | [Spatial transformation and lakehouse](11-spatial-transformation-and-lakehouse.prompt.md) | Sedona jobs, tables, benchmark | 3–5 days |
| 12 | [Change products and indicators](12-change-products-and-indicators.prompt.md) | per-product methods, gold outputs, evaluations | 5–15 days |
| 13 | [Airflow orchestration and recovery](13-airflow-orchestration-and-recovery.prompt.md) | DAGs, recovery and backfill evidence | 2–4 days |
| 14 | [Quality and validation gates](14-quality-and-validation-gates.prompt.md) | quality gates, quarantine, bad-input proof | 2–4 days |
| 15 | [STAC API and analyst serving](15-stac-api-and-analyst-serving.prompt.md) | local STAC items, analyst view | 3–5 days |
| 16 | [Observability and runbooks](16-observability-and-operational-runbooks.prompt.md) | logs, metrics, alerts, runbooks | 2–3 days |
| 17 | [Security and governance verification](17-security-and-governance-verification.prompt.md) | scans, control evidence, residual risks | 1–3 days |
| 18 | [Performance and resource FinOps](18-performance-and-resource-finops.prompt.md) | unit costs, guardrails, cleanup | 2–3 days |
| 19 | [End-to-end and reproducibility](19-end-to-end-and-reproducibility.prompt.md) | network-free demo, e2e evidence | 2–4 days |
| 20 | [Documentation and portfolio story](20-documentation-and-portfolio-story.prompt.md) | README, guides, diagrams | 2–3 days |
| 21 | [GitHub release and handover](21-github-release-and-handover.prompt.md) | readiness report, licence, checklist, backlog | 1–2 days |

## Approval Process

- The agent asks about every material business, domain, data, architecture, infrastructure, modelling, analytical, quality, security, governance, budget and release decision. It presents 2–4 options with a recommendation and also accepts a custom answer.
- For decisions that need evidence first, the agent proposes a bounded probe and asks your permission before running it.
- After the decisions, the agent proposes a short plan. Substantive edits, installations, downloads and long jobs start only after you approve that plan.
- Approved decisions become ADRs in `docs/decisions/`. Changing an earlier decision supersedes its ADR and invalidates the affected downstream approvals.
- A stage becomes `complete` only when its acceptance checks pass **and** you accept the outcome.

## Resuming

Start a fresh chat and run the stage that `docs/project-state.md` lists as active. The agent resumes from the recorded state and the repository evidence, not from earlier chat history. If you revise an earlier decision, rerun that stage's prompt.

## Git Policy (selected)

**No Git operations unless you specifically ask for them.** At the end of each stage, the agent proposes a truthful commit subject and the exact files to stage. It runs `git init`, commits, merges, branches, tags or pushes only when you explicitly request that operation. It never uses `git add .`, backdates commits or rewrites history.

## Important Limitation

These prompts and instructions **guide** the agent's behavior. They are **not a technical permission boundary**. Keep VS Code tool-approval prompts enabled, especially for terminal, Git and network operations, and review every diff before accepting it.
