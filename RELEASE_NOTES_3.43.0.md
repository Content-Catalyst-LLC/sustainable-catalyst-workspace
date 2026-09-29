# Workspace v3.43.0 — Model Serving, Batch Inference & Research Deployment

Workspace v3.43.0 adds a governed model-serving and research-deployment layer above reproducible neural model packages, distributed workers, and accelerator resource governance.

## Added
- Immutable serving-model bindings to verified Workspace neural model packages.
- Runtime/device compatibility evaluation without external runtime image resolution.
- Bounded synchronous serving inference with prediction provenance.
- Deterministic batch-inference planning and bounded sequential batch execution.
- Research-deployment readiness evaluation, manifests, and operator-declared receipts.
- Workspace artifact-store persistence and receipt lineage for all eight new object classes.

## Boundaries
- No public endpoint provisioning.
- No infrastructure mutation.
- No client-supplied serving URLs, deployment URLs, container images, registry credentials, or deployment tokens.
- No arbitrary code, packages, serialized PyTorch modules, or external model reads.
- Predictions and deployment records remain `isObservedEvidence=false`.

## Continuity
- Baseline and rollback: v3.42.0.
- Neural registry: 125 → 133 operations.
- Database migration: none.
- The repaired cumulative Workspace frontend is preserved.
