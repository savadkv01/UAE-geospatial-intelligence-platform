---
description: "Generate an interactive, phase-wise implementation prompt pack for the Abu Dhabi geospatial intelligence portfolio project."
agent: "agent"
---

# Generate the Project Workflow

Act as a senior geospatial data-platform architect, data engineer, and technical mentor. Create reusable VS Code GitHub Copilot prompt files for the project below. Your task is to generate the workflow, NOT to implement the application or execute its stages.

## Project Brief

- Name: UAE Geospatial Intelligence & Urban Change Monitoring Platform.
- Initial geography: a bounded Abu Dhabi pilot, not the entire emirate. Exact AOI remains a user decision informed by source coverage.
- Purpose: a public GitHub flagship portfolio demonstrating senior data engineering and practical Earth-observation knowledge for Space42-like employers. Do not claim employer endorsement or assume their internal stack.
- Capabilities: vegetation change, surface-water extent change, candidate urban expansion, broad coastal change, and multi-year environmental indicators.
- Data: only free, openly licensed data. Candidate sources are Sentinel-2 L2A, Sentinel-1 GRD, GHSL and OpenStreetMap. Verify access, licenses, quotas, coverage and product versions instead of treating candidates as commitments.
- Execution: laptop-first, open-source software, containers with Docker Compose; Windows/WSL2 compatibility. No required paid cloud services, paid imagery, proprietary GIS runtime, Kubernetes or GPU.
- Required technologies: Python, Spark, STAC API and Airflow. Explain their responsibilities and limits. Include both upstream STAC discovery and a local STAC API for published products unless the user explicitly revises this requirement.
- Engineering: medallion architecture, spatial data modelling, incremental and idempotent processing, quality, lineage, governance, security, monitoring, resource economics, reusable code and automated tests.
- Publication: clear documentation, architecture diagrams, reproducible examples and meaningful, genuinely incremental Git history.
- User: experienced data engineer learning the geospatial domain. Explain unfamiliar domain reasoning without reteaching elementary programming.

## First Interaction: Agree on the Workflow

Inspect existing repository instructions, relevant files and worktree state without changing them. Do not assume an empty repository. Preserve existing work and do not overwrite existing prompts silently.

Before generating files, ask a small first batch of questions with selectable options:

1. Workflow granularity: the recommended 21 stages below; a compact pack with explicit mappings for every listed responsibility; or a custom grouping.
2. Learning interaction: guided explanations and approval at each material decision (recommended); concise trade-offs with the same approval gates; or a custom style.
3. Git policy: propose commits only (recommended); create a commit after each explicitly approved milestone; or no Git operations.

Use the available structured question tool if supported. Otherwise present lettered options in chat and wait. Permit a custom answer. Do not run ahead while awaiting answers. Ask about naming conflicts only if they exist. Laptop specifications, AOI, dates and architecture belong to later stages, not this initial interview.

After the user answers, generate the agreed prompt pack and supporting workflow files. Do not ask the user to approve every filename or Markdown formatting choice.

## Files to Generate

Write the stage prompts into `.github/prompts/`, using the numbered names in the stage catalogue unless the user approved another grouping. Keep this generator intact. Each stage must be independently invocable in a fresh Copilot Agent chat.

Create only these additional supporting files initially:

- `.github/prompts/README.md`: invocation instructions, stage sequence/dependencies, expected outputs, approximate effort clearly labelled as estimates, approval process, resume process and Git policy. Explain that prompts guide behavior but are not a technical permission boundary.
- `.github/instructions/geospatial-workflow.instructions.md`: the shared workflow contract, with valid YAML frontmatter using `applyTo: "**"` because the approval and safety rules apply project-wide. Keep it concise. Do not duplicate or contradict existing repository instructions; integrate narrowly if an equivalent file exists.
- `docs/project-state.md`: stage status, active stage, approved requirements, unresolved decisions, evidence links, checks run, blockers and next action. Initialize all stages as not started; generation does not approve any project decisions.
- `docs/decisions/README.md`: decision-record template and index, initially without fabricated decisions.

