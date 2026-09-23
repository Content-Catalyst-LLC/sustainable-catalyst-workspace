# Workspace v3.18.0 Validation Report

## Release

**Workspace v3.18.0 — Causal Analysis & Alternative Explanation Workspace**

## Final results

- Workspace version: **3.18.0**
- Baseline: **3.17.0**
- Migration: **049**
- Typed endpoints: **272**
- New v3.18 endpoints: **18**
- Missing OpenAPI operations: **0**
- v3.18 focused tests: **8/8 PASS**
- v3.17 immediate-parent tests: **7/7 PASS**
- Combined current/parent gate: **15/15 PASS**
- Python compilation: **PASS**
- Typed client generation/check: **PASS**
- PHP syntax: **PASS**
- JavaScript syntax: **PASS**
- Full v3.17 repository → v3.18 clean-room overlay: **PASS**
- v3.17 backend → v3.18 backend-only overlay: **PASS**
- Packaged backend overlay replay: **PASS**
- WordPress stable package identity: **PASS**
- Rollback baseline: **3.17.0**
- Catalyst Analytics R 2.2 preservation contract: **preserved by deployment gate**

## Epistemic / research boundaries

The v3.18 profile keeps all of the following false:

- `automaticCausalityInference`
- `automaticCausalDiscovery`
- `automaticConfounderSelection`
- `automaticIdentificationClaim`
- `automaticAlternativeExplanationRanking`
- `automaticEvidenceRanking`
- `automaticTruthDetermination`
- `automaticCulpabilityInference`
- `automaticNarrativeSelection`

Causal results are explicitly marked model-conditional. Alternative explanations are preserved as first-class records, and identification assumptions remain explicit researcher-authored objects.

Expected Pydantic warnings about request-model fields named `schema` remain warnings only and do not cause test failures.

## Release gate

`FINAL_V31800_RELEASE_VALIDATION=PASS`
