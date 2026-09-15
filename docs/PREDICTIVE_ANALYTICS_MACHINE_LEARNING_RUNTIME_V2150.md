# Predictive Analytics & Machine Learning Runtime — v2.15.0

Runtime: `python-sklearn-predictive`

The v2.15 specialist runtime provides eight fixed ML operations over bounded tabular payloads. Training is deterministic when the same dataset, feature order, target, hyperparameters, preprocessing configuration and random seed are supplied. Numeric features are required in this release; categorical preprocessing is deliberately deferred.

Model artifacts are trusted outputs only: the ML service serializes its own fitted estimators, Workspace persists those bytes with SHA-256 lineage, and the public execution contract never deserializes arbitrary user-provided model binaries.
