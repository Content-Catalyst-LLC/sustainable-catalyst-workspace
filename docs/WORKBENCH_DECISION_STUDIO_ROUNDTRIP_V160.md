# Workspace v1.6.0 — Workbench & Decision Studio Round-Trip Workflows

## Workbench
Supports explicit context packages for calculation, simulation, optimization, engineering analysis, data transformation, and sensitivity analysis. Compatible outbound context includes datasets, analyses, evidence, documents, and exports. Typed returns include calculations, simulation/optimization results, transformed datasets, engineering reports, and sensitivity results.

## Decision Studio
Supports decision packets, scenario comparison, tradeoff analysis, option assessment, risk review, and decision briefs. Compatible outbound context includes decisions, evidence, sources, analyses, documents, and exports. Typed returns include decision packets, scenario sets, recommendations, risk registers, decision briefs, and outcome plans.

## Governance
Only stable IDs are placed in outbound URLs. Context packages require explicit export. Returns must match the local project, handoff, and destination before materialization. Returned artifacts preserve specialist metadata in the Workspace record and receive deterministic `derived-from` traceability to the selected outbound context. No automatic execution, upload, commit, AI, telemetry, canonical specialist mutation, or schema migration is introduced.

Storage 35, Project `sc-workspace-project/20.0`, and Export `sc-workspace-project-export/20.0` remain frozen.
