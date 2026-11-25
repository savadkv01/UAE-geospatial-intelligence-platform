# 0020. Shared PostgreSQL/PostGIS

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 07, 08, 13, 15, 17

## Question
Should Airflow and PgSTAC have separate database servers?

## Options considered
1. One server with distinct databases and least-privilege roles; lower RAM and operational cost.
2. Two servers; better failure and upgrade isolation at an estimated 0.2–0.3 GB extra.

## User selection
Q3c(a): One PostgreSQL/PostGIS server with separate databases and roles.

## Rationale
Avoid duplicate server overhead on the laptop.

## Evidence
[Laptop constraints](0012-laptop-constraints-and-data-budgets.md); [PostGIS](https://postgis.net/), checked 2026-11-25. The 0.4 GB planning allocation is an estimate.

## Consequences
Server outages affect both services. Stage 07 owns roles and trust controls; Stage 08 verifies version and migrations.
