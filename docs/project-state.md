# Project State

> The single source of truth for workflow progress. Stage prompts read this file first and update it at the end of each session.
> Allowed states are `not started`, `in progress`, `blocked`, `awaiting approval` and `complete`. Mark a stage `complete` only when the user accepts its outcome.
> Creating the prompt pack approved **no** project decisions.

## Workflow Settings

| Setting | Value | Source |
| --- | --- | --- |
| Workflow granularity | 21 stages (one prompt per stage) | User selection during prompt-pack generation |
| Learning interaction | Guided explanations with approval at each material decision | User selection during prompt-pack generation |
| Git policy | No Git operations unless the user specifically asks to commit or merge; agent proposes commits only | User selection during prompt-pack generation |

## Active Stage

- **Active stage:** none
- **Next action:** run `06-data-modelling-and-contracts` when ready; it is not started automatically.

## Stage Status

| # | Stage | Status | Approved outputs / evidence | Notes |
| --- | --- | --- | --- | --- |
| 01 | Business requirements | complete | [Approved requirements](requirements.md); [ADR 0001](decisions/0001-audience-and-mvp-priorities.md); [ADR 0002](decisions/0002-batch-observation-window-cadence.md); [ADR 0003](decisions/0003-acceptance-target-frameworks-and-non-goals.md) | Document review passed and user accepted the Stage 01 outcome. |
| 02 | Domain and measurement | complete | [Domain glossary](domain-glossary.md); [Measurement spec](measurement-spec.md); [ADR 0004](decisions/0004-mvp-indicator-families.md); [ADR 0005](decisions/0005-persistence-confirmed-change-semantics.md); [ADR 0006](decisions/0006-temporal-comparability-policy.md); [ADR 0007](decisions/0007-uncertainty-communication.md) | Document review passed and user accepted the Stage 02 outcome on 2026-11-14. |
| 03 | Source discovery and profiling | complete | [Source register](source-register.md); [Profiling report](profiling-report.md); [Probe script](../tools/probes/stage03_source_probe.py); [ADR 0008](decisions/0008-upstream-stac-providers-and-access-model.md); [ADR 0009](decisions/0009-sentinel-2-l2a-mvp-source.md); [ADR 0010](decisions/0010-sentinel-1-grd-mvp-source-and-level.md); [ADR 0011](decisions/0011-context-layers-and-reference-candidates.md) | Register, report and MVP sources approved on 2026-11-14 (S2 = Earth Search c1 with CDSE fallback; S1 = PC GRD with Earth Search and CDSE fallbacks). Probe used ≤ 0.33 GB of the 1 GB budget. Acceptance checks passed; user accepted the Stage 03 outcome on 2026-11-14. |
| 04 | AOI and feasibility pilot | complete | [Feasibility pilot](feasibility-pilot.md); [AOI file](../config/aoi/abu-dhabi-pilot-v1.geojson); probes [compare](../tools/probes/stage04_aoi_compare.py), [pilot 1](../tools/probes/stage04_pilot.py), [pilot 2](../tools/probes/stage04_pilot2.py); [ADR 0012](decisions/0012-laptop-constraints-and-data-budgets.md); [ADR 0013](decisions/0013-pilot-aoi.md); [ADR 0014](decisions/0014-observation-period-and-window.md); [ADR 0015](decisions/0015-feasibility-pilot-gates-and-outcome.md) | Outcome **go with recorded waiver** (G4 desert control C3 and G5a U1 failed; waived by the user). AOI = corridor (c) 562 km² + Al Ain patch 100 km², EPSG:32640; period P1 (Dec–Feb 2019/20–2025/26, 2021/22 Dec only). Pilot spend 2.32 GB (cap 2.6 GB); full scope ≈ 8.0 GB download, ≈ 11.3 GB disk (estimates). User accepted the Stage 04 outcome on 2026-11-24. |
| 05 | Solution and data architecture | complete | [Architecture](architecture.md); [ADR 0016–0032](decisions/README.md); [requirements mapping](architecture.md#requirements-traceability) | First accepted 2026-11-25. Revised the same day after review: ADR 0021 (boundary detail) and 0022 superseded by 0027 and 0028; new ADRs 0029–0032 (lineage, catalog, data products, quality gates). User re-accepted the revised outcome on 2026-11-25. All-on RAM ≈ 9.9 GB is an estimate; the revision adds no services. |
| 06 | Data modelling and contracts | not started | — | — |
| 07 | Governance and security design | not started | — | — |
| 08 | Repository and local infrastructure | not started | — | — |
| 09 | Source ingestion and bronze | not started | — | — |
| 10 | Raster standardization and silver | not started | — | — |
| 11 | Spatial transformation and lakehouse | not started | — | — |
| 12 | Change products and indicators | not started | — | — |
| 13 | Airflow orchestration and recovery | not started | — | — |
| 14 | Quality and validation gates | not started | — | — |
| 15 | STAC API and analyst serving | not started | — | — |
| 16 | Observability and operational runbooks | not started | — | — |
| 17 | Security and governance verification | not started | — | — |
| 18 | Performance and resource FinOps | not started | — | — |
| 19 | End-to-end and reproducibility | not started | — | — |
| 20 | Documentation and portfolio story | not started | — | — |
| 21 | GitHub release and handover | not started | — | — |

## Approved Requirements

[Approved requirements](requirements.md) — accepted by the user on 2026-11-11.

## Unresolved Decisions

- Exact observation-window length: **resolved** as Dec–Feb anniversary windows ([ADR 0014](decisions/0014-observation-period-and-window.md)). The freshness deadline remains open (Stages 13 and 18); annual windows with N = 2–3 imply 2–3 years of detection latency.
- Analytical reference source, metric selection, and numeric agreement and coverage thresholds; resolve in Stage 12. Stage 04 inputs: desert-control σ⁰ drift ≈ 1.7 dB; urban controls ≤ 0.6 dB; NDVI control drift ≤ 0.027 ([feasibility pilot](feasibility-pilot.md) §5).
- Persistence N (proposed 2–3), minimum mapping unit, compositing method and confidence-class rules; resolve in Stage 12. **SCL class 2 evidence (Stage 04):** ≤ 0.001 % of bare-land pixels on the selected winter dates, so masking it makes negligible difference in this AOI.
- Common target CRS: **resolved for this AOI** as EPSG:32640, 10 m ([ADR 0013](decisions/0013-pilot-aoi.md)). The corridor's 39N tiles must be reprojected (Stage 10).
- SAR calibration choice: **resolved for the MVP** as σ⁰ from GRD ([ADR 0010](decisions/0010-sentinel-1-grd-mvp-source-and-level.md)); the method is owned by Stage 10.
- Index families for the deferred capabilities (water, coastal, multi-year) and tide normalisation; decide when each enters scope.
- CDSE S3 keys are the first platform secret; storage and rotation to be defined in Stage 07 ([ADR 0008](decisions/0008-upstream-stac-providers-and-access-model.md)).
- Runtime pins, integrated Linux-on-WSL2 compatibility and loaded profile memory are Stage 08 gates; validate the 12 GB aggregate limit target and job/storage budgets in Stages 08 and 18. Safe release retries, orphan-release reconciliation and indexed-only tile access are implementation checks in Stages 13–15 and 19 ([architecture](architecture.md)).
- Stage 08 handoffs from the Stage 05 review: one Python version across Airflow constraints, PySpark, Sedona, Delta and rasterio; repository and data root inside the Ubuntu-24.04 WSL distro rather than NTFS or Docker Desktop's disk image; Spark jars baked into the image; Spark OpenLineage on 4.1 unverified ([architecture](architecture.md#implementation-feasibility-and-handoffs)).
- Map-ready vector export format (FlatGeobuf, GeoJSON or PMTiles); Stages 06 and 15. Quality library (GX Core or pandera); Stage 14.

**Open items from Stage 03 — status after Stage 04:**
- Earth Search c1 coverage re-measured for the chosen AOI: **resolved**. There are no items in Jan–Feb or Apr–Nov 2022 and only a few in Mar 2022; winter 2018/19 is thin. This led to the Dec-only 2021/22 window.
- Pre-2025 S1 revisit for persistence: **resolved**. Asc 130 gives 7 passes per Dec–Feb window (2 in the Dec-only window), which was enough for pilot composites.
- Gaps (unchanged): no free tide-data source has been researched or verified; terms for viewing very-high-resolution basemaps are unverified ([source register](source-register.md) §2).

**Risks handed off from Stage 04** (details in the [feasibility pilot](feasibility-pilot.md) §7):
- The G4 and G5a waivers ([ADR 0015](decisions/0015-feasibility-pilot-gates-and-outcome.md)).
- Thin Dec 2021 window.
- Four-tile MGRS junction.
- `WarpedVRT` explicit-grid defect over GCP-only S1 sources (Stage 10).
- Geocoding accuracy not measured.
- S1C cross-calibration not isolated.

## Invalidated Approvals

- 2026-11-25: the Stage 05 acceptance is reopened for the publication-boundary detail of [ADR 0021](decisions/0021-local-stac-api.md) and the tiler choice of [ADR 0022](decisions/0022-titiler.md), superseded by [ADR 0027](decisions/0027-stac-visibility-publication-boundary.md) and [ADR 0028](decisions/0028-titiler-pgstac.md). No downstream stage had started, so nothing else is invalidated.

## Evidence Links

- [Business requirements](requirements.md)
- [Domain glossary](domain-glossary.md)
- [Measurement specification](measurement-spec.md)
- [Decision index](decisions/README.md)
- [Source register](source-register.md)
- [Profiling report](profiling-report.md)
- [Source guide](source-guide.md) (learning companion for the Stage 03 sources)
- [Feasibility pilot](feasibility-pilot.md)
- [Solution and data architecture](architecture.md)
- [Pilot AOI file](../config/aoi/abu-dhabi-pilot-v1.geojson)
- [Domain knowledge handbook](domain-knowledge.md) (learning companion across stages; extend at the end of each stage)

## Checks Run

| Date | Stage | Command / review | Environment | Result |
| --- | --- | --- | --- | --- |
| 2026-11-11 | 01 | Document review against Stage 01 acceptance checks and user acceptance | Repository files; no external data or downloads | Passed; Stage 01 accepted |
| 2026-11-14 | 02 | Web verification of index formulas, sensor specifications and GHSL epoch semantics (ESA SentiWiki, ESA STEP forum, ASF HyP3, JRC GHSL catalogue, peer-reviewed citations) | Web search and fetch; no data downloads | Citations verified; MDPI full text blocked (HTTP 403), not relied on |
| 2026-11-14 | 02 | Document review against Stage 02 acceptance checks | Repository files | Passed: both MVP rows complete including "cannot claim"; every formula cited; arid and coastal confounders addressed; no threshold presented as validated |
| 2026-11-14 | 03 | Official documentation and live STAC collection metadata for licences, access and quotas (CDSE, PC, Earth Search, AWS Registry, JRC GHSL, OSM, EC Sentinel legal notice) | Web fetch and search | Verified; the ESA-hosted Sentinel legal notice URL failed DNS, so the EC copy hosted by ECMWF was used |
| 2026-11-14 | 03 | Bounded probe `.scratch/stage03/probe.py` (env, catalog, access, s2, s1, worldcover, ghsl, osm, cdse) | Windows 11, Python 3.13.14, rasterio 1.5.2 / GDAL 3.12.2, pystac-client 0.9.1; disposable venv | Completed within budget (≤ 0.33 GB of 1 GB); 12 anomalies recorded in the [profiling report](profiling-report.md) |
| 2026-11-14 | 03 (follow-up) | [Source guide](source-guide.md): mission facts checked against ESA SentiWiki, ESA, GDAL and cogeo.org; code examples run via `.scratch/stage03/guide_examples.py` and the guide's own snippets extracted and run as-is | Same probe environment; ≈ 20 MB per run | Passed; found and documented the negative-reflectance / NDVI-range pitfall |
| 2026-11-24 | 04 | Read-only environment check (`Get-CimInstance`, `Get-PSDrive`, `wsl --status`, `docker info`) | This laptop | Recorded in [ADR 0012](decisions/0012-laptop-constraints-and-data-budgets.md) |
| 2026-11-24 | 04 | AOI comparison probe `.scratch/stage04/compare.py` | Stage 03 venv (Python 3.13.14, rasterio 1.5.2 / GDAL 3.12.2) | 312 s, 6.9 MB; 3 candidates compared |
| 2026-11-24 | 04 | Pilot 1 `.scratch/stage04/pilot.py`: run 1 stopped after an S1 `WarpedVRT` defect; run 2 after the fix | Same | 567.5 MB + 1,209.7 MB; 532.6 s (run 2); peak RSS 1.48 GB; no-go (G4, G5a, G5b) |
| 2026-11-24 | 04 | Pilot 2 `.scratch/stage04/pilot2.py`: calibrated σ⁰ at sites; Al Ain vegetation patch | Same | 533.1 MB (cumulative 2.32 GB of the 2.6 GB cap); 256.3 s; G5b′ passed; G4 and G5a still failed and were waived by the user |
| 2026-11-24 | 04 | AOI geometry validation (shapely 2.2.0, pyproj 3.8.0) | Same | Valid, simple, closed, CCW, disjoint parts; areas 561.98 and 100.03 km² |
| 2026-11-24 | 04 | `py_compile` of `tools/probes/stage04_*.py` | Same | Passed |
| 2026-11-25 | 05 | Extract four Mermaid blocks from `architecture.md`; render to SVG with installed Mermaid Chart extension bundle in headless Edge | Windows, Mermaid Chart VS Code extension 2.8.4; local files, no installation or image pulls | Passed 4/4: context, components, data flow and deployment |
| 2026-11-25 | 05 | Compare requirement IDs with the architecture traceability matrix and check ADR index entries | Local Markdown files | Passed: 14/14 requirement IDs mapped, 11/11 new ADR links resolve; user accepted Stage 05 |
| 2026-11-25 | 05 (revision) | Web verification of titiler-pgstac, eoAPI, odc-stac, Delta/Spark 4.1, OpenLineage provider, Marquez, OpenMetadata, ODCS/ODPS, datacontract-cli, GX Core/Soda | Web search and fetch; no downloads | Recorded in [architecture](architecture.md) and ADRs 0027–0032; secondary sources labelled |
| 2026-11-25 | 05 (revision) | Re-render four Mermaid diagrams offline; requirement coverage; relative-link and anchor check | Same local renderer; local Markdown files | Passed: 4/4 diagrams, 14/14 requirements, 0 broken links |

## Blockers

_None._
