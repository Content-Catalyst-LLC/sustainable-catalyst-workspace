# SC-RUN-VERIFY-01 corrective verification

Follow-up to [the original verification PR #78](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/pull/78).
The original receipt and its finding describe the behavior of source commit
`6c5dfee4803ace1dbb2aca563b0bb80f3bfbdd2b`. The correction is independently reviewable in
[draft PR #79](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/pull/79).
The candidate application and test commit is `362354da4bbbf5a7bc0bcf2db572dcb5f5ebfad5`.

## Receipt behavior

Both `POST /v1/reproduction-verifications` and
`POST /v1/reproduction/cross-runtime/verifications` report registered-digest matching separately
from artifact-byte integrity. For each output, Workspace resolves an owner-scoped artifact revision
by the registered artifact ID, SHA-256 and size. It reads the stored blob, independently hashes
the bytes and measures their length. Historical revisions remain resolvable after the artifact
head advances. The common checker streams the content and captures up to 5 MiB only when
cross-runtime JSON comparison needs the authenticated bytes.

| Fixture | Registered digest match | Artifact check | Receipt classification |
| --- | --- | --- | --- |
| Intact, or artifact head advanced with the registered revision intact | Yes | `verified` | `exact` for the tested matching runs |
| Same-length byte corruption | Yes | `corrupted` | `incomplete` |
| Missing blob or missing registered artifact record | Yes | `missing` | `incomplete` |
| Storage read failure or digest-only registration | Yes | `unavailable` | `incomplete` |
| Intact, different content within JSON numeric tolerances | No | `verified` | Cross-runtime `equivalent` in tolerance mode and `divergent` in exact-digest mode |

A positive classification requires succeeded runs in addition to the relevant input, environment,
runtime and output conditions. The API sets `scientificValidationPerformed: false`. The byte
check establishes integrity at receipt creation time. Existing receipts are time-stamped evidence
and a later read of a receipt does not recheck storage. To check current bytes, create a fresh
verification receipt. Operational unavailability returns an incomplete receipt with a stable
reason code instead of treating a match of stored digests as successful verification.

Request shapes, identifiers, receipt schema versions, and stored receipt rows and fingerprints
are retained. No database migration or backfill is required. When reading a historical receipt
without artifact-check evidence, the API marks it `not-checked`, exposes its old classification
as `registeredClassification`, and represents historical positive claims as `incomplete`.
The existing receipt fingerprint continues to identify the stored historical evidence. Previously
exported artifacts remain historical records. Treat their classifications according to the
verification method that produced them. A digest-only output can still be registered.

## Historical test investigation

- `backend/RELEASE_NOTES_3.4.0.md` identifies the introduction of the scientific execution
  provenance endpoints, migration 035 and a then-current 64-operation typed client. The profile's
  current declaration is `3.5.0`, the typed-client projection declares `3.46.0`, and the backend
  health response reports the configured service version, currently `3.83.0`. The global health
  migration pointer refers to migration 050. The tests now check the provenance release identity,
  schema and authority flags, the presence of migration 035, health against configured service
  identity, and typed route bindings and OpenAPI coverage. Historical counts and global release
  metadata are left to their original release artifacts.
- `backend/RELEASE_NOTES_2.17.0.md` identifies the cross-runtime release contract as digest and
  bounded JSON comparisons, durable receipts and migration 017. The test's unrelated backend
  default of `3.0.0` was removed. The supported comparison modes, tolerance behavior and
  migration 017 checks remain.
- The earlier three failures and six database-dependent skips remain in
  [PR #78's original focused JUnit result](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/blob/5a3d9f3a634e17c94d970a110b72ce6555e47e98/docs/verification/sc-run-verify-01/evidence/existing.xml).

## Reproduction and acceptance

From the corrective commit, with Docker and a local PostgreSQL image available:

```bash
python3.12 -m venv /tmp/sc-reproduction-venv
/tmp/sc-reproduction-venv/bin/python -m pip install -r backend/requirements.txt pytest==9.0.2
docker pull postgres:16-alpine
bash scripts/sc_run_reproduction_integrity.sh \
  /tmp/sc-reproduction-venv/bin/python /tmp/sc-reproduction-evidence
```

The script launches a new PostgreSQL container from the image ID resolved locally, binds a random
loopback port, creates disposable object storage and removes both after execution. FastAPI and
worker functions execute from the checkout using a host Python process. The suite initializes
a clean schema with the existing ORM. The tests exercise the actual ASGI endpoints, worker
claim and completion, PostgreSQL receipt writes and readback, and real temporary object files.
The unavailable-storage fixture replaces the blob path with a directory to induce a real read error.
It demonstrates fail-closed classification. A storage service outage remains outside the test.

The candidate passed **19 tests locally and 19 in GitHub Actions**, with no failures or skips in
either run. Each run included 10 PostgreSQL integration cases and 9 release-contract and unit
checks. The attached JUnit XML omits runner hostnames. [Local JUnit](evidence/local/test-results.xml) ·
[CI JUnit](evidence/ci/test-results.xml) ·
[GitHub Actions run](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/actions/runs/44682116615)

The [acceptance receipt](acceptance.json) records the exact test commit, commands, test counts,
environment identities and evidence checksums. The original PR #78 receipt is preserved.
Its baseline test asserts the previously observed metadata-only behavior. That assertion will need
to follow the corrected contract if the two branches are integrated.

## Staging and release scope

The correction has been exercised only in isolation. Staging remains blocked pending authorized
Workspace, Lab, Library and Research staging endpoint and contract identities, scoped accounts and
a disposable fixture tenant. Provide the running API and worker image digests with source mapping,
approved manifests, applied migration ledger and an authorized way to create, verify and clean up
synthetic runs. No production data, configuration or deployment was changed. Independent
scientific validation requires separate evidence for the scientific method and data.
