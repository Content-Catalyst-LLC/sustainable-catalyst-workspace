# Sustainable Catalyst Workspace v0.67.0 — Validation Report

## Release

- **Version:** 0.67.0
- **Previous version:** 0.66.1
- **Release:** Cross-Device Continuity & Sync Hardening
- **Storage schema:** 35
- **Project schema:** `sc-workspace-project/20.0`
- **Project Export schema:** `sc-workspace-project-export/20.0`
- **Canonical schema migration:** none

## Cross-device continuity gates

- Explicit project enrollment remains required for sync.
- Sync pushes use a client operation ID and a server revision precondition.
- Exact retries of a completed operation ID are replay-safe and do not create another server revision.
- Pending operations surviving a browser restart are marked interrupted and reconciled explicitly.
- Remote application creates a local `sync-safety` restore point before replacing the local project state.
- Device migration packages import only as a new local copy.
- Device identity, account profile, REST nonce, and recent-tool history are excluded from migration packages.
- Sync enrollment is not transferred by device migration.
- Exact duplicate migration packages are blocked by source-project + SHA-256 fingerprint history.
- Manual account backup cannot replace an active `sync-head` and bypass its revision precondition.
- Current Project 20.0 snapshots are accepted by account backup/sync storage.
- Background sync, automatic enrollment, automatic conflict merge, and silent last-write-wins remain disabled.

## Automated validation

- **871 / 871 Python contract tests:** PASS
- **133 JavaScript files syntax-validated:** PASS
- **48 / 48 JavaScript runtime suites:** PASS
- **11 PHP files syntax-validated:** PASS
- **6 / 6 PHP runtime suites:** PASS
- **WordPress enqueue dependency graph runtime:** PASS
- **378 JSON files parsed:** PASS
- **v0.67.0 release validator:** PASS
- **WordPress 8 KB plugin-header metadata gate:** PASS
- **Release-diff whitespace gate:** PASS

## Presentation regression

The inherited v0.64.1 desktop-layout Chromium matrix passes at 1600, 1440, 1280, 1024, 768, and 390 px with no page-level horizontal overflow or character-width text collapse.

The inherited v0.65 field-use Chromium matrix passes at 1600×1000, 1440×1000, 1280×900, 1024×800, 834×1112, 768×1024, 430×900, 390×844, and 844×390. Dense field-use presentation remains bounded and touch targets retain the narrow-layout hardening.

## Important boundary

This release hardens explicit continuity and recovery. It does **not** introduce background synchronization, automatic uploads, automatic device enrollment, automatic conflict resolution, or server-side device identity tracking. Physical cross-device smoke testing with two real signed-in browsers remains a deployment/field-validation step.
