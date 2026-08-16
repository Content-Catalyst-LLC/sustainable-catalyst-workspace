# Workspace v2.0.0 — Connected Knowledge Workspace

Workspace v2.0.0 promotes the mature 1.x product line into a stable connected knowledge-work architecture. The release introduces a common v2 Connected Knowledge contract while retaining the proven v1 project, export, REST, developer, governance, and local-first boundaries.

## Major-version boundary

v2.0.0 is a major product release, but it does **not** force a storage migration. Storage schema 35, `sc-workspace-project/20.0`, and `sc-workspace-project-export/20.0` remain accepted as the canonical project-data contracts at launch. A future v2-native project schema must ship behind its own explicit compatibility and migration contract.

## Connected surfaces

The v2 context layer spans Workspace projects and research, Knowledge Library, Site Intelligence, Lab, Workbench, Decision Studio, Shared Review, Institutional Audit, Public Knowledge packages, and the Developer API. Specialist products keep canonical ownership and execution authority.

## Safety and governance

Context is ID/provenance-driven, explicit, and local-first. No automatic cross-product execution, context upload, return commit, AI invocation, hidden telemetry, or canonical mutation is introduced. Existing v1 REST routes remain supported.
