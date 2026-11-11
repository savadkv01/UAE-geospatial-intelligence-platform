---
description: "Stage 08: Establish the Python package, tooling, tests and the Docker Compose local platform according to the approved architecture and controls."
agent: "agent"
---

# Stage 08: Repository and Local Infrastructure

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/architecture.md`
- `docs/data-model.md`
- `docs/governance-security.md`
- `docs/feasibility-pilot.md` (resource budgets)

**Prerequisites:** Stages 01–07 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** create a reusable, tested project skeleton and a local platform that starts cleanly within the approved resource envelope.

The skeleton includes:
- The Python package layout
- Configuration
- Dependency pinning
- Linting and tests
- Docker Compose with profiles, health checks and resource limits

**Non-goals:**
- Ingestion logic and processing logic
- DAG business logic
- Continuous integration (CI) workflows, unless the user approves a minimal lint/test CI here

## 2. Domain-learning Objective

Explain the following topics:

- Why GDAL, PROJ and Spark versions must be compatible.
- The Windows/WSL2 path and line-ending pitfalls: bind mounts from `/mnt/c` are slow, and CRLF line endings break shell scripts.
- Why named volumes are safer for databases.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Python environment and lock tool:**
   - (a) `uv` with `pyproject.toml` and a lockfile
   - (b) Poetry
   - (c) pip-tools
   - (d) conda/mamba. This option eases GDAL installation but adds weight.

   Verify the current tool status first.
2. **Repository layout:**
   - (a) A single `src/<package>` with submodules (ingest, raster, spatial, products, quality, stac, serving and observability)
   - (b) Multiple packages

   Also decide where the DAGs, Compose files, config and contracts live.
3. **Base images and versions:**
   - Official Airflow, Spark and PostGIS images, a STAC API image and a GDAL-capable Python image.
   - Pin by version or digest, checking current documentation.
4. **Code location:** whether to place the project in the WSL2 filesystem for performance, or keep it on Windows.

## 4. Evidence Plan

Check the current versions and compatibility from the official documentation. With approval, pull images and measure each profile's idle memory and disk use.

## 5. Approval Gate

Present the planned file tree, the services per profile, the port bindings (localhost only, according to Stage 07) and the resource limits. Get approval before creating the files or pulling images.

## 6. Work Steps

1. Create the package skeleton:
   - Typed configuration loading from versioned config files and environment variables.
   - No absolute machine paths.
   - A structured logging helper with credential redaction, so that redaction starts here.
2. Add linting, formatting, type checking and a test runner, with one smoke test. Run the smoke test immediately.
3. Create `.gitignore` entries for data, scratch, volumes, `.env`, caches and virtual environments. Add `.env.example` with placeholder names only, and a `.gitattributes` file for line endings.
4. Create the Docker Compose file:
   - Services from the approved architecture, using profiles such as `core`, `serving` and `monitoring`.
   - Named volumes for state.
   - Health checks and memory and CPU limits.
   - Ports bound to `127.0.0.1` only.
   - No secrets in the file.
5. Validate the stack:
   - Run `docker compose config`.
   - Start each profile, check health, tear down **without** `-v`, and confirm that the volumes persist.
6. Write `docs/runbooks/local-setup.md`: prerequisites, setup, start and stop per profile, reset (explicitly destructive and opt-in) and troubleshooting on Windows/WSL2.

## 7. Deliverables

- The package skeleton
- Tooling configuration
- The Compose file
- `.env.example`
- Ignore files
- The setup runbook
- Updates to project state

## 8. Acceptance Checks

- Linting and tests pass.
- `docker compose config` succeeds.
- Each profile becomes healthy within the approved memory envelope (measured with `docker stats`).
- No port binds to `0.0.0.0`.
- Teardown preserves volumes.
- A search finds no secrets in tracked files.

**What falsifies success:** a service that is only "running" but unhealthy, a public bind, or a secret in a tracked file.

## 9. Failure and Blocker Handling

If Docker or WSL2 is unavailable, or an image exceeds the budget, stop. Report the measured values and present the options to the user. Do not install system software without approval.

## 10. State and Completion Report

Record the commands run and their results in project state, and update the Stage 07 control-check status.

## 11. Handoff

- Suggested commit subject (propose only): `build: add package skeleton, tooling and local compose platform`
- Next prompt: `09-source-ingestion-and-bronze.prompt.md`. Do not run it automatically.
