# Workspace v3.13.0 — Media Artifact, Image, Video & Derivative Provenance Workspace

## Purpose
Represent media evidence and its derivation chain as reproducible, source-pinned research objects while leaving canonical media bytes with their authoritative source/storage system.

## Durable objects
1. Media artifact heads and immutable revisions.
2. Frame/timecode/region locators.
3. Explicit parent→child derivative operations.
4. Media-to-research-context links.
5. Human-asserted media relationships.
6. Immutable media investigation snapshots.

## Provenance rules
Every artifact records a source reference, source fingerprint, content-hash algorithm and content hash. Derivative lineage records the parent, child, transformation type, parameters, tool/operation references, and an immutable fingerprint. A matching hash is surfaced for human review but is not silently treated as identity, authenticity, or duplication proof.

## Epistemic boundaries
Workspace does not automatically perform media similarity matching, derivative inference, authenticity determination, identity inference, causality inference, truth determination, evidence ranking, culpability inference, or narrative selection.
