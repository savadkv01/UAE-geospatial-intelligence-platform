---
description: "Stage 03: Research and verify candidate open data sources and their licences and access, then profile bounded samples into a source register."
agent: "agent"
---

# Stage 03: Source Discovery and Profiling

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md`
- `docs/measurement-spec.md`

**Prerequisites:** Stages 01–02 must be `complete`. Otherwise, stop and list what is missing.

## 1. Objective, Boundaries and Non-goals

**Objective:** turn candidate sources into **verified** sources. For each source, record:

- Licence
- Access and authentication
- Quotas
- Product levels and versions
- STAC collections and assets
- Formats
- Historical availability

Then measure real coverage, sizes and quality on a bounded sample.

Candidate sources include:
- Sentinel-2 L2A
- Sentinel-1 GRD
- GHSL
- OpenStreetMap
- Optional free reference layers that the user approves

**Non-goals:**
- Building ingestion code. Stage 09 owns this.
- Choosing the final AOI. Stage 04 owns this.
- Bulk downloads.

## 2. Domain-learning Objective

Explain the following topics:
- Processing levels: L1C versus L2A, and GRD versus RTC/ARD.
- STAC concepts: Catalog, Collection, Item, Asset and extensions such as `eo`, `sar`, `proj` and `raster`.
- The Sentinel-2 scene classification layer (SCL) and cloud probability.
- Processing baseline changes and the reflectance offset in newer Sentinel-2 baselines.
- Why **catalogue access** differs from **asset download access**. For example, an asset may need signed URLs, requester-pays storage or authentication.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Upstream STAC providers to evaluate:** candidates include Microsoft Planetary Computer, Earth Search (Element 84) and the Copernicus Data Space Ecosystem STAC. Recommend evaluating at least two. State each provider's auth and signing model only after verifying it.
2. **Which sources enter profiling:** the user selects from the verified candidates. Explain the role and the licence of each source, for example, Copernicus terms, GHSL terms and ODbL for OSM.
3. **Sample budget for profiling:** for example, (a) ≤ 1 GB, (b) ≤ 5 GB or (c) custom. Also set the number of items and the date range.
4. **Reference evidence options:** examples include free open land-cover products and user-reviewed labels. Note their redistribution constraints. Record these as candidates only.

## 4. Evidence and Probe Plan

**Research.** Read the official documentation for licences, access, quotas, product specifications and STAC collection IDs. Record the source URLs and access dates. Separate verified facts from assumptions.

**Probe.** The probe is bounded, read-only and disposable, and it runs only after the user approves the sample budget:

1. Run STAC searches over a small candidate bounding box around Abu Dhabi and a short date range. Record the item counts, cloud-cover distribution, asset keys, media types, `proj:epsg` values, sizes and baselines.
2. Download only the approved small sample to a git-ignored scratch location, or read windows remotely when supported. Record the bytes actually transferred and the elapsed time.
3. Inspect the sample with established tools such as rasterio, pystac-client or GDAL info. Record the CRS, resolution, dtype, nodata, scale and offset, and valid-pixel fraction.
4. Ask before any network or tool installation. If a probe fails, record the failure exactly. **Never report a download or measurement that did not happen.**

## 5. Approval Gate

The user approves two things separately:
- The probe plan and budget, before any network retrieval.
- The source register content and the selected MVP sources, before writing the ADRs.

## 6. Work Steps

1. Create `docs/source-register.md` with one row per source and these columns:
   - Provider
   - Collection ID
   - Product level and version
   - Licence and attribution text
   - Access and authentication
   - Quotas and rate limits
   - Formats and assets
   - Temporal availability
   - Spatial coverage
   - Known issues
   - Verification date and URLs
   - Status: candidate, verified or rejected
2. Create `docs/profiling-report.md` with the probe commands, environment, measured results, anomalies and limitations.
3. Record ADRs for the approved MVP sources and upstream STAC providers.
4. Keep scratch data out of the repository. Propose `.gitignore` entries if no ignore file exists yet.

## 7. Deliverables

- `docs/source-register.md`
- `docs/profiling-report.md`
- ADRs
- Updates to project state

## 8. Acceptance Checks

- Every MVP capability has at least one verified source, or a recorded gap.
- Licences, attribution, access paths and verification dates are present for each source.
- The profiling numbers come from executed commands that are recorded in the report.
- Catalogue access and asset access are documented separately.

**What falsifies success:** any measured value without a command or environment, or a licence claim without a source URL.

## 9. Failure and Blocker Handling

If network or authentication is unavailable, mark the affected rows `unverified` and record what the user can run manually. If a provider changes its terms, record the date and flag the downstream stages.

## 10. State and Completion Report

Update project state, including the evidence links and checks run. Report the verified sources, the gaps and the risks for Stage 04.

## 11. Handoff

- Suggested commit subject (propose only): `docs: add verified source register and profiling report`
- Next prompt: `04-aoi-and-feasibility-pilot.prompt.md`. Do not run it automatically.
