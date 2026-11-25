# 0027. STAC Visibility as the Publication Boundary

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 13, 14, 15, 17, 19
- Supersedes: [0021](0021-local-stac-api.md) (publication-boundary detail only)

## Question
Must direct asset requests be checked against catalogue membership, or is STAC visibility enough as the publication boundary?

## Options considered
1. Catalogue-gated direct access (ADR 0021): nginx checks PgSTAC membership before serving bytes. It needs an unspecified custom authorization component, and no RAM was sized for it.
2. STAC visibility as the boundary: nginx serves the promoted release directory read-only, tiles resolve only indexed Items through titiler-pgstac, and a reconciliation task indexes or reports orphan releases.

## User selection
After the Stage 05 review the user said "proceed with changes", which approved option 2 as recommended in the review.

## Rationale
A promoted but unindexed release is complete, checksummed and undiscoverable, so serving its bytes carries no consistency risk. Option 2 removes a custom component without weakening AC-01 or AC-02. stac-fastapi-pgstac remains the STAC API.

## Evidence
- [Architecture review](../architecture.md#publication-consistency), 2026-11-25.
- titiler-pgstac resolves tiles through PgSTAC Items and searches ([titiler-pgstac](https://github.com/stac-utils/titiler-pgstac), verified 2026-11-25).

## Consequences
- Staging and quarantine stay outside the served root.
- Stages 13 and 19 test the orphan state and the reconciliation task.
- Stage 17 records the accepted residual: a guessed path can return the bytes of a complete orphan release.
