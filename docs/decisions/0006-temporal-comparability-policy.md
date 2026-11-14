# 0006. Temporal Comparability Policy

- Status: accepted
- Date: 2026-11-14
- Stage: 02-domain-and-measurement
- Affected stages: 03, 04, 09, 10, 12, 14, 15

## Question

Which observations may be compared with each other, and should coastal products normalise for tide state or only flag it? Seasonal and tidal differences otherwise appear as false change.

## Options considered

1. Same season across years, with a tide flag only (recommended): removes most seasonal, sun-angle and irrigation-cycle effects; tide relevance is flagged because no tide source has been verified and coastal products are deferred.
2. All available observations, with a tide flag only: more data, but more seasonal confounding.
3. Same season across years, with tide normalisation now: adds a tide-model or tide-data dependency to the MVP.
4. Custom.

## User selection

“Same season across years + tide flag only.”

## Rationale

The user accepted the recommendation. Comparing anniversary windows controls the dominant seasonal confounders in Abu Dhabi: summer haze and dust, irrigation intensity and sun angle. Tide normalisation is deferred together with the coastal capability, while the flag keeps intertidal and mangrove effects visible to analysts.

## Evidence

- **Assumption:** the size of seasonal effects in the pilot AOI; to be measured in Stage 04.
- **Assumption:** no tide data source has been verified; Stage 03 may identify candidates.
- **Verified (2026-11-14):** SAR backscatter depends on viewing geometry ([glossary S5](../domain-glossary.md#sources)), so SAR comparisons are also restricted to the same relative orbit and pass direction.

## Consequences

- Baselines are same-season composites from earlier years.
- Sentinel-1 comparisons use the same relative orbit and pass direction.
- Products near the coast carry a tide-relevance flag. Tide normalisation requires a new decision and ADR when coastal change enters scope.
- Observation-window boundaries (deferred, [ADR 0002](0002-batch-observation-window-cadence.md)) must align with the seasons across years.
