# Workspace v0.80.0 — Release Candidate I

## Purpose

v0.80.0 establishes the formal Release Candidate boundary for Sustainable Catalyst Workspace. The product is feature-frozen at this point: remaining pre-1.0 work is limited to defect repair, deployment hardening, compatibility, recovery, documentation, certification, packaging, rollback, and field-validation findings.

## Frozen canonical baseline

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project Export schema: `sc-workspace-project-export/20.0`
- Canonical object types: source, evidence, dataset, analysis, decision, document, export
- No schema migration is introduced by v0.80.0.

## Release Candidate gate

The Review → Release Candidate surface verifies runtime release identity, the `release-candidate` stage, the canonical schema freeze, required hardening surfaces and modules, the Public Beta III closure contract, recovery/disaster simulations, and the inherited accessibility/performance final audit.

The source/package release gate separately verifies current-release identity, the WordPress 8 KiB plugin-header boundary, the enqueue dependency graph, Security & Privacy Audit II, Accessibility & Performance Final Audit, Public Beta III Defect Closure, package-integrity requirements, and the presence of a rollback artifact in the release bundle.

## Feature-freeze policy

Allowed work during the RC phase:

- defect fixes;
- production/deployment hardening;
- browser/device compatibility fixes;
- accessibility fixes;
- performance fixes;
- recovery and rollback fixes;
- security/privacy fixes;
- documentation/help corrections;
- packaging/reproducibility corrections;
- fixes arising from explicit field validation.

Not allowed before 1.0 without deliberately reopening product scope:

- a new canonical data subsystem;
- a new project/object schema generation;
- a new live collaboration model;
- background sync;
- hidden scoring or behavioral telemetry;
- automatic publication, institutional ingestion, or AI mutation.

## Human certification remains open

A passing automated RC gate is not production certification. The production WordPress smoke test, rollback rehearsal, assistive-technology testing, measured contrast/zoom/reflow and physical touch testing, a representative multi-hour large-project session, a real two-device continuity exercise, and real shared/institutional handoffs remain explicit human field work.