Do not generate application code, infrastructure, sample results, populated business requirements, CI workflows, datasets or speculative architecture documents during this generator run. Later stages own those deliverables.

Every generated stage prompt must explicitly reference and instruct the agent to read the shared workflow contract, project state and relevant approved outputs. Use correct relative Markdown links from `.github/prompts/`. Do not assume that a bare file link guarantees full context loading.

## Shared Interaction and Decision Contract

Encode these rules in the shared contract and make each stage explicitly require them:

1. Start by checking prerequisites and reading relevant approved decisions. Explain the current stage's purpose, inputs and success criteria. Do not execute another stage automatically.
2. The user must participate in every material business, domain, data, architecture, infrastructure, modelling, analytical, quality, security, governance, resource-budget and release decision. Never silently choose on their behalf. Bundle tightly related choices, but do not hide several independent decisions inside one option.
3. Present two to four realistic options, the recommended option with reasons, trade-offs, impact on laptop resources and delivery, and a custom-answer option. Include a short explanation of new domain concepts. Do not fabricate alternatives just to fill a list.
4. Ask at most two to four related questions per interaction. Use a structured question tool when available; otherwise use numbered questions with lettered options. Wait for the user's answer. Never interpret silence as approval.
5. Explicitly identify decisions that require evidence first. Ask permission for a bounded, read-only or disposable feasibility experiment; report measurements before asking the user to select the long-term approach. An experiment does not approve its architecture.
6. Propose a short implementation plan after decisions are resolved. Obtain explicit plan approval before substantive edits, installations or long-running jobs. Permission to start a stage permits its read-only discovery, not every implementation choice.
7. Once a plan is approved, proceed with routine implementation details within that scope without asking about every variable name, helper or test assertion. Return to the user whenever scope, budget, public contract or an approved decision would change.
8. Record approved material decisions in `docs/decisions/` using numbered ADRs. Record the question, options, user selection, rationale, supporting evidence, consequences, status and affected stages. Distinguish proposed, accepted, superseded and rejected records. Never invent user answers.
9. Keep questions in chat or the question tool, not only in a file. The workflow must pause at approval gates even when the agent would otherwise continue autonomously.
10. If the user requests changes to an earlier decision, identify affected artifacts and invalidate relevant downstream approvals. Do not silently rewrite history or treat downstream results as still verified.

## Stage Catalogue

Generate a substantive, tailored prompt for each row, not a generic template with a different title. Suggested artifact locations below are outputs for the stage to propose and create after approval, not files to prepopulate now.

