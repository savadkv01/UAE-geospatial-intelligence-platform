# 0025. Airflow Release Line

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 08, 13

## Question
Which Airflow release line should the laptop deployment pin?

## Options considered
1. Airflow 3.4.x with matching official constraints.
2. Airflow 3.3.x; older, with more time in use.

## User selection
Q5b(a): Airflow 3.4.x, latest patch pinned in Stage 08 with the official constraints.

## Rationale
Start from the current verified minor line and keep the integrated image reproducible.

## Evidence
[Airflow 3.4.0 release](https://airflow.apache.org/blog/airflow-3.4.0/), checked 2026-11-25: official image and constraints.

## Consequences
Stage 08 checks dependency compatibility; Stage 13 targets the selected API and executor behavior.
