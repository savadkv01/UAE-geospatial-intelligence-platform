# 0026. Deployment Profiles and Resource Verification

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 08, 13, 15, 16, 18, 19

## Question
Which profiles are offered, and when will their resource use be measured?

## Options considered
1. Core, optional serving and optional Prometheus/Grafana monitoring; core ops records always available.
2. Core and serving only; defer exporters and dashboards, saving an estimated 0.75 GB.
3. Add a heavier observability stack including OpenTelemetry and Loki.
4. For measurement, either use labelled estimates until Stage 08 or pull representative images for a Stage 05 idle probe.

## User selection
Q6a(a) and Q6b(a): Three profiles with core ops records and optional Prometheus/Grafana/exporters; no Stage 05 probe.

## Rationale
Keep services opt-in and measure the actual composition rather than relying on an idle-only probe.

## Evidence
[Stage 04](../feasibility-pilot.md) §§1, 5: measured VM 15.5 GB, pilot peak RSS 1.48 GB. [Profile breakdown](../architecture.md#resource-envelopes-and-deployment-profiles): **estimated** 9.9 GB all-on against the 12 GB planning cap.

## Consequences
Stage 08 checks loaded profile RAM before expansion; Stage 16 builds operational views; Stage 18 verifies time, storage and transfer budgets.
