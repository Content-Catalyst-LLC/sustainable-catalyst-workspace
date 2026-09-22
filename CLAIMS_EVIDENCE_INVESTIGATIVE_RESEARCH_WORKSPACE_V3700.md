# Workspace v3.7.0 — Claims, Evidence & Investigative Research Workspace

Workspace v3.7.0 adds a backend-authoritative investigative research layer on top of the v3.6 visual research workspace.

## Core design

- Versioned investigative statements: claim, finding, hypothesis, question.
- Immutable evidence links with source-reference and fingerprint pinning.
- Explicit statement relationships for contradiction, competing hypotheses, support, dependency, refinement, duplication, and general relationship mapping.
- Investigation graph overlays v3.6 visual-research nodes and edges so evidence can connect directly to visualizations and other Workspace research objects.
- Immutable investigation snapshots capture the graph and its deterministic SHA-256 fingerprints.
- Unified Research Project Context includes investigative statement/evidence/relation counts and the investigative graph projection.

## Human-judgment boundary

Evidence relationships and statement relationships are recorded as explicit human-authored assertions. Workspace does not automatically decide truth, rank evidence, score claims, or make decisions. Contradiction and competing-hypothesis relationships are graph facts about the research record, not automated conclusions about which proposition is correct.

## Platform Core boundary

The release projects the existing Platform Core linked research session through the inherited v3.6 visual graph. It does not invent a new Core mutation endpoint for investigative statements. Specialist objects remain authoritative in their existing layers and are referenced rather than copied.

## Release lineage

- Prior release: v3.6.0 — Platform Core Visual Analysis & Research Object Workspace
- Migration: `038_claims_evidence_investigative_research_workspace.sql`
- Rollback baseline: v3.6.0
- Expected typed endpoint count: at least 87
