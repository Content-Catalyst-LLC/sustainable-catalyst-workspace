# Workspace v3.37.0 — Temporal Deep Learning & Sequence Models

Workspace v3.37.0 adds a governed temporal deep-learning and sequence-model foundation to the existing PyTorch runtime. It introduces bounded sequence tensor contracts, deterministic window planning, dataset projection, transparent tanh-RNN and GRU model specifications, forward/inference execution, hidden-state embeddings, and bounded next-step forecasts.

- Neural operation registry: 77 → 85 operations.
- Database migration: none.
- Rollback baseline: Workspace v3.36.0.
- External sequence/file/URL reads remain disabled.
- Arbitrary Python, dynamic imports, client packages, runtime URLs, and serialized Torch modules remain prohibited.
- Sequence predictions, embeddings, and forecasts are model-derived analytical outputs and are never marked as observed evidence.
