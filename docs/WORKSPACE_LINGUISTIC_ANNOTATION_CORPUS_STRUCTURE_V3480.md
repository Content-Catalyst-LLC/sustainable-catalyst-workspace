# Workspace v3.48.0 — Linguistic Annotation & Corpus Structure Workspace

## Purpose
Add structured linguistic annotation and hierarchical corpus organization on top of the v3.47.0 original-language foundation.

## Host-neutral module
`app/linguistics/workspace-linguistic-annotation-corpus-structure-v3480.js`

The module provides:
- annotation objects;
- annotation layers;
- hierarchical structure nodes;
- corpus-structure objects;
- Unicode code-point offset validation;
- backend execution for six bounded operations.

## Annotation contract
Annotations explicitly record:
- document ID;
- layer ID;
- annotation type;
- start/end offsets;
- label/value/features;
- annotation method;
- annotator;
- confidence;
- source reference;
- parent annotations for derived annotation lineage.

Supported provenance methods:
- human
- rule
- model
- imported
- other

Offsets use `unicode-code-point`, matching Python string indexing and avoiding UTF-16 ambiguity for multilingual text.

## Corpus structure
Structure nodes support:
- document
- section
- paragraph
- sentence
- token
- custom

Each node records document, parent, order, span, label, attributes, and source reference.

The backend validates:
- document references;
- layer references;
- offsets;
- parent containment;
- missing parents;
- cross-document parent errors;
- structure cycles;
- annotation derivation references.

## Bounded backend operations
- `workspace.linguistics.annotation-validate`
- `workspace.linguistics.annotation-span-index`
- `workspace.linguistics.annotation-layer-profile`
- `workspace.linguistics.document-structure`
- `workspace.linguistics.corpus-structure`
- `workspace.linguistics.annotation-lineage`

## Dependency
The module depends on:
- `core.api`
- `workspace.linguistics.original-language-corpus`

The original-language module remains at its v3.47.0 module version and is reused rather than duplicated.

## Production architecture
The v3.46.10.0 decoupled production baseline remains mandatory:
- one WordPress script entry point;
- WordPress owns no canonical state/project/module logic;
- standalone is independently bootable;
- backend remains canonical server authority;
- shared module assets maintain checksum parity.

## Migration
- database migration: none
- browser-storage schema migration: none

## Next
v3.49.0 — Translation, Transliteration & Parallel Alignment Workspace.
