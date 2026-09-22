# Workspace v3.11.0 — Documentary Evidence, Testimony & Statement Analysis Workspace

## Purpose

Workspace v3.11.0 extends the investigative research stack with backend-authoritative documentary and testimony objects that preserve provenance and explicit human interpretation boundaries.

## New canonical objects

- Versioned documentary records with source references and source fingerprints.
- Locator-preserving document excerpts pinned to a document revision fingerprint.
- Versioned testimony/statement records with speaker-entity references and source provenance.
- Explicit documentary context links to statements, events, entities, evidence references, and scientific objects.
- Explicit testimony-to-testimony relations for corroboration, contradiction, contextualization, challenge, duplication, or relatedness.
- Immutable documentary-analysis snapshots.

## Analysis surfaces

- Documentary graph over the v3.10 entity/timeline graph.
- Descriptive coverage and consistency diagnostics.
- Counts of explicit testimony relations and context-link relation types.
- Identification of documents/testimonies lacking contextual linkage or speaker binding.

## Epistemic boundaries

The runtime does not automatically:
- score witness or source credibility,
- determine truth,
- rank evidence,
- infer culpability or motive,
- infer undocumented relationships,
- select a preferred narrative.

All contradiction/corroboration relations remain explicit human-authored assertions.

## Storage

Migration 042 creates eight additive PostgreSQL tables:
- workspace_investigation_document_heads
- workspace_investigation_document_revisions
- workspace_investigation_document_excerpts
- workspace_investigation_testimony_heads
- workspace_investigation_testimony_revisions
- workspace_investigation_documentary_context_links
- workspace_investigation_testimony_relations
- workspace_investigation_documentary_snapshots

## API

v3.11.0 adds 19 typed operations under `/v1/documentary-evidence-workspace`, increasing the typed endpoint surface from 131 to 150.
