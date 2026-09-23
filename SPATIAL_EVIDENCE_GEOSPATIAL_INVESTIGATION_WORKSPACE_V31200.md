# Workspace v3.12.0 — Spatial Evidence & Geospatial Investigation Workspace

Adds a backend-authoritative, provenance-aware spatial evidence layer across entities, events, documentary evidence, testimony, claims, evidence references, and scientific objects.

## Capabilities
- Versioned spatial observations with geometry/place references, coordinate-system identity, timestamps, source refs, and fingerprints.
- Explicit human-authored spatial context links and spatial relations.
- GeoJSON-compatible map projection without automatic geocoding.
- Documentary/entity/timeline graph overlay rather than duplicated canonical objects.
- Descriptive spatial consistency/coverage diagnostics.
- Immutable spatial investigation snapshots.

## Boundaries
No automatic geolocation inference, relationship inference, causal inference, truth determination, evidence ranking, culpability inference, or preferred narrative selection.

## Persistence
Migration `043_spatial_evidence_geospatial_investigation_workspace.sql` adds five additive PostgreSQL tables.
