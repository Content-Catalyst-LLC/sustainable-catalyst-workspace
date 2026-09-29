# Workspace v3.36.0 — Computer Vision & Remote Sensing Neural Runtime

Extends Workspace's governed PyTorch runtime into bounded image and multiband remote-sensing analysis. Adds eight operations for image contracts, dataset projection, declarative CNN forward/inference, deterministic tiling, band projection, and spectral-index computation.

No database migration. Rollback baseline: v3.35.0. Neural operation registry: 77.

## Boundaries
- no arbitrary Python/model code or external package loading
- no opaque serialized PyTorch modules
- no filesystem, URL, bucket, or external raster reads
- CPU remains the safe default; existing device policy governs accelerators
- remote-sensing outputs are derived analytical objects and are not labeled observed evidence
