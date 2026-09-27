# Deploy Workspace Backend v3.23.0

The v3.23.0 backend deployer uses v3.22.0.2 as the rollback baseline and requires no database migration.

Before switching production it builds the new backend/worker/neural images and runs a hardened one-shot checkpoint certification: train, checkpoint inspect, resume, parent-lineage verification, and equivalence against uninterrupted training.

After promotion it submits a real Workspace neural training job, verifies the persisted checkpoint artifact, submits a resume job using that checkpoint, verifies the child lineage and separate Workspace checkpoint artifact, validates OpenAPI/runtime registry coherence, and rechecks container hardening.
