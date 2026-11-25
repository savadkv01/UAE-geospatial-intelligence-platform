# 0024. Airflow LocalExecutor

- Status: accepted
- Date: 2026-11-25
- Stage: 05-solution-and-data-architecture
- Affected stages: 07, 08, 13, 16, 18

## Question
How should Airflow launch laptop batch tasks?

## Options considered
1. LocalExecutor with shared Postgres and a processing-capable Airflow image.
2. LocalExecutor with DockerOperator; isolates dependencies but introduces a Docker socket trust boundary.
3. CeleryExecutor; workers and broker add services and estimated RAM.

## User selection
Q5a(a): LocalExecutor with shared Postgres, processing dependencies in the task image, parallelism 2, Spark pool 1 and raster pool 2.

## Rationale
Keep the execution environment simple and cap collocated compute without a broker or Docker socket.

## Evidence
[Official Airflow Docker quick-start](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html), checked 2026-11-25: uses Celery rather than this LocalExecutor design.

## Consequences
Count task memory inside the scheduler container envelope and validate contention in Stages 08 and 18.
