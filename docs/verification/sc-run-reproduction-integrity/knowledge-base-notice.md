# Proposed Knowledge Base verification notice

Workspace Backend 3.83.0 run tracking was verified in an isolated PostgreSQL environment using the
implementation at commit `6c5dfee4803ace1dbb2aca563b0bb80f3bfbdd2b) and synthetic data.
The checks covered revision-pinned inputs, job state and retry, output registration, and persisted
provenance. An independent replay reproduced five synthetic descriptive statistics within absolute
and relative tolerances of 1 × 10⁻¹². In that baseline, an `exact` reproduction receipt reports
registered-digest equivalence.

A separate corrective candidate at commit `362354da4bbbf5a7bc0bcf2db572dcb5f5ebfad5` passed isolated
PostgreSQL checks for independent artifact SHA-256 and byte-count verification. With the candidate,
corrupted, missing or unavailable artifacts produce an incomplete receipt even when registered
digests match. A byte-verified receipt describes the outputs read at verification time.
The candidate remains under review in PR #79.

Staging and production deployment verification, connected Lab, Library and Research workflows,
and scientific validation remain unverified. The deployed Workspace product version remains
unassigned.
