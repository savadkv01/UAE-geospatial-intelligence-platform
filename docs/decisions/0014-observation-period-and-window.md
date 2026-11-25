# 0014. Observation Period and Window

- Status: accepted
- Date: 2026-11-24
- Stage: 04-aoi-and-feasibility-pilot
- Affected stages: 05, 06, 09, 10, 12, 13, 14, 15, 18, 19
- Refines: [ADR 0002](0002-batch-observation-window-cadence.md) (cadence) and [ADR 0006](0006-temporal-comparability-policy.md) (anniversary comparability)

## Question

Which observation windows and which multi-year period should the MVP products use? Together with persistence N ([ADR 0005](0005-persistence-confirmed-change-semantics.md)), the window defines comparability, data volume and detection latency.

## Options considered

1. **P1 (recommended):** a Dec–Feb anniversary window per year, 2019/20 → 2025/26, with 2021/22 reduced to Dec 2021 only. Uses Earth Search COGs only and covers most of the Riyadh City build.
2. **P1b:** as P1, but Jan–Feb 2022 filled from CDSE JP2 (an extra ≈ 3–15 GB of full-tile downloads, needs an account).
3. **P2:** Dec–Feb 2022/23 → 2025/26 only. Cheapest and gap-free, but misses the main 2019–2022 build and leaves N = 3 with no slack.
4. Monthly: ruled out by measurement (≈ 2–3 S1 passes per track per month before 2025).
5. Custom.

## User selection

"P1 — DJF 2019/20→2025/26, 2021/22 = Dec only (recommended)".

## Rationale

Dec–Feb is the lowest-cloud season, with a full set of Earth Search scenes in most years. The same season each year satisfies the anniversary rule. Winter 2019/20 is the earliest consistent baseline; winter 2018/19 is too thin in Earth Search. A reduced Dec 2021 window avoids CDSE full-tile downloads while keeping the series consecutive.

## Evidence

All counts were measured on 2026-11-24 ([feasibility pilot](../feasibility-pilot.md) §2.2, §6).

- Earth Search `sentinel-2-c1-l2a` has no items in Jan–Feb or Apr–Nov 2022 and only a few in Mar 2022. Winter 2018/19 is thin.
- Eligible S2 dates per window (≥ 98 % footprint, ≤ 30 % cloud): corridor 10, 15, **3**, 9, 10, 13, 16; Al Ain 16, 17, **3**, 14, 13, 15, 17.
- S1 asc-130 passes per window: 7, 7, **2**, 7, 7, 7, 15.

## Consequences

- **Windows:** `2019/20` (baseline) through `2025/26`, defined as 1 Dec – end of Feb (UTC). Window `2021/22` is Dec 2021 only and carries a **reduced-window flag** with lower observation counts.
- **Latency:** with annual windows and N = 2–3, detection latency is **2–3 years**. Stages 12 and 13 must reflect this in the freshness definition (AC-03) and in the analyst narrative.
- **Baseline timing:** the 2019/20 baseline falls about 8 months after Riyadh City works began. Earthworks visible in the baseline cannot be detected as change (assumption: most building came later).
- **Later windows:** Dec 2026 – Feb 2027 and later windows extend the series under the same rule.