| Prompt Filename | Responsibilities and Expected Evidence |
| --- | --- |
| `01-business-requirements.prompt.md` | Identify users, analyst workflow, business questions, five capability priorities, MVP/non-goals and measurable acceptance criteria. Separate platform reliability from analytical accuracy. Produce `docs/requirements.md`, a requirement-to-stage traceability table and approved MVP boundaries. |
| `02-domain-and-measurement.prompt.md` | Teach and document optical versus SAR, raster/vector, CRS, resolution versus pixel spacing, temporal comparability, cloud/nodata, uncertainty and arid-region confounders. Define what each indicator measures and cannot claim. Cover tides/reclamation, irrigation/seasonality, sand versus built-up, surface area versus water volume, and association versus causation. Produce a domain glossary and measurement specification. |
| `03-source-discovery-and-profiling.prompt.md` | Research authoritative source documentation, licenses, access/auth, quotas, product levels, STAC collections, assets, formats and historical availability. Separate catalogue access from asset download access. Propose bounded sample retrieval; measure actual AOI/date coverage, sizes, quality and schema. Record metadata, provenance, source URLs and verification dates in a source register and profiling report. Do not invent successful downloads. |
| `04-aoi-and-feasibility-pilot.prompt.md` | Ask about laptop CPU/RAM/free disk, Docker/WSL2 constraints, available time and data budget. Compare evidence-backed AOIs and observation periods. Propose a small, approved pilot measuring bandwidth, memory, disk, runtime, valid coverage and whether interpretable change exists. Include stable controls and candidate-change locations. Produce explicit go/no-go gates and approve geographic/time scope before full infrastructure. |
| `05-solution-and-data-architecture.prompt.md` | Design medallion flow, raster and vector compute responsibilities, storage, orchestration, upstream/local STAC, serving, observability and deployment profiles. Compare practical options without removing required technologies silently. Include resource envelopes, error paths, publication consistency and interfaces. Produce architecture ADRs and Mermaid context, component, data-flow and local-deployment diagrams. No claim of distributed-scale performance from Spark local mode. |
| `06-data-modelling-and-contracts.prompt.md` | Define grains, keys, spatial/temporal semantics and contracts for source items/assets, AOIs, processing runs, observation windows, grids, feature summaries, change candidates, quality results, lineage and resource usage. Select suitable CRS, partitions and formats; model footprints and nodata denominators. Distinguish observation time, ingestion time and processing time. Specify schema evolution, deterministic IDs, incremental updates and source-to-target mappings. Avoid one row per raster pixel by default. |
| `07-governance-and-security-design.prompt.md` | Agree a threat model, local/public exposure, data classifications, source licensing/attribution, open-source dependencies, retention/deletion, lineage, reproducibility, access roles and credential lifecycle. Consider OSM database licensing separately from code licensing. Decide how user-reviewed labels and reference evidence may be published. Produce implementable controls and acceptance checks, not just policy prose. |
| `08-repository-and-local-infrastructure.prompt.md` | Establish a reusable Python package, configuration, lock/pin strategy, tests, linting and Docker Compose using approved architecture. Separate persistent volumes and optional profiles, resource limits and health checks. Keep databases/internal services off public interfaces; ignore secrets, bulk data and local state. Validate Windows/WSL2 paths, clean startup and teardown without destroying volumes. Produce a setup runbook and safe environment example. |
| `09-source-ingestion-and-bronze.prompt.md` | Implement reusable adapters for approved sources, initially the approved MVP subset. Cover spatial/date filtering, pagination, bounded retries/backoff, rate limits, secure auth, checksums, manifests, caching and interrupted-download recovery. Preserve acquired original assets and provenance; do not call transformed clips raw originals. Test duplicate ingestion and deterministic reruns. Keep secrets and signed URLs out of logs and public metadata. |
| `10-raster-standardization-and-silver.prompt.md` | Implement approved raster preprocessing: source scaling/offsets and harmonization, masking, AOI clipping, grid alignment, reprojection, appropriate resampling, composites, valid-observation counts and COG validation. Use windowed processing and resource bounds. Distinguish categorical from continuous resampling. Implement SAR preprocessing only when selected and justified; do not assume raw GRD is analysis ready. Test misalignment, missing bands, clouds/nodata and comparable observation windows. |
| `11-spatial-transformation-and-lakehouse.prompt.md` | Implement Spark/Sedona processing for approved vector/features tables, spatial joins and grid/zone aggregations. Apply selected table formats, incremental/upsert rules, schema checks, partition strategy and small-file handling. Verify interoperability with the Python and serving layers. Benchmark one meaningful operation against a simpler baseline and explain why Spark remains in the portfolio architecture. |
| `12-change-products-and-indicators.prompt.md` | Deliver approved vegetation and surface-water baselines, candidate urban expansion, coastal-change products and multi-year environmental indicators in prioritized increments. Each product needs an explicit measurement contract, masks, persistence rules, uncertainty, representative stable/change controls and held-out evaluation where labels permit. Keep GHSL interpolated/projected epochs distinct from observations and OSM edits distinct from construction. Do not label same-source visual review independent ground truth. Require product-specific acceptance before proceeding to another increment. |
| `13-airflow-orchestration-and-recovery.prompt.md` | Orchestrate tested package entry points rather than embedding business logic in DAGs. Define observation-window processing, bounded concurrency, retries, timeouts, checkpoints, backfills, freshness semantics and safe publication. Avoid passing large rasters through XCom. Demonstrate a failed task, recovery and replay without duplicate outputs. Show how an already-running stage is prevented from double-publishing. |
| `14-quality-and-validation-gates.prompt.md` | Consolidate executable quality contracts and promotion gates across bronze/silver/gold; earlier stages must already include their relevant tests. Cover spatial validity, completeness, alignment, ranges, schema, duplicates, temporal coverage, source drift and analytical evaluation. Define warn/fail/quarantine behavior and auditable results. Block or mark insufficient-evidence products instead of publishing zero change. Prove a deliberately bad input cannot silently reach serving. |
| `15-stac-api-and-analyst-serving.prompt.md` | Publish searchable local STAC metadata with correct spatial/temporal extents, assets, projection/raster metadata and usable links; distinguish metadata APIs from raster tiles. Serve approved gold tables and before/after evidence through a minimal analyst interface. Include filters, legends, units, valid coverage, uncertainty and provenance. Enforce license attribution and secure access defaults. Test actual asset retrieval, API contracts and nonblank desktop/mobile views where a UI is built. |
| `16-observability-and-operational-runbooks.prompt.md` | Add correlated structured logs and metrics for source/API errors, processing failures, freshness, valid coverage, quality outcomes, runtime, memory and disk. Define actionable local alerts and runbooks. Test an alert and recovery. Keep logs free of credentials and high-cardinality metric labels. Use optional monitoring profiles to respect laptop limits; do not imply a sleeping laptop provides a 24/7 service. |
| `17-security-and-governance-verification.prompt.md` | Implement and verify the previously approved controls: secret/dependency/image scanning, credential redaction, bind addresses, least privilege, service separation, license notices, lineage queries, retention and deletion safeguards. Review public STAC links and repository fixtures for credential leakage or restricted data. Document residual risks honestly. Do not postpone all security until this stage; audit controls built into earlier work. |
| `18-performance-and-resource-finops.prompt.md` | Measure agreed workloads and report actual downloaded bytes, disk growth, runtime, peak memory and CPU time per meaningful unit such as km2 per observation window. Benchmark selected caching, chunking, partitioning and retention choices. Add budget guardrails and safe cleanup with protected source/provenance rules. Keep hypothetical cloud-cost estimates separate from actual local costs; do not invent bills or equate runtime to measured CPU time. |
| `19-end-to-end-and-reproducibility.prompt.md` | Validate requirement traceability, a clean-environment tiny demo, an approved real-data sample, incremental reruns, failure recovery, backfills, quality rejection and end-to-end lineage. Use network-free fixtures in ordinary CI and explicitly opted-in live-source tests. Distinguish synthetic fixtures from scientific validation. Report hardware, versions, commands, actual results and unverified gates. Do not fabricate analytical accuracy or production-scale reliability. |
| `20-documentation-and-portfolio-story.prompt.md` | Polish the root README, quickstart, developer guide, data dictionary, source register, methodology, ADR index, runbooks, limitations and Mermaid architecture diagrams based on implemented reality. Add lawful small screenshots/demo evidence and measured results, not invented achievements. Explain business value and senior engineering trade-offs, including what was deferred. Check all commands, links, source attribution and architecture-to-code consistency. |
| `21-github-release-and-handover.prompt.md` | Conduct a publication-readiness review for secrets, data/dependency licenses, large files, reproducibility, CI and documentation. Ask the user to approve a code license separately from source-data terms. Propose repository metadata, release notes and a concise portfolio narrative. Review incremental commit history without fabricating or rewriting it. Remote creation, pushes, tags and releases each require explicit authorization; provide manual steps if tooling/auth is unavailable. Produce a final requirement/evidence checklist and a prioritized backlog. |

