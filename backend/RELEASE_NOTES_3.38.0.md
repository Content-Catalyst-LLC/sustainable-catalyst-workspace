# Workspace v3.38.0 — Multimodal Neural Runtime

Workspace v3.38.0 composes the existing governed computer-vision and temporal-sequence runtimes into a bounded multimodal execution layer. The first supported pairing is vision + sequence, with explicit sample alignment contracts, dataset projection, declarative encoder composition, representation fusion, forward/inference execution, representation extraction, and similarity analysis.

- Neural operation registry: 85 → 93 operations.
- Database migration: none.
- Rollback baseline: Workspace v3.37.0.
- Fusion modes: concatenation and normalized weighted mean.
- External files/URLs/model downloads remain disabled.
- Arbitrary Python, dynamic imports, client packages, runtime URLs, and serialized Torch modules remain prohibited.
- Multimodal representations, similarities, and predictions are model-derived analytical outputs and are never marked as observed evidence.
