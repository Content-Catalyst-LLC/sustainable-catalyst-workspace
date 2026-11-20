# SC-RUN-VERIFY-01 — Workspace experiment and run tracking

## Result

Two PostgreSQL integration tests passed against the Workspace application from GitHub main at
`6c5dfee4803ace1dbb2aca563b0bb80f3bfbdd2b`. The tests used the real FastAPI routes,
SQLAlchemy persistence, content-addressed object store, worker claim and processing functions,
and pandas executor with disposable synthetic data. They established local behavior for one native
Workspace operation. Staging acceptance remains blocked. Production and scientific validation
were outside the executed checks.

The artifact endpoint returned HTTP 503 after the harness changed one byte of a registered output.
The reproduction endpoint still classified the pair as `exact`. That endpoint compares stored
input and output metadata. Its own record says `comparisonExecuted: false`. Treat this classification
as evidence of matching registered digests and rehash downloaded bytes for an integrity claim.

## Implementation at the source baseline

| Capability | Code and normal entry points | Reference migrations |
| --- | --- | --- |
| Dataset, model and parameter registry | `backend/app/registry.py`, `models.py`, `schemas.py`, versioned heads and revision rows exposed by `/v1/datasets`, `/v1/models`, `/v1/parameter-sets` | 004, 052 |
| Run tracking | `registry.py` resolves exact revisions and records the input fingerprint. `/v1/runs` exposes run state, events and outputs. | 004–006 |
| Runtime environment | `environments.py` serves `/v1/execution-environments` and pins environment manifest fingerprints. Runtime adapters are separate. | 005–006 |
| Execution and results | `jobs.py`, `worker.py`, `routing.py`, `compute.py`, `input_integrity.py`, `object_store.py`. The worker claims PostgreSQL job rows, resolves pinned inputs, stores a content-addressed result and registers it on the run. | 003, 004, 011, 052 |
| Provenance and replay evidence | `execution_provenance.py` assembles the graph and stores snapshots. `reproduction.py` records metadata comparisons. Cross-runtime verification has a separate API. | 006, 017, 035 |
| Access and audit | `security.py`, `authorization.py`, `session_auth.py`, `session_revocation.py`. Registry rows are owner-scoped. Run and job events record lifecycle changes. Explicit authorization evaluation has a separate decision-receipt path. | 031, 054–056 |

Here, the run is the execution record. Its `projectId` provides context and its inputs represent
the experiment specification. This review did not identify a separate experiment entity in
the run registry. Environment and model revision IDs were exercised as registry references.
The fixture executed in the host Python environment with the built-in pandas operation.
It did not launch the registered environment as a separate runtime or execute a model artifact.

## Execution and evidence

From the repository root at harness commit `4a135e84e96a2d7c4c7140a39f6c1a620e1d835b`:

```bash
python3.12 -m venv /tmp/sc-run-verify-venv
/tmp/sc-run-verify-venv/bin/python -m pip install -r backend/requirements.txt pytest==9.0.2
# With a local postgres:16-alpine image available:
SC_RUN_VERIFY_POSTGRES_IMAGE=postgres:16-alpine \
  bash scripts/sc_run_verify01_local.sh /tmp/sc-run-verify-venv/bin/python /tmp/sc-run-verify-evidence
```

The harness resolves the local Docker tag to an immutable image ID and launches that ID.
Use the recorded image identity and [Python dependency versions](evidence/python-dependencies.txt)
to repeat this execution as closely as possible. The runner also supports a disposable native
PostgreSQL cluster via `pg_config`. The first native attempt on the local host failed because
the sandbox denied PostgreSQL shared-memory allocation. The recorded passing run used Docker
for PostgreSQL and host Python 3.12.12 for Workspace. The API used an in-process ASGI client.
The harness called the production claim and processing functions synchronously to inspect
intermediate states. It did not run a separate API listener or the worker daemon loop.

| Check | Observed local behavior |
| --- | --- |
| Run creation and input revisions | Run began in `planned`. Four registry heads advanced to revision 2, while revision 1 remained readable with its original fingerprint. Jobs ran using revision 1 dataset bytes and parameters after the heads moved. |
| Parameter fingerprint | Independent canonical JSON SHA-256 matched the stored parameter-set descriptor. The job supplied the expected fingerprint and executed with the original selected column. |
| Unauthorized access | Anonymous run read returned 401. A distinct trusted-service user context received 404 for another owner's run and artifact reads and output registration. |
| Revoked session | Session exchange succeeded, then same-origin logout durably revoked the cookie. A fresh client presenting that cookie received 401 for both run read and creation. This covers session access revocation under the local flag. |
| Stale and duplicate requests | Stale writes and a missing dataset revision returned 409. Exact sequential replays of run and job creation returned the replay response. Reusing their keys with changed operation or priority returned 409. |
| Job progression and recovery | An altered input blob caused failure and produced zero outputs. Restoring bytes and requesting retry yielded `queued → running → succeeded` with 100% progress. A request to requeue the completed run returned 409. |
| Output integrity and provenance | Both successful jobs registered artifacts with matching byte counts and independently computed SHA-256. Run provenance resolved the pinned inputs, registered output and execution receipt. A stored snapshot, run, output reference and ordered run/job event sequences were readable after closing the client and disposing the database connection pool. |
| Numerical replay | A second run and job executed the same pinned fixture. Mean, sample standard deviation, median, minimum and maximum matched Python's standard-library oracle and each other with both absolute and relative tolerances of `1e-12`. The result artifacts had identical SHA-256. |

