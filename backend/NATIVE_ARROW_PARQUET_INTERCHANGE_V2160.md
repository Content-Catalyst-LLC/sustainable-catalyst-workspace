# Workspace v2.16.0 — Native Arrow / Parquet Cross-Language Exchange

Adds an internal-only PyArrow interchange runtime with eight bounded operations for Arrow IPC and Parquet materialization, reading, conversion, schema inspection, and integrity verification. Binary artifacts are persisted through Workspace content-addressed storage with SHA-256 and schema fingerprints. No client filesystem paths, runtime URLs, package installation, or arbitrary code are accepted.
