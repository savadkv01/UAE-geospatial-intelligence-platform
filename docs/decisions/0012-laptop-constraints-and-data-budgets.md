# 0012. Laptop Constraints and Data Budgets

- Status: accepted
- Date: 2026-11-24
- Stage: 04-aoi-and-feasibility-pilot
- Affected stages: 05, 08, 09, 10, 13, 18, 19

## Question

What hardware, time and data budgets bound the project? They cap the AOI size, the number of observation windows, the job design and the infrastructure footprint.

## Options considered

1. **Tight:** pilot ≤ 1 GB download; full scope ≤ 20 GB download and ≤ 50 GB disk; single job ≤ 30 min. Safest, but leaves little room for multi-year windows.
2. **Moderate (recommended):** pilot ≤ 2 GB; full scope ≤ 50 GB download and ≤ 100 GB disk; single job ≤ 60 min. Fits multi-year seasonal windows for a sub-1,000 km² AOI and keeps runs short.
3. **Generous:** pilot ≤ 5 GB; full scope ≤ 150 GB download and ≤ 250 GB disk; single job ≤ 2 h. More headroom, but heavier on the laptop and slower to iterate.
4. Custom.

## User selection

"B. Moderate — pilot ≤ 2 GB download; full scope ≤ 50 GB download, ≤ 100 GB disk; single job ≤ 60 min." The user confirmed that the measured hardware values are correct, that there is "No cap; ~10 MB/s is typical", and that available time is "< 5 h" per week. After pilot 1, the user approved raising the **cumulative pilot** cap to **2.6 GB** for pilot 2.

## Rationale

The moderate budget comfortably fits the measured full-scope estimate (≈ 8 GB download, ≈ 11 GB disk) with room for re-runs. The limited weekly time favours small, per-window jobs over a larger scope.

## Evidence

- **Measured (2026-11-24, read-only commands):** Intel i7-10610U, 4 cores / 8 threads; 31.8 GB RAM; 467 GB free on `C:`; WSL2 default (Ubuntu-24.04 running); Docker Desktop 29.9.3 with a 15.5 GB / 8-CPU VM and no `.wslconfig`.
- **Measured (Stage 03):** ≈ 9.7 MB/s single-stream download.
- **Measured:** pilot spend 2.32 GB cumulative, peak RSS 1.48 GB, longest step 156.5 s ([feasibility pilot](../feasibility-pilot.md) §5).

## Consequences

- Stages 05, 08 and 18 design within ≤ 50 GB download, ≤ 100 GB project disk and ≤ 60 min per job. The full P1 scope (≈ 48 min of sequential I/O) must be split per window.
- The Docker VM currently has 15.5 GB of memory (WSL default). Any change, such as a `.wslconfig`, is a Stage 08 decision.
- The time budget of under 5 h/week favours small, testable increments.
