# 0018. WSL2 Filesystem Storage

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 07–09, 13, 15, 18

## Question
Where should the laptop deployment persist datasets?

## Options considered
1. Bind-mounted WSL2 ext4 root; no object-store daemon and supports same-filesystem rename.
2. SeaweedFS S3 now; exercises S3 clients but adds a service and credentials.
3. RustFS S3 now; similar integration costs, with a younger implementation.

## User selection
Q3a(a): Local filesystem on WSL2 ext4, URI-based I/O, S3 deferred.

## Rationale
Reduce service overhead and keep staging and promotion on one filesystem.

## Evidence
[Measured laptop configuration](0012-laptop-constraints-and-data-budgets.md); [MinIO CE archive](https://github.com/minio/minio), verified 2026-11-25.

## Consequences
Use a shared data root with distinct write/serve boundaries. A future S3 backend needs a new release protocol as well as URI adapters.
