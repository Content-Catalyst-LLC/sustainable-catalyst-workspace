# Workspace v3.22.0.1 — Neural Training Runtime Production Repair

v3.22.0.1 preserves the v3.22 bounded neural training feature set while repairing the production-only PyTorch 2.10 optimizer initialization failure captured by the Contabo live smoke test.

The runtime remains declarative, CPU-only, non-root, read-only, and bounded. The repair does not enable arbitrary Python, packages, serialized models, checkpoints, resume, or GPU execution.

The repair contract is:

1. `torch._dynamo` is imported before FastAPI request dispatch.
2. Adam optimizer integration is warmed once during process import.
3. Optimizer construction is serialized to avoid first-use initialization races.
4. NumPy is explicitly installed and reported by health.
5. The production deployer must submit a real training job before promotion succeeds.
