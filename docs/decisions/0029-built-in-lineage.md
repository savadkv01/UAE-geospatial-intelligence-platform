# 0029. Built-in Lineage

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 06, 07, 09–17, 19

## Question
How is lineage captured and exposed, and does it need a dedicated service?

## Options considered
1. **Built-in lineage, no extra service:**
   - run manifests and Delta lineage tables;
   - the STAC processing extension and `derived_from` links;
   - OpenLineage events written by Airflow's provider to a file transport.

   No extra RAM.
2. As option 1, plus a Marquez UI in an optional `lineage` profile. Estimated 0.5–1 GB. A secondary source reports no Marquez release since 0.50.0 (Oct 2024).
3. Manifests and STAC links only, with no OpenLineage.

## User selection
Q1(a): built-in lineage with OpenLineage file events and no lineage service.

## Rationale
Gives traceability from gold to bronze, and standard OpenLineage events that a lineage server could ingest later, without adding a service of uncertain maintenance.

## Evidence
- **Verified (2026-11-25):** [Airflow OpenLineage provider 2.21.1](https://airflow.apache.org/docs/apache-airflow-providers-openlineage/stable/index.html) requires Airflow ≥ 2.11; [STAC processing extension](https://github.com/stac-extensions/processing) defines `derived_from` and `processing:lineage`.
- **Secondary source:** Marquez release status.
- **Unverified:** Spark OpenLineage support for Spark 4.1.

## Consequences
- Stage 06 defines the lineage keys and fields.
- Stage 07 sets the retention rules.
- Stages 17 and 19 run the gold-to-bronze lineage query.
- The Spark listener is optional until Stage 08 verifies it.
