---
description: "Stage 09: Implement reusable, idempotent source adapters that land original assets with manifests and provenance in the bronze layer."
agent: "agent"
---

# Stage 09: Source Ingestion and Bronze

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/source-register.md`
- `docs/feasibility-pilot.md`
- `docs/architecture.md`
- `docs/data-model.md`
- `docs/governance-security.md`
- The package and runbook from Stage 08

**Prerequisites:** Stages 01–08 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** ingest the approved MVP sources for the approved AOI and windows into bronze. The ingestion must be reusable, resumable and idempotent, with full provenance.

**Non-goals:**
- Reprojection, compositing and masking. Stage 10 owns these.
- Airflow DAGs. Stage 13 owns these. Expose package entry points instead.

## 2. Domain-learning Objective

Explain the following topics:

- STAC item search: bbox versus intersects, and datetime ranges.
- Pagination.
- Asset signing or authentication, depending on the provider.
- Why bronze keeps **acquired originals**. A clipped or transformed file is not a raw original. If the user approves remote windowed reads, record them as derived subsets with their source references.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Acquisition mode per source:**
   - (a) Download full original assets. This uses more disk and gives the strongest provenance.
   - (b) Store STAC item JSON plus remote COG references, and read on demand. This uses less disk but depends on the provider.
   - (c) A hybrid.
2. **Retry, rate-limit and cache policy:**
   - The maximum number of retries and the backoff.
   - Concurrency, within the provider's quotas.
   - The cache location and the cache eviction rules from Stage 07.
3. **MVP ingestion subset:** which sources, windows and assets (bands) to ingest first, within the approved budget.

## 4. Evidence Plan

Before any full run, run a **dry run** that lists the items and assets with their expected bytes, and compare the total to the budget. Ask before the first real download batch.

## 5. Approval Gate

Get approval for the adapter design, the manifest schema (aligned with Stage 06), the subset and the byte budget before you implement or download anything.

## 6. Work Steps

1. Implement a source-adapter interface in the package, plus adapters for the approved sources. Use pystac-client, the provider's signing library if needed, and HTTP with bounded retries and backoff.
2. Implement manifests: one record per asset, using the deterministic ID from Stage 06. Each record includes:
   - Source href, without signed tokens
   - Checksum
   - Bytes
   - Retrieval time
   - Item and collection IDs
   - Product version or baseline
   - Licence and attribution reference
   - `run_id`
3. Make downloads resumable:
   - Write to a temporary file and move it atomically.
   - Verify the checksum.
   - Skip an asset if its manifest record and checksum already match.
4. Ensure that secrets and signed URLs never appear in logs, manifests or STAC metadata.
5. Write tests using network-free fixtures and mocked HTTP:
   - Pagination
   - Retry
   - Duplicate ingestion, which must create no new records
   - Interrupted download recovery
   - Redaction

   Run the first test right after the first adapter edit.
6. With approval, run one real, bounded ingestion and record the measurements.

## 7. Deliverables

- The adapters
- The manifest writer
- The command-line interface (CLI) or entry points
- Tests
- `docs/runbooks/ingestion.md`
- Updates to project state

## 8. Acceptance Checks

- The tests pass.
- A rerun of the same window produces zero new assets and an identical manifest set.
- An interrupted download recovers.
- Searching the logs and manifests for token patterns finds nothing.
- The measured bytes are within the budget.

**What falsifies success:** duplicate records on rerun, a transformed file labelled as an original, or a token found in output.

## 9. Failure and Blocker Handling

If provider throttling, authentication failures or outages occur, record them, back off and stop within the budget. Do not loop indefinitely. Report partial results honestly.

## 10. State and Completion Report

Update project state with the measured bytes, runtime, checks and the Stage 07 controls that are now verified.

## 11. Handoff

- Suggested commit subject (propose only): `feat(ingest): add idempotent STAC source adapters with bronze manifests`
- Next prompt: `10-raster-standardization-and-silver.prompt.md`. Do not run it automatically.