## Required Structure of Every Stage Prompt

Use valid YAML frontmatter with a meaningful quoted `description` and `agent: "agent"`. Do not pin a model or invent tool identifiers. Do not include an unavailable custom agent as a dependency.

Each prompt body must include:

1. Stage objective, boundaries and explicit non-goals.
2. Required context and predecessor artifacts, with instructions to stop and identify missing approvals rather than fabricate them.
3. A short domain-learning objective tied to the actual stage.
4. Stage-specific decision checkpoints with realistic candidate options; alternatives remain proposals until selected. Do not prescribe an architecture as already approved.
5. An evidence/research or bounded-probe plan where needed.
6. An explicit approval gate before implementation.
7. Concrete work steps using existing reusable modules and repository conventions.
8. Named deliverables and their owners. Prefer updating existing documents/modules over introducing duplicate frameworks or files.
9. Focused, executable acceptance checks when practical; document review criteria for non-code stages. State what would falsify success. Run a focused check immediately after the first meaningful code edit before expanding the implementation.
10. Failure/blocker handling, including tool/network limitations and evidence not obtained.
11. State/ADR/requirement-traceability updates and a stage completion report.
12. A suggested truthful commit subject and the next prompt to run. Do not automatically run it.

Prompts must be detailed enough to execute, but keep shared rules in the shared contract. Do not repeat this entire generator inside every stage. Stage-specific candidate options should cover meaningful decisions, not force the user to decide low-level implementation trivia.

