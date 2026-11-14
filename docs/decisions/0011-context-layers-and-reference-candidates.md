# 0011. Context Layers and Reference-Evidence Candidates

- Status: accepted
- Date: 2026-11-14
- Stage: 03-source-discovery-and-profiling
- Affected stages: 04, 07, 09, 12, 15, 20, 21

## Question

Which non-signal sources enter profiling as context, and which reference-evidence options are recorded as **candidates** for Stage 12's analytical evaluation (AC-04)? Licence terms, especially attribution and share-alike, constrain what can be published.

## Options considered

**Sources entering profiling:** S2 L2A, S1 GRD, GHSL GHS-BUILT-S R2023A, OpenStreetMap, ESA WorldCover. Any subset could be chosen.

**Reference candidates:**
- ESA WorldCover 2020/2021
- S2 true-colour composites for visual interpretation
- user-reviewed labels
- Impact Observatory/Esri 10 m annual LULC
- very-high-resolution basemaps for viewing only

Any subset could be chosen.

## User selection

All five profiling sources, and all five reference candidates.

## Rationale

Context layers help analysts interpret candidate signals. Recording a broad set of reference candidates keeps Stage 12 options open, while making each candidate's licence status explicit.

## Evidence

All entries come from the [source register](../source-register.md) rows R8–R14, dated 2026-11-14.

| Source | Licence (verified) | Measured findings |
| --- | --- | --- |
| GHSL | CC BY 4.0. Must cite Pesaresi et al. (2024), doi:10.1080/17538947.2024.2390454, plus the product citation | 100 m Mollweide tile of 3.2 MB |
| OSM | ODbL 1.0: "© OpenStreetMap contributors"; distributed derived databases must be ODbL | 26,044 buildings in the test box; `start_date` on 0.01 %; 48 % last edited in 2023; one Overpass HTTP 502 |
| ESA WorldCover | CC BY 4.0 | 2020 v1.0.0 and 2021 v2.0.0 only, delivered in EPSG:4326 |
| Impact Observatory LULC v02 | CC BY 4.0, from collection metadata | 2017–2023; not profiled |

The very-high-resolution basemap terms were **not verified**.

## Consequences

- **GHSL and OSM are context only.** They are never inputs to the signal, and GHSL epochs are not observations ([measurement spec](../measurement-spec.md)).
- **OSM handling.** OSM-derived layers stay separate from our own products, so the share-alike obligation does not extend to them. Stage 07 decides how OSM is displayed and attributed. For repeatable ingestion, a dated extract file is preferred over live Overpass queries (**proposed**, Stage 09).
- **Reference candidates are not approved for evaluation.** Stage 12 selects them.
- **Very-high-resolution basemaps** stay view-only and unverified. They must not be redistributed, or used to derive published labels, until their terms are verified.
- **WorldCover** must be reprojected before computing area statistics. Its 2020 and 2021 versions use different algorithms, so they must not be compared as change.
- **Attribution.** Stage 20/21 documentation carries every attribution notice: Copernicus, GHSL, OSM, WorldCover and Impact Observatory.
- **Remaining gaps:** a free tide-data source, and terms for very-high-resolution viewing.
