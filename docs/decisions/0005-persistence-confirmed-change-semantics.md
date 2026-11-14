# 0005. Persistence-Confirmed Change Semantics

- Status: accepted
- Date: 2026-11-14
- Stage: 02-domain-and-measurement
- Affected stages: 04, 05, 06, 10, 11, 12, 13, 14, 15, 18

## Question

What does "change" mean for the MVP products? The definition determines the false-positive rate, the number of observation windows needed (data volume) and how late a change is flagged.

## Options considered

1. Difference between two comparable composites: needs the least data (two windows), but transient effects (irrigation pulses, residual cloud, speckle, rain-wetted soil) cause the most false positives.
2. Trend over a multi-year series: robust to gradual change but slow to flag abrupt construction, and needs many windows. Better suited to the deferred multi-year capability.
3. Persistence-confirmed candidate change (recommended): a change against a same-season baseline must recur in N consecutive windows. Fewer transient false positives; needs a baseline plus N windows; flags change N windows later.
4. Custom.

## User selection

“(c) Persistence-confirmed candidate change.”

## Rationale

The user accepted the recommendation. The persistent signals of interest, such as completed construction and lasting greening or loss, survive the persistence test. Much of the transient noise typical of Abu Dhabi does not: irrigation cycles, rain events, dust, speckle and moving objects.

## Evidence

- **Assumption:** the relative frequency of transient vs persistent signals in the pilot AOI; to be measured in Stage 04.
- **Proposed target:** N = 2–3 consecutive windows; to be confirmed with evidence in Stage 04 or 12.

## Consequences

- Each product stores the baseline reference, the windows tested and a persistence count k of N.
- Detection latency is at least N windows, which affects the freshness discussion (AC-03, Stages 13 and 18).
- Data volume scales with the baseline plus N windows per comparison.
- Changes that occur and revert within fewer than N windows are not reported as candidate changes.
