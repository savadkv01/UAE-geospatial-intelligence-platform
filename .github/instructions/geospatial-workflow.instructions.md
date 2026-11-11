---
description: "Shared workflow, decision, approval, safety and Git contract for the UAE Geospatial Intelligence & Urban Change Monitoring Platform."
applyTo: "**"
---

# Geospatial Workflow Contract

This contract applies to every stage prompt in `.github/prompts/` and to any work in this repository. It guides agent behavior; it is **not** a technical permission boundary. The user keeps VS Code tool approvals and reviews diffs, especially for shell, Git and network operations.

## Project Frame

- Public portfolio project: an Abu Dhabi **pilot** AOI (exact AOI decided in Stage 04), five capabilities: vegetation change, surface-water extent change, candidate urban expansion, broad coastal change and multi-year environmental indicators.
- Free, openly licensed data only. Candidate sources include Sentinel-2 L2A, Sentinel-1 GRD, GHSL and OpenStreetMap. These are candidates until a stage verifies them and the user approves them.
- Laptop-first, open-source, Docker Compose, Windows/WSL2-compatible. No required paid cloud, paid imagery, proprietary GIS runtime, Kubernetes or GPU.
- Required technologies: Python, Spark, STAC API (upstream discovery **and** a local STAC API for published products), Airflow. Do not remove them silently.
- No claim of endorsement by, or knowledge of the internal stack of, any employer.
- The user is an experienced data engineer who is learning the geospatial domain. Explain domain reasoning such as CRS, SAR, masking and seasonality. Do not reteach elementary programming. Interaction style: **guided explanations with approval at each material decision**.

## Interaction and Decision Rules

1. **Start each stage by checking context.** Read this file, [project-state](../../docs/project-state.md), [decision index](../../docs/decisions/README.md) and the approved outputs that the stage names. Check that prerequisites are complete or explicitly waived by the user. Explain the stage's purpose, inputs and success criteria. Never start another stage automatically.
2. **The user makes material decisions.** This covers business, domain, data, architecture, infrastructure, modelling, analytics, quality, security, governance, resource budgets and releases. Never choose silently. Bundle choices only when they are tightly related. Keep independent decisions separate.
3. **Present options properly.** Give 2–4 realistic options, with a recommendation and reasons. Cover trade-offs and the impact on laptop resources and delivery. Include a custom-answer option and briefly explain new domain concepts. Never invent alternatives to fill a list.
4. **Ask few questions and wait.** Ask at most 2–4 related questions per interaction, using the structured question tool when available. Otherwise, use numbered questions with lettered options. Ask in chat or the tool, not only in a file. Silence is not approval. Pause at every approval gate, even in autonomous modes.
5. **Get evidence before deciding.** Identify decisions that need measurements first. Ask permission for a bounded, read-only or disposable probe, then report the measurements before the user chooses. A probe does not approve an architecture.
6. **Approve the plan before implementing.** After decisions are resolved, propose a short implementation plan. Get explicit approval before substantive edits, installations, downloads or long-running jobs. Permission to start a stage covers only its read-only discovery.
7. **Work within approved scope.** After approving a plan, handle routine details such as names, helpers and test assertions without asking. Return to the user if scope, budget, a public contract or an approved decision would change.
8. **Record decisions in ADRs.** Record approved material decisions as numbered ADRs in `docs/decisions/` using the template there. Include the question, options, user selection, rationale, evidence, consequences, status (proposed, accepted, superseded or rejected) and affected stages. Never invent user answers.
9. **Handle changes to earlier decisions explicitly.** Identify the affected artifacts and stages. Mark downstream approvals as invalidated in project state, and supersede ADRs instead of rewriting them. Do not treat downstream results as still verified.

## State Discipline

- Allowed stage states are `not started`, `in progress`, `blocked`, `awaiting approval` and `complete`. Mark a stage `complete` only when its approved acceptance criteria are met **and** the user accepts the outcome. Otherwise, record exactly what remains.
- Resume from `docs/project-state.md` and repository evidence, not from claims in earlier chats. Recheck any assumptions that later code or configuration changes have invalidated.
- Label every fact as **verified** (with source and access date), **measured** (with command and environment), **assumption** or **proposed target**.

## Engineering and Safety Rules

- Quality, testing, documentation, security and governance start with the first relevant implementation. The dedicated stages consolidate and verify these controls; they do not permit deferral.
- Prefer established geospatial libraries such as GDAL/rasterio, pyproj, shapely, pystac and Sedona over custom geometry, format or statistical code. Keep domain logic in a reusable, tested package, not in notebooks, DAGs or UIs.
- Keep configuration separate from code. Avoid machine-specific absolute paths. Version AOIs and configuration. Pin dependency versions after checking current documentation.
- After the first meaningful code edit, run a focused check before expanding the change.
- Never put credentials in chat, commits, examples, reports, screenshots, logs or metadata. Ask the user to enter secrets through a local secret mechanism such as an untracked `.env` file or a credential store, never through a question-tool answer.
- Verify redistribution and attribution terms before publishing third-party imagery, OSM-derived data, basemap tiles or reference labels. Public code does not imply public bulk data. Commit only small, lawful fixtures; never commit full scenes, virtual environments, caches, volumes or secrets.
- Ask before downloads or jobs that exceed the approved budgets. Never deploy paid resources or install unapproved system software. Do not auto-spawn subagents or switch agent modes without approval.
- If browsing, network or execution is unavailable, say so and request the smallest useful evidence. Never fabricate downloads, metrics, accuracy or results.

## Git Policy (user-selected)

- **No Git operations unless the user specifically asks for them.** At the end of a stage or milestone, *propose* a truthful commit subject and the exact list of files to stage.
- Run `git init`, staging, committing, branching, merging, tagging, pushing or remote creation only when the user explicitly requests that specific operation. Perform only the requested operation.
- Never use blanket staging such as `git add .` or `git add -A`. Inspect and stage only the files that belong to the approved increment.
- Each commit must be a real, tested logical increment. Never backdate commits, manufacture history, split finished work to simulate progress or rewrite existing commits without permission.
- Include the `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer when creating commits unless the user says otherwise.
