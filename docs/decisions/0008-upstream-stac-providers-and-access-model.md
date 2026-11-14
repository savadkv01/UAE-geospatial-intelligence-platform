# 0008. Upstream STAC Providers and Access Model

- Status: accepted
- Date: 2026-11-14
- Stage: 03-source-discovery-and-profiling
- Affected stages: 04, 05, 07, 09, 13, 16, 18

## Question

Which upstream STAC providers should the platform discover and read data from, and with what access model? This is material because providers differ in catalogue completeness, radiometric consistency, file format, authentication and quotas. Each of those affects ingestion design, secrets handling and laptop transfer volume.

## Options considered

1. Planetary Computer + Earth Search, with CDSE searched in the catalogue only (recommended at the time): no accounts needed; CDSE file access not profiled.
2. All three providers, including CDSE file access: CDSE is the official Copernicus source; needs a free account and S3 keys kept in an untracked `.env`.
3. Planetary Computer + CDSE: official source plus a COG mirror; needs an account.
4. Custom.

## User selection

Option 2: "All three, including CDSE file downloads (you create a free CDSE account; credentials go in an untracked .env)". After profiling, the user approved the per-role assignment in [ADR 0009](0009-sentinel-2-l2a-mvp-source.md) and [ADR 0010](0010-sentinel-1-grd-mvp-source-and-level.md).

## Rationale

Evaluating all three showed that no single provider is best for every role. CDSE has the only complete Collection-1 S2 archive. Earth Search serves the same Collection-1 data as anonymous COGs, but with gaps. Planetary Computer gives efficient windowed S1 reads. Assigning providers per role gives resilience without a paid service.

## Evidence

All entries come from the [profiling report](../profiling-report.md) and the [source register](../source-register.md), dated 2026-11-14.

- **Verified (docs and collection metadata):**
  - Planetary Computer: anonymous catalogue; Azure Blob assets need SAS signing.
  - Earth Search: anonymous catalogue and COGs.
  - CDSE: anonymous STAC v1 catalogue at `stac.dataspace.copernicus.eu/v1` (the legacy endpoint was deprecated from 17 Nov 2025). Assets need a free account and either S3 keys or a 10-minute token. Quotas: 4 concurrent connections, 20 MB/s per connection, 12 TB per 30 days.
- **Measured (catalogue access ≠ asset access):**

  | Provider | Unsigned or anonymous | Signed or authenticated |
  | --- | --- | --- |
  | Planetary Computer | 409 | 206 (SAS-signed) |
  | Earth Search S2 and S1 | 206 | — |
  | CDSE (HTTPS) | 401 | S3 download succeeded with keys |

- **Measured:**
  - CDSE returned HTTP 429 (WAF rate limit) on rapid sequential searches; the retry after 20 s succeeded.
  - Earth Search S1 metadata says `storage:requester_pays: true`, contradicting the measured anonymous access and the AWS Registry ("No AWS account required").

## Consequences

- Ingestion (Stage 09) needs a provider-specific asset-access layer:
  - SAS signing for Planetary Computer
  - anonymous HTTPS for Earth Search
  - S3 keys for CDSE
- Ingestion also needs retry and backoff on HTTP 429.
- The CDSE S3 keys are the platform's first secret. Stage 07 must define how they are stored and rotated; they are never committed, logged or written into metadata.
- Provider metadata can be stale (Earth Search `requester_pays`). Stage 09 must re-verify access before relying on it, and Stage 16 should monitor access.
- Per-provider terms and access are re-verified whenever a provider changes its service. The CDSE endpoint migration shows these can change.
