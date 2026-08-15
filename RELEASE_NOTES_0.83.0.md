# Sustainable Catalyst Workspace v0.83.0 — Live Production Certification & Release Sign-Off

Release date: 2026-08-14

v0.83.0 remains inside the Workspace pre-1.0 feature freeze. It does not introduce a new canonical product subsystem or migrate project data.

## Release focus

- Add **Review → Production Sign-Off**.
- Require explicit human evidence for every live-production validation item left open by the v0.80–v0.82 Release Candidate line.
- Export a production sign-off certificate that is `signed-off` only when every required field check and final attestation is complete.
- Keep incomplete exports explicitly `pending` rather than implying certification.
- Carry v0.82.1 as the immediate rollback package and predecessor.
- Preserve the installer-lineage protections introduced in v0.82.1 while making the v0.82.1 validator safe to inherit under later releases.

## Required live checks

The sign-off gate covers public-page and REST identity, anonymous/authenticated use, cache coherence, representative local-project preservation, rollback/reinstall, assistive technology, zoom/reflow/touch, long-session large-project use, two-device continuity, shared review, and institutional handoff.

## Claim boundary

Workspace does not perform or infer these checks. It does not automatically certify production, purge caches, execute rollback, inspect project content, or sign on behalf of an operator.

## Compatibility

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project Export schema: `sc-workspace-project-export/20.0`
- Schema migration required: no
- Previous release: v0.82.1
- Rollback target: v0.82.1
