# 0007. Uncertainty Communication

- Status: accepted
- Date: 2026-11-14
- Stage: 02-domain-and-measurement
- Affected stages: 06, 10, 12, 14, 15, 20

## Question

How should products communicate the uncertainty of each candidate signal to analysts (AC-05)?

## Options considered

1. Categorical confidence classes only: easy to read, but they hide the underlying evidence.
2. Valid-observation counts plus index variability: objective and auditable, but harder for analysts to read.
3. Both (recommended): publish counts and variability as evidence, and derive confidence classes from them by documented rules whose thresholds are proposed targets.
4. Custom.

## User selection

“(c) Both.”

## Rationale

The user accepted the recommendation. Analysts get a readable class, while the auditable evidence behind it stays available, so a class is never an unexplained judgement.

## Evidence

- **Proposed target:** class rules and thresholds; to be defined with evidence in Stage 12.

## Consequences

- Product schemas (Stage 06) include, per pixel or object: valid-observation count, index variability, persistence count k of N, and the derived confidence class; plus the NDVI–SAVI agreement flag for vegetation.
- Class rules are versioned with the products, and changing them changes the product version.
- Serving (Stage 15) must show the evidence fields alongside the classes.
