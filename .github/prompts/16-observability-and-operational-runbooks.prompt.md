---
description: "Stage 16: Add correlated structured logs, metrics, actionable local alerts and tested operational runbooks within laptop limits."
agent: "agent"
---

# Stage 16: Observability and Operational Runbooks

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/architecture.md` (monitoring profile)
- `docs/governance-security.md` (logging and redaction rules)
- `docs/quality.md`
- The existing runbooks
- The logging helper from Stage 08

**Prerequisites:** Stages 01–15 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** make the pipeline observable. Track these signals:

- Source and API errors
- Processing failures
- Freshness
- Valid coverage
- Quality outcomes
- Runtime
- Memory
- Disk

Each signal needs correlated identifiers, actionable alerts and tested runbooks.

**Non-goals:**
- A 24/7 service-level agreement (SLA). A sleeping laptop is not an always-on service; say so explicitly.
- Paid SaaS monitoring.

## 2. Domain-learning Objective

Explain the following:

- How data freshness differs from pipeline success. For example, the latest valid observation can be old because of clouds even when every run succeeds.
- Why coverage-aware metrics matter for EO monitoring.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Monitoring stack:**
   - (a) Structured logs plus Airflow UI and metrics, with a lightweight summary report. This option has the minimal footprint.
   - (b) An optional `monitoring` profile with Prometheus and Grafana, plus Loki or a similar log store.
   - (c) Custom.

   For each option, show its memory cost from measurements.
2. **Signals and labels:**
   - The metric names.
   - The allowed labels: low cardinality, such as product, layer, stage and source. Never use item IDs or cell IDs as labels.
   - The correlation IDs to use in logs, such as `run_id`, `window_id` and `task_id`.
3. **Alerts:** which conditions alert, for example:
   - Freshness beyond N days
   - Quality failure
   - Disk above X%
   - Repeated source errors

   Also decide the channel. Use a local notification or log only; no paid services.
4. **Runbook set:** which incidents get runbooks.

## 4. Evidence Plan

Measure the overhead of the monitoring profile with `docker stats` before the user approves it.

## 5. Approval Gate

Get approval for the stack, signals, alerts and runbook set before you implement.

## 6. Work Steps

1. Extend the structured logging with correlation IDs across the package, the DAGs and serving. Keep credential redaction, and add a redaction test.
2. Emit the metrics for the approved signals.
3. Configure the alerts. Write `docs/runbooks/<incident>.md` for each approved incident, with these sections: symptoms, diagnosis queries, recovery and verification.
4. **Alert test:** with approval, trigger at least one alert, for example, by simulating a disk threshold or a source error. Follow the runbook to recover, and record the evidence.

## 7. Deliverables

- The logging and metrics code
- The optional monitoring profile
- The alert rules
- The runbooks
- Tests
- Updates to project state

## 8. Acceptance Checks

- The redaction test passes.
- One run can be traced end to end by `run_id`.
- An alert fires and clears after recovery.
- No high-cardinality labels exist. Check by inspecting the label sets.
- The overhead of the monitoring profile is within the budget.

**What falsifies success:** credentials in the logs, an alert that never fires during the test, or unbounded label sets.

## 9. Failure and Blocker Handling

If the monitoring profile exceeds the budget, keep it optional and off by default. Document the trade-off.

## 10. State and Completion Report

Update project state with the alert-test evidence.

## 11. Handoff

- Suggested commit subject (propose only): `feat(observability): add correlated logs, metrics, alerts and runbooks`
- Next prompt: `17-security-and-governance-verification.prompt.md`. Do not run it automatically.
