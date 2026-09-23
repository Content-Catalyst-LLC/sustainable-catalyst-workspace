# Workspace v3.16.0 Release Notes

**Release:** Quantitative Reconstruction & Scientific Analysis Handoffs  
**Baseline:** v3.15.0  
**Migration:** `047_quantitative_reconstruction_scientific_analysis_handoffs.sql`

Workspace v3.16.0 adds a reproducible bridge between investigative evidence and Sustainable Catalyst's scientific/analytical runtimes. Researchers can define a quantitative reconstruction, pin canonical source/evidence inputs, declare assumptions and parameters, hand the package to Workbench, Research Lab, Catalyst Analytics R, or Platform Core, and bind returned results back to the originating research context.

The handoff is reference-first. Canonical claims, events, entities, documents, testimony, spatial/media/source objects, datasets, scientific objects, and other inputs remain governed by their existing authorities. Workspace stores their references and optional fingerprints rather than creating replacement evidence bodies.

### New durable objects
- `QuantitativeReconstructionHead` / `QuantitativeReconstructionRevision`
- `QuantitativeInputBinding`
- `QuantitativeAnalysisHandoff`
- `QuantitativeResultBinding`
- `QuantitativeAnalysisSnapshot`

### Release gates
- 236 typed endpoints (+18 over v3.15)
- v3.16 focused tests: 7
- immediate-parent v3.15 tests: 6
- migration 047
- rollback baseline v3.15.0
- Catalyst Analytics R 2.2.0 preserved

### Safety / epistemic boundary
A statistical, simulation, causal, optimization, or other quantitative output is an analytical artifact, not an automatically accepted fact. Human review remains required before analytical results are used as findings or conclusions.
