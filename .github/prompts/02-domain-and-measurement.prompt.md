---
description: "Stage 02: Teach and document the Earth-observation measurement concepts, and define what each indicator measures and cannot claim."
agent: "agent"
---

# Stage 02: Domain and Measurement

## Required Context

Read these files explicitly before starting.

- [Shared workflow contract](../instructions/geospatial-workflow.instructions.md)
- [Project state](../../docs/project-state.md)
- [Decision index](../../docs/decisions/README.md)
- `docs/requirements.md` from Stage 01

**Prerequisite:** Stage 01 must be `complete`. If it is not, stop and list the missing approvals. Do not invent requirements.

## 1. Objective, Boundaries and Non-goals

**Objective:** build a shared vocabulary and a **measurement specification**. For each approved capability, the specification states what the indicator physically measures, its unit, its valid domain and what it cannot claim.

**Non-goals:**
- Selecting final sources or products. Stage 03 owns this.
- Selecting the AOI. Stage 04 owns this.
- Implementing algorithms.

## 2. Domain-learning Objective

Teach the following concepts concisely, each tied to Abu Dhabi:

**Sensors and data types**
- Optical sensing (for example, Sentinel-2 surface reflectance) versus C-band SAR (for example, Sentinel-1 backscatter). Explain why SAR sees through cloud but responds to roughness and geometry.
- Raster versus vector data.

**Spatial reference and grids**
- Coordinate reference systems (CRS): geographic versus projected; UTM zones 39N and 40N around Abu Dhabi; area distortion.
- Resolution versus pixel spacing versus geometric accuracy.

**Observation quality**
- Temporal comparability: season, sun angle, acquisition time and tide.
- Cloud, haze, shadow and nodata.
- Uncertainty sources.

**Arid and coastal confounders**
- Irrigation and seasonality in vegetation indices; low-NDVI desert backgrounds.
- Bright sand versus built-up spectral confusion.
- Tides, turbidity and land reclamation for coastal and water change.
- Surface water **area** versus water **volume**.
- **Association versus causation**.

Use short examples. Do not reteach programming.

## 3. Decision Checkpoints

Ask at most 2–4 related questions per interaction and wait for each answer.

1. **Indicator families per MVP capability:**
   - Vegetation, for example:
     - (a) NDVI. This is recommended for simplicity and interpretability.
     - (b) SAVI or MSAVI, which handles bright soils better.
     - (c) Both, with SAVI as the arid-region check.
   - Water, for example:
     - (a) NDWI (McFeeters).
     - (b) MNDWI. This is recommended because it suppresses built-up noise.
     - (c) An optical index plus SAR thresholding.

   Present similar options for urban and coastal capabilities only if they are in scope. For example, built-up indices versus GHSL comparison, or shoreline from water masks versus SAR.
2. **Change semantics:**
   - (a) Difference between two comparable composites.
   - (b) Trend over a multi-year series.
   - (c) Persistence-confirmed candidate change. This option requires change to appear in N consecutive windows.

   Explain the effects on false positives and on data volume.
3. **Temporal comparability policy:**
   - Same season across years versus all available observations.
   - Whether to normalise for tide state or only flag it for coastal products.
4. **Uncertainty communication:**
   - (a) Categorical confidence classes.
   - (b) Valid-observation counts plus index variability.
   - (c) Both.

Any threshold remains a **proposed target** until Stage 04 or Stage 12 provides evidence.

## 4. Evidence Plan

Cite authoritative definitions for every index and formula, such as ESA Sentinel documentation and peer-reviewed sources, with access dates. If browsing is unavailable, say so and mark the definitions **unverified**.

## 5. Approval Gate

Present the draft glossary outline and the measurement-specification table. Obtain approval before writing the files.

## 6. Work Steps

1. Create `docs/domain-glossary.md`: concise definitions with Abu Dhabi examples and links.
2. Create `docs/measurement-spec.md`. For each capability, include:
   - Question answered
   - Physical quantity
   - Candidate inputs
   - Index or formula
   - Unit and range
   - Spatial and temporal grain
   - Comparability rules
   - Masks needed
   - Known confounders
   - Uncertainty representation
   - **Cannot claim**
   - Validation idea
3. Add explicit "cannot claim" statements. Examples:
   - Water area does not equal water volume.
   - Candidate urban expansion is not a construction permit or a building footprint.
   - GHSL epochs can be modelled or projected rather than observed.
   - OSM edits do not equal construction dates.
   - Coastal-line change can reflect tide, not erosion.
4. Record ADRs for the selected indicator families and change semantics.
5. Update the traceability statuses in `docs/requirements.md`.

## 7. Deliverables

- `docs/domain-glossary.md`
- `docs/measurement-spec.md`
- ADRs
- Updates to project state

## 8. Acceptance Checks (Document Review)

- Every MVP capability has a complete measurement-spec row, including "cannot claim".
- Every formula has an authoritative citation or an "unverified" label.
- Confounders specific to arid and coastal Abu Dhabi are addressed.

**What falsifies success:** an indicator described as measuring something it does not, such as NDVI as biomass or water area as volume, or a threshold presented as validated without evidence.

## 9. Failure and Blocker Handling

If a capability appears unmeasurable with free data at the chosen grain, document why. Propose deferral or rescoping through Stage 01 and an ADR supersession, and let the user decide.

## 10. State and Completion Report

Update project state and the evidence links. Summarise the decisions, open questions for Stage 03, which must verify source availability, and the assumptions.

## 11. Handoff

- Suggested commit subject (propose only): `docs: add domain glossary and measurement specification`
- Next prompt: `03-source-discovery-and-profiling.prompt.md`. Do not run it automatically.
