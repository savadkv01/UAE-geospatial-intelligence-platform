# 0023. Analyst Web Map

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 07, 15, 20

## Question
What client should support the analyst workflow?

## Options considered
1. Static STAC Browser and small MapLibre comparison page; light server footprint.
2. Streamlit-style application; Python-first, but adds an application runtime.
3. API-only plus QGIS/notebook recipes; least UI work, no built-in comparison workflow.

## User selection
Q4c(a): STAC Browser plus a small MapLibre comparison page.

## Rationale
Provide discovery and window comparison without requiring a second Python web app.

## Evidence
[Approved analyst workflow](../requirements.md#analyst-workflow); [STAC Browser](https://github.com/radiantearth/stac-browser) and [MapLibre](https://github.com/maplibre/maplibre-gl-js), checked 2026-11-25.

## Consequences
Stage 15 owns interaction details and presents coverage, uncertainty and context alongside the indicator. QGIS remains a supported workflow to verify.