## Cross-Stage Engineering and Safety Rules

- Quality, documentation, security, governance and testing begin with the first relevant implementation. Their dedicated stages consolidate and verify; they are not permission to defer essential controls.
- Prefer established geospatial libraries over custom geometry, image-format or statistical machinery. Keep domain logic reusable and independently testable, not trapped in notebooks, DAGs or dashboards.
- Keep source and configuration separate; no machine-specific absolute paths. Use versioned AOIs/configuration and pin compatible runtime/dependency versions after checking current documentation.
- Research facts using authoritative sources and record access dates. Distinguish verified facts, measured results, assumptions and proposed targets. If browsing or execution is unavailable, state the limitation and request the smallest useful evidence instead of pretending.
- No credentials in chat, commits, examples, reports, screenshots, logs or metadata. Ask the user to enter secrets through an appropriate local secret mechanism, not a structured question response.
- No publishing third-party imagery, OSM-derived databases, basemap tiles or validation references without verifying redistribution and attribution requirements. A public code repository does not require public bulk datasets.
- Use a small lawful fixture/demo strategy. Do not commit entire satellite scenes, virtual environments, caches, container volumes or generated secrets.
- Respect the selected Git policy across all stages. Never use blanket staging such as `git add .`; inspect and stage only approved files. Do not initialize Git, create branches, commit, push or publish without authorization for that operation.
- A meaningful commit corresponds to a real, tested logical increment. Never backdate, manufacture a development history, split a finished implementation merely to simulate progress, or rewrite existing commits without permission.
- Do not deploy paid resources or install unapproved system software. Ask before downloads/jobs that exceed approved budgets. Do not auto-spawn subagents or change agent modes; propose any workflow handoff and obtain approval first.
- Maintain honest state transitions: not started, in progress, blocked, awaiting approval, complete. Mark complete only when approved acceptance criteria are met and the user accepts the stage outcome. Otherwise record exactly what remains.
- Resume from recorded state and repository evidence, not from claims in an earlier chat. Recheck assumptions invalidated by code/configuration changes.

## Generator Validation and Handover

Before reporting success:

1. Validate all generated prompt frontmatter, unique numbered filenames and relative links.
2. Check that the generated files cover every stage-catalogue responsibility and all five analytical capabilities, including scope and accuracy limitations.
3. Check every stage has prerequisites, option-based user decisions, a wait-for-answer rule, an implementation approval gate, concrete outputs, acceptance criteria and an explicit handoff.
4. Verify the shared instructions do not contradict existing repository policies and that no project decision is falsely recorded as accepted.
5. Confirm no application implementation, installations, source downloads, commits or remote publication occurred during generation.
6. Summarize generated files, the approved Git policy and how to invoke the first stage through the prompt picker or `Chat: Run Prompt...`. Stop and let the user launch it.

Do not claim these behavioral instructions technically prevent autonomous actions. Explain that the user should retain VS Code tool approvals and review diffs, especially for shell, Git and network operations.