# Workspace v3.47.0 — Original-Language Text & Corpus Workspace Foundation

## Purpose
Begin the post-decoupling linguistics line by exposing the existing bounded multilingual backend as a host-neutral Workspace capability.

## Architectural principle
Original language is the primary representation.

Translation, transliteration, normalization, transcription, annotation, OCR, and HTR are derived transformations. Each derived representation must identify its parent and transformation explicitly.

Workspace does not automatically:
- detect a language;
- translate text;
- transliterate text.

## New host-neutral module
`app/linguistics/workspace-original-language-corpus-v3470.js`

The module provides:
- explicit language-tagged original text objects;
- derived representation objects;
- bounded corpus assembly;
- original/derived validation;
- backend request construction;
- text identity;
- Unicode normalization;
- text segmentation;
- corpus profiling;
- corpus segment indexing;
- transformation lineage.

## Existing backend runtime reused
v3.47.0 intentionally builds on the v3.46.0 runtime:

`sc-workspace-multilingual-text-corpus-runtime/1.0`

Backend routes:
- `/v1/multilingual-text-corpus-runtime`
- `/v1/multilingual-text-corpus-runtime/operations`
- `/v1/multilingual-text-corpus-runtime/execute`

New Workspace integration profile:
- `/v1/original-language-corpus-workspace`

## Module registry
The module is registered through logical asset ID:

`workspace.linguistics.original-language-corpus`

Neither WordPress nor standalone hard-codes the module file URL. Both resolve the same shared asset through the host-agnostic asset manifest.

## Production baseline
The v3.46.10.0 decoupled production baseline remains binding:
- WordPress optional;
- WordPress owns no canonical application state/project logic;
- standalone remains independently bootable;
- backend remains canonical server authority;
- shared assets maintain checksum parity.

## Migration
- database migration: none
- browser-storage schema migration: none

## Next
v3.48.0 — Linguistic Annotation & Corpus Structure Workspace.
