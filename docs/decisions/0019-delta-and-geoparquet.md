# 0019. Delta and GeoParquet

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 06, 08, 11–16, 19

## Question
What formats support incremental tables and portable delivery?

## Options considered
1. GeoParquet alone: lowest setup cost, no transaction log or MERGE.
2. Path-based Delta plus GeoParquet exports: transactional tables without a catalog daemon; requires compatible jars.
3. Iceberg v2 and JDBC catalog: transactional snapshots and partition evolution at the cost of catalog setup.

## User selection
Q3b(b): Delta Lake with WKB and bbox; GeoParquet 1.1 export for publication.

## Rationale
Use Delta transactions and pinned snapshots for operational tables without coupling analysts to Delta.

## Evidence
[Delta release evidence](https://delta.io/blog/2026-08-20-simplifying-your-open-lakehouse-with-the-delta-kernel-and-the-uc-delta-apis/) and [GeoParquet 1.1](https://geoparquet.org/releases/v1.1.0/), checked 2026-11-25. Incremental Spark overhead is an estimate, not measured.

## Consequences
Stage 08 checks compatibility; Stage 11 verifies round trips and CRS. Delta commits do not publish STAC items.
