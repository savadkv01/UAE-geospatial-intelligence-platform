# 0021. Local STAC API

- Status: superseded by 0027 (publication-boundary detail only; stac-fastapi-pgstac selection unchanged)
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 06, 07, 13–15, 19

## Question
How should analysts discover gold products and download their assets?

## Options considered
1. stac-fastapi-pgstac and read-only HTTP asset delivery; indexed search and transactional item loading.
2. In-memory STAC over JSON; lower RAM but maintenance/conformance and recovery are unverified.

## User selection
Q4a(a): stac-fastapi-pgstac on PgSTAC with a read-only static asset server. At the final documentation gate the user approved publishing assets first and indexing second, with serving restricted to indexed releases.

## Rationale
Separate catalog queries from asset bytes and use item identity as the publication boundary.

## Evidence
[API 7.4.0](https://pypi.org/project/stac-fastapi-pgstac/) and [pypgstac 0.10.2](https://pypi.org/project/pypgstac/) observed 2026-11-25; exact pairing remains to be validated.

## Consequences
Stage 15 provides range-capable asset URLs and restricts direct access to indexed releases. Stage 13 owns safe ordering and reconciliation; see [architecture](../architecture.md#publication-consistency).
