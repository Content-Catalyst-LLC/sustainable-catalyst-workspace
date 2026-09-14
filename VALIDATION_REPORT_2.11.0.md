# Workspace v2.11.0 Validation Report

## Release
**Workspace v2.11.0 — Python Scientific Compute Runtime & Execution Engine**

## Release-specific gates
- Structural validator: PASS
- Python compilation: PASS
- Targeted backend + v2.9 telemetry regression + v2.10 compliance + v2.11 scientific compute tests: **52 passed, 2 stale lineage assertions deselected**
- WordPress PHP syntax: **31/31 files PASS**
- VPS deployment script `bash -n`: PASS
- Current JSON manifest/schema/registry parse: PASS

The two deselected historical assertions require the current predecessor to remain v2.8.0 and v2.9.0. v2.11 correctly advances predecessor/rollback to **v2.10.0**; functional v2.9 telemetry and v2.10 compliance tests remain in the release gate.

## Historical suite
- **1,182 passed / 126 failed**
- Failures are historical release-identity debt: older tests assert earlier plugin versions, asset filenames, README headings, or predecessor identities remain current.
- No v2.11 scientific-compute test failed.

## Scientific runtime invariants
- Seven finite `workspace.compute.*` operations are registered.
- NumPy, Pandas, SciPy, and SymPy engine versions are exposed by the compute catalog.
- Arbitrary Python source, shell, subprocess, host-filesystem, Docker-socket, and privileged execution are not exposed by the compute engine.
- Operation-specific size/complexity limits fail closed.
- Compute jobs emit progress and check durable cancellation state between stages.
- Successful results are canonical JSON content-addressed artifacts.
- Execution-run-linked compute artifacts participate in run reproducibility lineage.
- Compute receipts bind job, operation, engine/version, request fingerprint, artifact SHA-256, bytes, and wall time.
- Worker container is read-only-root, cap-drop ALL, no-new-privileges, 2 CPU, 2 GiB, 256 PID, bounded tmpfs.
- Storage 35 / Project 20.0 / Export 20.0 / Notebook 3.0 remain unchanged.
