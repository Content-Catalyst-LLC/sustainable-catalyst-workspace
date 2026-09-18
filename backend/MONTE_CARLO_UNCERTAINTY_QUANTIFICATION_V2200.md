# Workspace v2.20.0 — Monte Carlo & Uncertainty Quantification

Workspace v2.20.0 extends the scientific runtime fabric with a server-configured, internal-only uncertainty-quantification runtime. It is designed for reproducible risk and sensitivity workflows rather than arbitrary scripting.

The runtime supports eight bounded operations: seeded Monte Carlo weighted-sum simulation, bootstrap confidence intervals, Latin-hypercube experimental design, correlated-normal sampling, empirical distribution summaries, Spearman rank-correlation sensitivity, independent linear variance contribution, and scenario envelopes.

Every completed uncertainty job persists its result artifact and an uncertainty-analysis receipt containing the runtime identity, operation, request fingerprint, sample count, random seed, interval metadata, summary metadata, sensitivity metadata, artifact ID, and SHA-256 digest.
