# Proposed Knowledge Base verification notice

Workspace Backend 3.83.0 was tested in an isolated PostgreSQL environment using synthetic data
and the implementation from source commit `6c5dfee4803ace1dbb2aca563b0bb80f3bfbdd2b`.
The checks covered run creation, revision-pinned inputs, job state and retry, registered outputs,
and persisted provenance. A second Workspace run reproduced the tested descriptive statistics
within absolute and relative tolerances of 1 × 10⁻¹². Artifact reads detected modified bytes.
Workspace's `exact` reproduction label reports a match between registered digests.

This verification applies to the tested backend and fixture. Staging, production, connected
Lab, Library and Research deployments, and scientific validity were outside the verified scope.
