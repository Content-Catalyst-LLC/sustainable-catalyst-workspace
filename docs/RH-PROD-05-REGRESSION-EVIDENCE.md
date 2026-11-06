# RH-PROD-05 — Workspace backend regression reconciliation

**Status:** Candidate tooling only; **not** production or full-suite acceptance.

## Evidence and exact comparison boundary

- Workspace candidate for PR #16 includes session revocation, identity introspection and isolated Research authority tests.
- The four focused Research Hub security modules passed locally (18 tests).
- Five selected historical-version tests failed identically at merge base
  `54e4ddf63abcca5e0d46f71f7505f03650e4aefe` and candidate
  `24d8abc91b802d8091566a1e5273cdcbc0eb092c`.
  This proves **only those five** were pre-existing failures.
- The earlier backend test collection discovered 655 tests and nine neural modules failed collection due to missing PyTorch support.
- A broad original suite additionally requires archived WordPress and historical-release fixtures; it is not covered by this backend-only comparison.

## Repeatable Mac run

Run from the root of the existing **Workspace feature-branch checkout** on the Mac with its Python 3.12 virtual environment:

```bash
git fetch origin main
git pull --ff-only
source .venv/bin/activate
python -m unittest discover -s scripts/tests -p 'test_rhprod05_*.py' -v
python scripts/rhprod05_run_backend_diff.py \
  --collection-log workspace-backend-collection.log \
  --output-dir "$HOME/Documents/Sustainable-Catalyst/RH-PROD-05-regression-$(date -u +%Y%m%dT%H%M%SZ)"
```

The comparison command creates a **new** private evidence directory containing `baseline.xml`, `candidate.xml`,
`baseline.log`, `candidate.log`, and `regression-diff.json`.

The runner archives the merge-base revision of `HEAD` versus `origin/main` and `HEAD`
into independent disposable directories, runs with the *same interpreter* and a restricted
environment (no inherited database URLs, credentials, or token variables), passes
`PYTHONPATH` separately for each checkout, and compares identities and outcomes.

A collection log must explicitly identify the nine known missing-neural-dependency test
modules. Each excluded module is recorded; missing modules and collection/runner errors
**fail closed**. The runner does not install dependencies, modify an active checkout,
contact a production host, or use an external AI agent.

Exit status 0: no new failures detected **within this bounded comparison**.
Exit status 1: blocking candidate changes/missing test coverage detected.
Exit status 2: incomplete or inconclusive execution.

An exit status of 0 is **not** deployment authorization. The report includes
`release_certified: false`. A complete gate still needs the scientific-runtime suite,
historical contracts, the Workspace-to-Research identity/auth bridge, real-account
staging acceptance, persisted project and document tests, figures/exports, and a populated,
restorable backup with verified rollback.

## Classification rules

- Historical failures are retained in the report, including a hash of diagnostic messages.
- A previously passing or skipped test that fails is a new regression.
- A changed existing failure requires review.
- Missing candidate tests or newly skipped tests are blocking.
- New candidate-only failures are blocking.
- The runner reports the number and filenames of excluded modules; no broad implicit skip is permitted.

## Release safety

- PRs #16 and #23 remain draft.
- Do not merge, alter production routing, prune Docker resources, run production migrations,
  or treat an empty Research candidate-database restore as populated recovery evidence.
- Keep the existing deployed Workspace login and Reporting Studio surface intact.
