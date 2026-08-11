# Sustainable Catalyst Workspace v0.66.0 — Validation Report

## Release

**Import, Export & Backward-Compatibility Hardening**

v0.66.0 is an interchange-safety release over v0.65.0. It does not migrate canonical Workspace data.

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Project Export schema: **sc-workspace-project-export/20.0**
- Schema migration: **none**

## Automated validation

| Gate | Result |
|---|---:|
| Python contract tests | **851 / 851 PASS** |
| JavaScript runtime suites | **47 / 47 PASS** |
| PHP runtime suites | **6 / 6 PASS** |
| JavaScript syntax checks | **130 PASS** |
| PHP syntax checks | **10 PASS** |
| JSON parse sweep | **367 PASS** |
| v0.66.0 release validator | **PASS** |
| WordPress enqueue dependency graph | **PASS** |
| Release-diff whitespace check | **PASS** |
| v0.64.1 desktop-layout regression fixture | **PASS** |
| v0.65.0 field-use Chromium matrix | **PASS** |

## Import/export compatibility coverage

The v0.66 runtime classifier and fixture suite validate Workspace Project and Project Export schema generations:

`1.0, 2.0, 3.0, 3.1, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0`.

The runtime suite checks every supported raw Project schema and every supported Project Export envelope. Dedicated fixtures also exercise early, intermediate, and current exports (1.0, 3.1, 10.0, 20.0), source-ID collision, malformed export material, and future v21 rejection.

Project Import is verified as a staged process. File selection parses/classifies the candidate but does not append a project to Workspace state. Explicit commit normalizes the supported candidate, generates a new local project ID, and records an import event.

## Future-schema and overwrite boundary

The release validator and runtime tests confirm:

- future Workspace Project/Project Export schemas are blocked rather than downgraded;
- unknown/malformed Project Import material is blocked;
- Project Import never automatically commits on file selection;
- imported projects are always new local copies;
- source-ID collision does not cause overwrite;
- no server import pipeline or external schema/network lookup exists;
- Portable Project and Interchange families remain assigned to their purpose-built review surfaces.

## Export round-trip gate

The v0.66 compatibility runtime validates a stable project projection before writing a normal Project Export. Tests cover both an equivalent round trip and deliberate drift introduced by a test normalizer.

The emitted receipt records before/after FNV-1a fingerprints for deterministic drift comparison. The release contract explicitly states that this fingerprint is **not** a cryptographic checksum, authentication mechanism, encryption primitive, or security signature.

## Existing storage compatibility

The release manifest records the inherited browser-state migration lineage from Storage 1 through Storage 35. This is separate from Project Import: Storage envelopes continue through the Workspace state-loader migration path and are not accepted as project files.

## Preserved runtime hardening

- The v0.64.1 WordPress enqueue-cycle regression test remains **PASS**.
- The accessibility-script self-dependency remains absent.
- The v0.64.1 desktop-layout fixture remains **PASS** at 1600, 1440, 1280, 1024, 768, and 390px.
- The v0.65 field-use fixture remains **PASS** at 1600×1000, 1440×1000, 1280×900, 1024×800, 834×1112, 768×1024, 430×900, 390×844, and 844×390 short landscape.
- v0.65 contextual Lab handoffs remain present.
- v0.63 browser compatibility fallbacks and v0.62 persistence/recovery hardening remain present.

## Field-validation boundary

Automated compatibility tests establish the documented Workspace schema contracts; they do not certify arbitrary files created outside those contracts. Production validation should still use real historical exports where available and exercise populated current projects in Safari, Firefox, Chrome, and Edge.

Particularly important production smoke cases are:

- selecting a legacy project file leaves the local project list unchanged until commit;
- committing the staged file creates a distinct local ID;
- an ID-colliding import cannot overwrite the original;
- a future schema remains blocked;
- current populated projects can export after a successful round-trip check;
- Portable Project and Interchange packages remain routed through their dedicated workflows.

## Release status

**PASS — ready for packaging, deployment, and backward-compatibility field validation.**

## Package validation

Final packaging additionally passed:

- repository ZIP integrity;
- WordPress plugin ZIP integrity;
- release-bundle ZIP integrity;
- SHA-256 verification for every payload listed in `SHA256SUMS`;
- macOS installer shell syntax;
- packaged-repository v0.66.0 release validator;
- packaged-repository **851 / 851** Python contract regression;
- packaged v0.66 import/export compatibility runtime;
- packaged registry migration runtime;
- packaged WordPress enqueue dependency-cycle runtime.
