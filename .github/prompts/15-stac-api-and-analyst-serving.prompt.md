---
description: "Stage 15: Publish gold products to a local STAC API and serve them through a minimal analyst interface with provenance, uncertainty and attribution."
agent: "agent"
---

# Stage 15: STAC API and Analyst Serving

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md` (analyst workflow)
- `docs/architecture.md` (serving ADRs)
- `docs/data-model.md`
- `docs/governance-security.md`
- `docs/quality.md`
- The accepted gold products

**Prerequisites:** Stages 01–14 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:**
- Publish searchable local STAC collections and items for the approved gold products.
- Serve tables and before/after evidence through the approved minimal analyst interface.

**Non-goals:**
- Public internet deployment.
- Republishing third-party imagery or OSM-derived databases beyond the Stage 07 rules.
- Feature-rich GIS applications.

## 2. Domain-learning Objective

Explain the following:

- STAC Collection and Item design for derived products: extents, `proj`, `raster`, `processing` and `file` extensions, `derived_from` links, licence fields and providers.
- The difference between a metadata API (STAC) and raster tile serving (for example, TiTiler).
- Why legends, units and valid-coverage displays matter for honest interpretation.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Collection design:**
   - (a) One collection per product. This option is recommended.
   - (b) One collection per product family.

   Also decide the item granularity, for example, per window per AOI tile.
2. **Analyst interface scope:** confirm or revise the Stage 05 choice. Decide which views are in the MVP, for example:
   - A map with layer toggles
   - A before/after comparison
   - A per-cell time series
   - A quality and provenance panel
3. **Access defaults:** localhost only. Decide whether authentication is needed for any write endpoints, such as STAC transactions. Write endpoints should normally be disabled or internal.
4. **Attribution display:** where and how to show the source licences and attribution.

## 4. Evidence Plan

Validate the STAC JSON against the schemas with available tooling, such as `stac-validator` or the pystac validation. Test actual asset retrieval through the asset hrefs.

## 5. Approval Gate

Get approval for the collection design, the interface scope and the access defaults before you implement.

## 6. Work Steps

1. Generate STAC items from the gold outputs with pystac. Include:
   - Correct bbox and geometry in EPSG:4326
   - Datetime or start and end datetimes
   - Assets with media types and roles
   - The projection and raster metadata
   - Lineage links to the inputs
   - The licence and attribution fields
2. Load the items into the local STAC API through the idempotent, publish-gated path from Stage 13.
3. Build the minimal analyst interface. Show filters, legends with units, valid coverage, uncertainty, the `insufficient_evidence` status, provenance (run, inputs and code version) and attribution.
4. Bind the services to localhost and disable unauthenticated writes.
5. Write tests:
   - STAC schema validation
   - API contract tests for search by bbox, datetime and collection
   - Asset hrefs resolve
   - Interface smoke tests

   With approval, take desktop and mobile viewport screenshots and check that the views are non-blank.
6. Write `docs/serving.md` and an analyst quick guide.

## 7. Deliverables

- The STAC publisher
- The collections and items
- The analyst interface
- Tests
- `docs/serving.md`
- Updates to project state

## 8. Acceptance Checks

- The STAC validation passes.
- A search returns the expected items, with spatial and temporal extents that match the data.
- The assets load.
- The interface renders non-blank views on desktop and mobile.
- Attribution is visible.
- No write endpoint is exposed without authentication.

**What falsifies success:** STAC extents that do not match the data, broken asset links, or missing uncertainty or attribution in the interface.

## 9. Failure and Blocker Handling

If a tile server or the user interface exceeds the budget, propose static previews or an optional profile. The user decides.

## 10. State and Completion Report

Update project state, the evidence (validation outputs and screenshots, if lawful) and the traceability.

## 11. Handoff

- Suggested commit subject (propose only): `feat(serving): publish gold products to local STAC API and analyst view`
- Next prompt: `16-observability-and-operational-runbooks.prompt.md`. Do not run it automatically.
