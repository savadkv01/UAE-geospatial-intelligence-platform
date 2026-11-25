# 0015. Feasibility Pilot Gates and Outcome

- Status: accepted
- Date: 2026-11-24
- Stage: 04-aoi-and-feasibility-pilot
- Affected stages: 05, 10, 12, 14, 18

## Question

Do the measured pilot results justify investing in infrastructure (Stage 05 onwards) for the chosen AOI and period? Which gates decide this, and what happens when a gate fails?

## Options considered

**Gates.** The user approved these before any results, as proposed targets:

| Gate | Target |
| --- | --- |
| G1 Coverage | ≥ 1 valid obs on ≥ 95 % of land and ≥ 3 on ≥ 80 % |
| G2 Runtime | Each step ≤ 60 min; peak RSS ≤ 8 GB |
| G3 Volume | Pilot within budget; full scope ≤ 50 GB download and ≤ 100 GB disk |
| G4 Control drift | Median \|ΔNDVI\| ≤ 0.05 and \|Δσ⁰ VV\| ≤ 1.0 dB at the controls |
| G5a Urban | U1 Δσ⁰ VV ≥ +3 dB in both windows, with visual agreement |
| G5b Vegetation | ≥ 1 site with persistent \|ΔNDVI\| ≥ 0.10, with visual agreement |

The approved outcome rules:
- **Go** if all gates pass.
- **Conditional go** if only G5b fails.
- Otherwise **no-go**, followed by remediation options chosen by the user.

**After pilot 1 (no-go),** the remediation options were:
- Urban: (A) a targeted re-pilot with calibrated, noise-removed σ⁰ at the same sites and with the same gates; (B) a waiver; (C) a new AOI or window.
- Vegetation: keep it as weak; add an Al Ain patch; or defer it.

The user chose A and the Al Ain patch. Before pilot 2's results, G5b was replaced by **G5b′**:
- ≥ 1.0 km² of valid, non-water pixels with same-sign |ΔNDVI| ≥ 0.10 in both windows;
- the top block visually confirmed;
- the desert control |ΔNDVI| ≤ 0.05.

**After pilot 2 (still no-go under the rules),** the options were:
1. **Go with an explicit waiver** of G4 (C3) and G5a.
2. **No-go**, followed by remediation.

## User selection

"Go WITH explicit waiver of G4 (C3) and G5a (0.05 dB margin); scope = (c) + Al Ain patch, P1 (recommended)".

## Rationale

The resource gates pass by a wide margin. The two failed analytical gates are measured, small or explained, and become Stage 12 inputs rather than blockers:

- **C3 (desert control):** drift persisted after thermal-noise removal while the noise share fell. This suggests real surface change at a graded desert plot, not a processing artefact.
- **U1 (urban change):** missed +3 dB by 0.05 dB in one window, rose to +3.92 dB in the next, and its quicklooks show build-out. The established urban controls stayed within 0.6 dB.

## Evidence

All values were measured on 2026-11-24 and are detailed in the [feasibility pilot](../feasibility-pilot.md) §5 and §6.

| Gate | Result |
| --- | --- |
| G1 | 100 % (≥ 1) and ≥ 99.99 % (≥ 3) in every window and part (clearest 6 dates) — **pass** |
| G2 | Longest step 156.5 s; peak RSS 1.48 GB — **pass** |
| G3 | Pilot 2.32 GB of the 2.6 GB cap; full scope ≈ 8.0 GB download and ≈ 11.3 GB disk (estimates with measured inputs) — **pass** |
| G4 | ΔNDVI ≤ 0.027 at C1–C4. Calibrated σ⁰ VV: C1 0.33/0.60, C2 0.33/0.47, **C3 1.68/1.72 dB** — **fail, waived** |
| G5a | U1 calibrated **+2.95**/+3.92 dB; proxy +2.84/+3.43 — **fail, waived** |
| G5b′ | Al Ain: 10.0 km² persistent change; top block confirmed by same-source review (field green → bare); C4 0.027/0.014 — **pass** |

## Consequences

- **Outcome recorded as "go with waiver", not an unqualified go.** Stage 05 may start.
- **Stage 12:**
  - Change thresholds must exceed the measured desert drift (≈ 1.7 dB).
  - Controls must avoid graded or disturbed land; use several controls and consider drift monitoring.
  - Persistence N and the dB threshold must be chosen together, so that slow build-out is not missed.
  - Water must be excluded (SCL 6) from vegetation statistics.
- **Stage 14:** add control-drift checks per window as quality gates.
- **Stage 10:**
  - σ⁰ = (DN² − η) / A²σ with the noise LUTs, as prototyped here.
  - Avoid the `WarpedVRT` explicit-grid defect over GCP-only sources.
  - Assess geocoding accuracy.
- **The waiver must stay visible.** It is to appear in documentation (Stage 20) and must not be described as a passed gate.
