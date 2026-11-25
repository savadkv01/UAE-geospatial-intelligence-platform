# 0031. Data Products and Contracts

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 06, 12, 14, 15, 20

## Question
How are the analyst-facing outputs packaged and specified as data products?

## Options considered
1. **Standards-based (recommended).** Each MVP capability is a data product published as one STAC Collection, with:
   - an ODPS v1.1 descriptor;
   - an ODCS v3.2 contract for each tabular or vector output, tested with datacontract-cli;
   - rasters specified with STAC `item_assets`, the raster, proj, file and processing extensions, and COG validation.
2. Custom YAML and JSON Schema per dataset: simpler, but no standard.
3. STAC-only: Collection metadata and `item_assets` define each product, with no separate contracts.

## User selection
Q3(a): products are STAC Collections, with ODPS descriptors, ODCS contracts, and rasters specified through STAC extensions.

## Rationale
Open, vendor-neutral standards make each product's owner, purpose, output ports, licence, limitations and schema explicit and machine-testable. ODCS does not describe rasters, so STAC covers them.

## Evidence
- **Verified (2026-11-25):** [ODCS v3.2.0 and ODPS v1.1.0](https://bitol.io/data-contracts-data-products-for-ai/), released 2026-09-08 by the Bitol project (Linux Foundation AI & Data).
- **Secondary source:** [datacontract-cli](https://github.com/datacontract/datacontract-cli) 1.2.9 (2026-10-30). Its MIT licence was verified in the repository.

## Consequences
- The products are *candidate urban expansion* and *vegetation change*. Deferred capabilities become new products when they enter scope.
- Each descriptor carries the cannot-claim statements and attribution notices.
- Stage 06 writes the contracts; Stage 14 runs the contract tests at the publish gate.
- Contract versions are part of the release identity ([ADR 0027](0027-stac-visibility-publication-boundary.md)).
