# Workspace v3.16.0 — Quantitative Reconstruction & Scientific Analysis Handoffs

## Purpose
Workspace v3.16.0 turns investigative and research objects into explicit, reproducible quantitative-analysis packages while keeping canonical evidence authority in Workspace and execution authority in specialist products.

## Core model
- **Quantitative reconstruction**: versioned analytical question, objective, method class, assumptions, parameters, and project identity.
- **Input binding**: reference-first binding from a canonical research/evidence object into a reconstruction, optionally pinned to an object fingerprint and explicit transformation specification.
- **Analysis handoff**: reproducible package for Workbench, Research Lab, Catalyst Analytics R, or Platform Core. Workspace records intent and lineage; it does not silently execute the specialist analysis.
- **Result binding**: returned specialist result reference, fingerprint, status, and notes attached back to the originating reconstruction/handoff.
- **Manifest / graph / diagnostics**: deterministic project-level views of reconstruction inputs, handoffs, returned outputs, and incomplete lineage.
- **Snapshot**: immutable fingerprinted capture of manifest, diagnostics, and optional graph.

## Supported method classes
`descriptive`, `statistical`, `simulation`, `optimization`, `causal`, `time-series`, `spatial`, `uncertainty`, `custom`.

## Specialist destinations
`workbench`, `research-lab`, `catalyst-analytics-r`, `platform-core`.

## Boundary rules
Workspace remains orchestration and provenance infrastructure. The release does not automatically execute analyses, transform canonical evidence, rank evidence, determine truth, infer culpability, or convert an analytical result into a factual conclusion.

```text
automaticAnalysisExecution          = false
automaticEvidenceTransformation     = false
automaticEvidenceRanking            = false
automaticTruthDetermination          = false
automaticCausalityInference          = false
automaticCulpabilityInference        = false
coreExecutesSpecialistProvider       = false
workspaceOrchestratesHandoffs        = true
```

## API surface
v3.16 adds 18 typed operations:
1. Workspace profile
2. Store reconstruction
3. List reconstructions
4. Get reconstruction
5. Reconstruction revisions
6. Create input binding
7. List input bindings
8. Create analysis handoff
9. List analysis handoffs
10. Get analysis handoff
11. Update handoff status
12. Create result binding
13. List result bindings
14. Project analysis manifest
15. Project analysis graph
16. Project diagnostics
17. Create immutable snapshot
18. List snapshots

## Persistence
Migration `047_quantitative_reconstruction_scientific_analysis_handoffs.sql` is additive and introduces six tables. Rollback runtime baseline is v3.15.0; migration 047 may remain without affecting a v3.15 runtime because v3.15 does not reference these tables.
