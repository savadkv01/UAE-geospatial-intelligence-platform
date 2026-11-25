# 0030. STAC as the Product Catalog

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 06, 15, 20

## Question
Does the platform need a metadata catalog service beyond the local STAC API?

## Options considered
1. The local STAC API (PgSTAC) catalogs published data products. Internal datasets are described by versioned contracts in the repository and a generated dataset reference page.
2. A metadata catalog service such as OpenMetadata. Its documented minimum is 4 vCPU and 16 GiB for the server alone, plus a database and a search engine, which exceeds the 15.5 GB Docker VM. Not feasible.
3. Custom.

## User selection
Q2(a): STAC as the product catalog, plus contracts in the repository and a generated dataset reference page.

## Rationale
STAC is the native catalog standard for Earth-observation products and is already required. A second catalog service does not fit the laptop.

## Evidence
- **Verified (2026-11-25):** [OpenMetadata minimum requirements](https://docs.open-metadata.org/v2.1.x-SNAPSHOT/deployment/minimum-requirements).
- **Measured:** 15.5 GB Docker VM ([ADR 0012](0012-laptop-constraints-and-data-budgets.md)).

## Consequences
- Stage 06 generates the dataset reference page from the contracts.
- Stage 15 exposes the product metadata through STAC Collections.
- A catalog service stays a deferred option, for example on a larger host.
