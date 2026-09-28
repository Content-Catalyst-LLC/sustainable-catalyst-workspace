# Workspace v3.27.0 Validation Report

## Result
PASS for the v3.27.0 release delta.

## Neural regression line
- 64 passed / 0 failed across v3.20.0 through v3.27.0 neural tests.
- 9 new v3.27 inference/prediction-provenance tests passed.
- PyTorch runtime: 31 bounded neural operations.

## Repository-wide backend regression
- 278 passed.
- 46 failed, matching the established historical release-lineage/version/migration baseline.
- No new failure category introduced by v3.27.0.
- 83 inherited Pydantic schema-shadow warnings.

## Static and contract validation
- Backend service version 3.27.0: PASS.
- Neural runtime version 3.27.0: PASS.
- Typed client: 291 endpoints, no missing OpenAPI operations: PASS.
- Python compilation: PASS.
- WordPress PHP lint: PASS.
- Hardened numeric UID/read-only/no-new-privileges contract: PASS.
- PyTorch 2.10.0 and NumPy 2.2.6 pins retained: PASS.

## New v3.27 behaviors covered
- Exact regression inference.
- Binary probability, decision threshold, confidence, and entropy.
- Multiclass softmax probabilities, class selection, margin, and entropy.
- Inference rejects observed targets and routes outcome comparison to evaluation workflows.
- Prediction artifacts are canonically fingerprinted and tamper-detecting.
- Prediction inspection accepts only governed fingerprint-valid artifacts.
- Checkpoint/model lineage is enforced.
- Row IDs are governed and included in inference-dataset provenance.
- Prediction/evidence/evaluation boundaries are explicit.

## Release engineering
- Database migration: none.
- Rollback baseline: Workspace v3.26.0.
- Contabo deployer includes pre-switch hardened inference certification and post-switch prediction artifact/receipt verification.

## Clean release-bundle certification
- Release bundle payload applied to an untouched v3.26.0 repository snapshot: PASS.
- Applied release-delta files: 38.
- Reconstructed-tree validator: PASS.
- Reconstructed-tree typed-client check: PASS (291 endpoints).
- Reconstructed-tree neural suite: 64 passed / 0 failed.
- PHP and deployer shell syntax: PASS.
- All distributable ZIP archives: integrity PASS.
- Package hygiene: PASS; no `.env`, `.git`, bytecode, or test-cache leakage (`.env.example` remains intentionally allowed).
