# Workspace v3.14.0 — Source Reliability, Provenance & Evidence Integrity Workspace

## Purpose
Workspace v3.14.0 adds a backend-authoritative source-integrity layer above the v3.13 media-provenance workspace. It records source identity, provenance events, custody events, human-authored integrity assertions, source-to-evidence bindings, descriptive diagnostics, and immutable snapshots without replacing canonical source content owned by specialist systems.

## Durable objects
- Versioned source records and source revisions
- Provenance events
- Chain-of-custody events
- Human-authored integrity assertions
- Source-to-investigation/scientific-object evidence bindings
- Immutable source-integrity snapshots

## Epistemic boundaries
The workspace does not automatically score source reliability or credibility, determine authenticity, verify integrity, rank evidence, determine truth, infer culpability, or select a preferred narrative. Integrity assertions are recorded as explicit claims with status and basis; diagnostics identify missing or conflicting recorded metadata for human review.

## Cross-product integration
The source-integrity graph can overlay the v3.13 media provenance graph and is exposed in Unified Research Context. Source content remains reference-first and specialist-object authority is preserved.

## Release engineering
- Baseline: v3.13.0
- Migration: 045_source_reliability_provenance_evidence_integrity_workspace.sql
- Typed endpoints: 200 total (+18)
- Rollback runtime baseline: v3.13.0
