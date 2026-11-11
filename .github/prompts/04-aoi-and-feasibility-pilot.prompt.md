---
description: "Stage 04: Capture laptop and budget constraints, compare evidence-backed AOIs and periods, and run an approved feasibility pilot with go/no-go gates."
agent: "agent"
---

# Stage 04: AOI and Feasibility Pilot

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md`
- `docs/measurement-spec.md`
- `docs/source-register.md`
- `docs/profiling-report.md`

**Prerequisites:** Stages 01–03 must be `complete`. Otherwise, stop and list what is missing.

## 1. Objective, Boundaries and Non-goals

**Objective:**
- Fix the geographic and temporal scope on evidence.
- Prove that the laptop can process the scope.
- Prove that the scope contains interpretable change.

Do both before any infrastructure investment.

**Non-goals:**
- Docker Compose stacks, Airflow and Spark setup. Stage 08 owns these.
- Production code. Pilot scripts are disposable unless the user approves keeping them.

## 2. Domain-learning Objective

Explain:
- How AOI size, pixel spacing, band count and number of observation windows drive data volume.
- Why a pilot needs **stable controls**, such as old urban cores, deep sea or bare rock, alongside **candidate-change locations**, such as new districts, reclaimed islands or irrigated farms.
- How cloud and nodata reduce the effective sample size.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Laptop and environment constraints:** ask for the following. Do not request any secrets.
   - CPU cores, RAM and free disk
   - OS and WSL2 status
   - Docker Desktop or Engine status and its memory allocation
   - Typical network bandwidth and data caps
   - Hours available per week
2. **Data and runtime budget:** for example, a maximum total download, a maximum disk footprint and a maximum single-job runtime.
3. **AOI candidates:** present 2–4 evidence-backed bounded options, each with an approximate area, rationale and expected change types. Examples:
   - (a) A coastal strip with known reclamation and new districts.
   - (b) An inland agricultural or irrigated zone with a desert margin.
   - (c) A combined small tile covering both.
   - (d) A custom polygon.
4. **Observation period and window:** for example, the same season annually over N years, or monthly over one to two years. Show the volume estimate for each option.

## 4. Evidence and Probe Plan (Pilot)

The pilot runs only after the user approves the plan, the budget and the scratch location.

1. Use a small, isolated, git-ignored environment. Ask before installing anything.
2. For the selected AOI and period:
   - Run STAC searches.
   - Retrieve the minimum assets needed, preferring windowed and remote reads.
   - Compute one simple indicator from the measurement spec on the comparable windows.
3. Measure and record the following, together with the commands and hardware context:
   - Bytes transferred
   - Disk growth
   - Wall time
   - Peak memory
   - Valid-observation coverage per window
4. Inspect the stable-control and candidate-change locations. Report whether the change is interpretable and whether controls stay stable within the stated tolerance. Label visual checks as same-source review, not ground truth.

## 5. Go/No-go Gates

Propose explicit gates as proposed targets, for example:

- Valid coverage is at least X% per window.
- The pilot runtime is within budget.
- Extrapolating the full-scope volume stays within the disk budget.
- The control drift is below the tolerance.
- At least one change site is interpretable.

The user approves the gates before seeing the pilot results.

## 6. Approval Gates

1. Approve the constraints and budget.
2. Approve the pilot plan.
3. Approve the final AOI, period and scope through an ADR. Record a `no-go` outcome if the evidence warrants it.

## 7. Work Steps

1. Store the approved AOI as a versioned vector file in a config location such as `config/aoi/<name>.geojson`. Use EPSG:4326 for storage and record its intended processing CRS.
2. Write `docs/feasibility-pilot.md` with these sections: constraints, candidates, chosen AOI and period, method, measurements, gates and their outcomes, scaling estimates, and risks.
3. Record ADRs for the AOI, period and budgets.
4. Update the requirements traceability.

## 8. Deliverables

- `docs/feasibility-pilot.md`
- The versioned AOI file
- ADRs
- Updates to project state

## 9. Acceptance Checks

- Every gate has a measured value or an explicit `not measured` entry, with a reason.
- The AOI geometry is valid: closed, non-self-intersecting and in the expected CRS. Check it with a geometry library.
- The scaling estimates show their formulae and inputs.

**What falsifies success:** a go decision with an unmeasured gate, or estimates presented as measurements.

## 10. Failure and Blocker Handling

If the gates fail, present the options: shrink the AOI, change the window, drop a capability or revisit Stage 01. The user decides.

## 11. State and Completion Report

Update project state with the measured budgets and the go/no-go outcome. Report the scope and the risks for Stage 05.

## 12. Handoff

- Suggested commit subject (propose only): `docs: record AOI selection and feasibility pilot results`
- Next prompt: `05-solution-and-data-architecture.prompt.md`. Do not run it automatically.
