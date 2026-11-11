---
description: "Stage 10: Implement approved raster preprocessing (scaling, masking, alignment, compositing and COG output) to produce silver analysis-ready data."
agent: "agent"
---

# Stage 10: Raster Standardization and Silver

## Required Context

Read these files explicitly.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/measurement-spec.md`
- `docs/source-register.md`
- `docs/feasibility-pilot.md`
- `docs/architecture.md`
- `docs/data-model.md`
- The Stage 09 bronze outputs and manifests

**Prerequisites:** Stages 01–09 must be `complete`. Otherwise, stop.

## 1. Objective, Boundaries and Non-goals

**Objective:** convert bronze rasters into comparable, aligned, masked, analysis-ready silver products for the approved windows, within the measured memory budget.

**Non-goals:**
- Indices, change detection and thresholds. Stage 12 owns these.
- Vector processing. Stage 11 owns this.

## 2. Domain-learning Objective

Explain the following topics:

- Sentinel-2 L2A digital-number scaling and the baseline-dependent offset.
- SCL-based cloud, shadow and water masking, and the limits of masking.
- Resampling choices:
  - Nearest neighbour for categorical layers such as SCL.
  - Bilinear or average for continuous reflectance.
- Grid alignment and snapping to a common origin.
- Median or percentile composites versus best-pixel composites.
- Valid-observation counts.
- Why raw Sentinel-1 GRD needs orbit correction, calibration, speckle handling and terrain correction before analysis. Explain this only if SAR is in scope.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Target grid:** the CRS, pixel size and origin. For example:
   - (a) The native 10 m UTM grid.
   - (b) A 20 m grid to reduce the data volume.
2. **Masking policy:** which SCL classes are invalid, whether to dilate the cloud mask, and whether to add a cloud-probability threshold.
3. **Compositing method:**
   - (a) Per-window median of valid pixels.
   - (b) Percentile composites.
   - (c) Best-available scene.

   For each option, show the effect on comparability and runtime.
4. **SAR (only if selected in Stages 01–05):**
   - (a) Use an analysis-ready or RTC product if a verified free source exists.
   - (b) Run a local preprocessing chain with an open-source tool, if justified within the budget.
   - (c) Defer SAR.

## 4. Evidence Plan

Process one window on a small tile first. Measure peak memory and runtime with windowed I/O, then extrapolate before running the full scope.

## 5. Approval Gate

Get approval for the grid, masking, compositing and SAR decisions, and for the plan with its runtime and memory estimate, before you implement.

## 6. Work Steps

1. Implement reusable functions in the package:
   - Apply the scale and offset per baseline.
   - Build masks.
   - Clip to the AOI with a buffer policy.
   - Reproject and align to the target grid, using the correct resampling per layer type.
   - Composite with a valid-observation count band.
   - Write COGs with nodata and overviews.
2. Use windowed or chunked processing with configurable memory bounds.
3. Write silver outputs with lineage metadata that links to the bronze asset IDs and the `run_id`.
4. Write tests with small synthetic or fixture rasters, covering:
   - Misalignment detection
   - A missing band
   - All-cloud and all-nodata windows
   - Categorical versus continuous resampling
   - Baseline offset handling
   - COG validity (for example, with rio-cogeo validation)

   Run the first test immediately after the first function.
5. With approval, process the approved windows and record the measurements.

## 7. Deliverables

- The raster modules
- Tests
- The silver COGs (local and git-ignored)
- `docs/methodology/raster-preprocessing.md`
- Updates to project state

## 8. Acceptance Checks

- The tests pass.
- All silver rasters share the CRS, transform and shape per grid.
- COG validation passes.
- The valid-observation band is present.
- Peak memory is within the budget.
- Rerunning the processing produces identical checksums or a documented deterministic tolerance.

**What falsifies success:** misaligned grids, reflectance outside the plausible range after scaling, or windows that are silently empty and still treated as valid.

## 9. Failure and Blocker Handling

If memory or runtime exceeds the budget, stop. Offer smaller tiles, a coarser grid or fewer windows, and let the user decide.

## 10. State and Completion Report

Update project state and traceability, and record the measured resources.

## 11. Handoff

- Suggested commit subject (propose only): `feat(raster): add masking, alignment and compositing to silver COGs`
- Next prompt: `11-spatial-transformation-and-lakehouse.prompt.md`. Do not run it automatically.
