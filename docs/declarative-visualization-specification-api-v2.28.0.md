# Workspace v2.28.0 — Declarative Visualization Specification API

Workspace now stores analytical visualization meaning as a backend-authoritative, renderer-neutral specification rather than as browser-specific chart configuration.

## Bounded view grammar

The v1 grammar supports table, line, area, bar, scatter, histogram, box, heatmap, distribution, uncertainty-band, timeline, network, and metric views. Scenes use single, grid, or dashboard layouts. Linked views can filter, highlight, or select across views.

## Provenance

Sources may reference Workspace artifacts, datasets, execution runs, scientific receipts, or bounded inline rows. Server-side compilation resolves supported Workspace references to revision/fingerprint/SHA-256 provenance pins before the specification is persisted.

## Authority boundary

The backend validates the grammar, creates the canonical SHA-256 specification fingerprint, owns revision history, and emits immutable receipts. Browser code renders the specification but does not define its analytical meaning. Renderer-specific executable fields and arbitrary-code execution are rejected.
