# Computer Vision & Remote Sensing Neural Runtime — v3.36.0

## Operations
- `workspace.neural.vision-tensor-contract`
- `workspace.neural.vision-dataset-project`
- `workspace.neural.vision-model-summary`
- `workspace.neural.vision-forward`
- `workspace.neural.vision-infer`
- `workspace.neural.vision-tile-plan`
- `workspace.neural.remote-sensing-band-project`
- `workspace.neural.remote-sensing-index-compute`

## Model contract
The first vision adapter is `bounded-cnn`. Models are declarative: one to four Conv2D layers with explicit finite kernels/biases, same-padding, bounded channel counts, and a global-average-pooling linear head. No `torchvision`, PyG/DGL, dynamic imports, external checkpoints, or serialized modules are accepted.

## Remote sensing
Scenes use in-memory CHW tensors with explicit band names and optional scene/spatial metadata. The runtime can deterministically project named bands and calculate NDVI, NDWI, NBR, NDMI, or an explicit two-band normalized difference. CRS/bounds/transforms are fingerprinted as provenance; v3.36 does not perform reprojection, resampling, or external raster access.
