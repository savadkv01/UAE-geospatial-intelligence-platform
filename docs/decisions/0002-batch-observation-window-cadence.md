# 0002. Batch Observation-Window Cadence

- Status: accepted
- Date: 2026-11-11
- Stage: 01-business-requirements
- Affected stages: 03, 05, 08, 09, 13, 18, 19

## Question

Should the product process each new scene near-real-time, in batches by observation window, or annually?

## Options considered

1. Batch by observation window, such as monthly or seasonal; balances monitoring needs with manageable laptop data volume and runtime.
2. Near-real-time per new scene; increases ingest and compute frequency, storage, and runtime pressure.
3. Annual multi-year analysis only; is lighter to operate but less timely for monitoring.
4. Custom cadence.

## User selection

The user selected “Batch by observation window, such as monthly or seasonal.”

## Rationale

The selected cadence is recorded as provided. The exact window was not selected.

## Evidence

- **User decision:** batch by observation window.
- **Assumption:** monthly or seasonal windows are examples, not an approved exact cadence.

## Consequences

- Later stages must evaluate source availability, workload, and freshness against batch processing.
- The exact observation-window length and freshness deadline remain deferred until evidence and constraints are available.
