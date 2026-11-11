# 0003. Acceptance Target Frameworks and Non-goals

- Status: accepted
- Date: 2026-11-11
- Stage: 01-business-requirements
- Affected stages: 02, 03, 04, 07, 08, 10, 12, 13, 14, 15, 16, 18, 19, 20

## Question

Which reliability and analytical acceptance frameworks and hard non-goals should guide the MVP?

## Options considered

1. Use proposed reliability targets for duplicate-free reruns and demonstrated task recovery, with freshness deadline to be determined.
2. Use labelled reference evidence, agreement metrics, and valid-observation coverage for analytical evaluation, with the source and numeric thresholds to be determined in Stage 12.
3. Define different targets or non-goals.

## User selection

The user approved the proposed reliability framework: duplicate-free reruns and demonstrated failed-task recovery; freshness deadline TBD.

The user approved the proposed analytical framework: labelled reference evidence, agreement metrics, and valid-observation coverage; reference source and numeric thresholds TBD in Stage 12.

The user accepted the recommended non-goals: no parcel-level claims and no real-time alerting. The stage-required non-goals also apply: no causal attribution and no claims of equivalence to ground truth.

## Rationale

The frameworks separate dependable pipeline behavior from analytical agreement and explicitly leave evidence-dependent thresholds for later validation. No achieved reliability or accuracy is claimed.

## Evidence

- **User decision:** approval of the reliability and analytical frameworks and recommended non-goals.
- **Assumption:** suitable agreement metrics and a labelled reference source can be identified in Stage 12; this is not yet verified.

## Consequences

- Reliability evidence must test rerun idempotency and recovery; any freshness deadline requires later approval.
- Analytical evaluations must identify their reference evidence, metrics, and valid-observation coverage; the source and numeric thresholds remain open for Stage 12.
- Product and portfolio language must preserve the distinction between candidate signals and confirmed facts, avoid causal claims, and avoid ground-truth equivalence claims.
