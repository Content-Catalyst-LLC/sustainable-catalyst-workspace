# Workspace v2.20.0 — Monte Carlo & Uncertainty Quantification

- Adds a dedicated internal `python-monte-carlo-uq` runtime.
- Eight bounded operations: seeded Monte Carlo weighted sums, bootstrap intervals, Latin-hypercube sampling, correlated-normal simulation, empirical summaries, rank-correlation sensitivity, linear variance contribution, and scenario envelopes.
- Migration 020 adds durable uncertainty-analysis receipts with sample counts, seeds, intervals, summaries, sensitivity metadata, artifact lineage, and SHA-256 result identity.
- Preserves the corrected v2.19 job-result readback contract.
- No arbitrary code execution, client-selected runtime URLs, host ports, privileged containers, or Docker-socket access.