The [integration JUnit result](evidence/integration.xml), [execution log](evidence/integration.log)
and [observations](evidence/lifecycle.json) provide the test evidence. JUnit XML omits the local hostname.
Persistence was checked across fresh database connections. Server restart, backup and
restore, and crash recovery after a live worker disappears remain untested.

GitHub Actions independently reran the two integration tests at the same harness commit on Ubuntu
with Python 3.12.16 and native PostgreSQL 16.16. Both passed. The local and CI runs returned identical
measured statistics and identical input and parameter fingerprints. Each environment produced
matching digests within its own replay pair. Digests differed across environments. The artifact
envelope includes runtime metadata such as the Python patch version.
[Workflow run](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/actions/runs/44680727472) ·
[CI JUnit result](evidence/ci/integration.xml)

## Existing test assessment

- Root-level `tests/test_dataset_model_execution_run_registry_v240.py`,
  `test_reproducible_execution_environments_v250.py` and
  `test_reproduction_cross_runtime_verification_v2170.py` mostly inspect repository text,
  JSON schemas, historical version markers or route declarations. These checks do not establish that
  a database transaction, remote handoff or job completes.
- Backend `test_registry.py` checks Pydantic validation, metadata helpers and transition
  declarations. `test_jobs.py` exercises the in-process echo dispatcher and unknown-operation rejection
  using stub job records. Neither suite exercises job persistence.
- Backend provenance and cross-runtime tests include in-memory graph and comparison behavior,
  unauthenticated HTTP requests and contract snapshots. The focused run had **23 passed,
  3 failed and 6 skipped**. All three observed failures were historical version assertions
  (`3.4.0` versus profile `3.5.0` or health `3.83.0`, and `3.0.0` versus settings `3.83.0`).
  The six skipped input-integrity cases required PostgreSQL. See [focused JUnit results](evidence/existing.xml).
- `backend/tests/test_input_integrity_sc_nb01.py` has real PostgreSQL paths for registry
  writes, byte pinning, refusal and export lineage. Its R and Julia calls use a stub HTTP
  response. The separate disposable PostgreSQL run passed all 9 tests. This establishes Workspace
  behavior through the mocked service boundary. See the [PostgreSQL JUnit result](evidence/input-integrity-postgres.xml).

## Deployment and component reconciliation

GitHub main and the checked-out application, migrations, Dockerfile and dependency requirements
matched. The verification commits change the tests, harness, workflow and documentation.
The [acceptance receipt](acceptance.json) records relevant source commits, commands and evidence hashes.
The default backend and the local `/health` response both reported **3.83.0**. The
WordPress plugin header and `release-manifest-v3.70.0.json` both declare **3.70.0**.
The provenance profile declaration **3.5.0** identifies a historical feature profile.
For the Knowledge Base, record only **Workspace Backend 3.83.0, local implementation verification**
with the tested source SHA. A deployed Workspace product version and verified WordPress
or frontend versions remain unassigned.

`backend/Dockerfile` builds the API from Python 3.12 and runs schema initialization before Uvicorn.
`backend/docker-compose.example.yml` declares a separate `python -m app.worker` service and
server-configured integrations. These files provide source lineage for packaging. The test used
PostgreSQL **16.15** on **linux/arm64**. Its [recorded image identity](evidence/postgres-image.txt)
applies to the disposable database. Workspace API and worker ran in host Python.
The checked-in migration checksums identify reference DDL. The local harness ran explicit
security migrations **054–056** and SQLAlchemy schema initialization, using the current ORM
fresh-schema route. The full historical SQL upgrade sequence and deployed migration state were untested.
GitHub returned no deployments or candidate-image workflow runs for the exact application baseline.
An authorized staging inventory is required to map an actual service image digest and applied
migrations to the repository commit. The GitHub queries establish the scope of available evidence.

| Integration | Source interface | Staging status |
| --- | --- | --- |
| Workspace → Lab | `routing.py` server-configured `lab` job dispatch and runtime handoff code | Blocked. No authorized staging route, service identity, fixture permissions or deployed contract version supplied. |
| Workspace → Library | `/v1/library-bridge/*` reference, context and public discovery routes. Job routing also supports a configured Library target. | Blocked. No authorized deployed interface and disposable records supplied. |
| Workspace → Research | `research_exports` grant/fetch, research access/introspection, and server-side Research API calls for outputs and publishing | Blocked. No authorized Workspace/Research staging pair, scoped test identities or isolated fixture access supplied. |

## Unresolved issues

1. Reproduction `exact` survives output blob corruption while artifact reads fail. A stronger
   verification receipt would need a fresh byte-integrity check.
2. The run and job idempotency checks exercise serial retries. Concurrent duplicates and worker
   termination recovery require separate evidence. The tested run state and event rows are not evidence
   of storage-level append-only enforcement.
3. Session revocation was exercised via the local trusted-service exchange with revocation enabled.
   OIDC login, project-role revocation, service credential revocation, cross-product permissions
   and in-flight execution under revoked permissions remain untested.
4. Staging acceptance requires scoped tenancy, synthetic fixture authorization, service
   manifests, running digest evidence, applied migration records and deployed interface identities.
   No production or scientific claim can be made from this fixture.
