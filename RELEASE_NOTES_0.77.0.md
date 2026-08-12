# Sustainable Catalyst Workspace v0.77.0 — Security & Privacy Audit II

Release date: 2026-08-11

## Purpose

Re-audit Workspace after the v0.62–v0.76 hardening sequence and make the security/privacy boundary inspectable without exposing research content in the diagnostic report.

## Included

- privacy-minimized localStorage and sessionStorage metadata audit;
- secure-context and embedded-context checks;
- count-only inspection of script-readable Workspace-like cookies;
- detection of unclassified Workspace-owned browser stores without exporting key names or values;
- release-time REST permission split validation;
- release-time dynamic-code primitive scan (`eval`, `new Function`, `document.write`);
- release-time embedded secret/private-key literal scan;
- release-time network-boundary check for the current JavaScript runtime;
- WordPress plugin-header and enqueue dependency gates retained;
- Security & Privacy surface extended with Audit II findings and source-gate status;
- stale v0.59 metadata in the complete local portability export corrected to use the installed Workspace version.

## Explicit non-claims

Audit II is not a penetration test, formal security certification, cryptographic review, malware scanner, or claim of application-level localStorage encryption. It does not inspect HttpOnly cookie contents, automatically remediate findings, delete data, upload data, disclose research, or mutate canonical Workspace projects.

## Schema stability

- Storage: 35
- Project: `sc-workspace-project/20.0`
- Project Export: `sc-workspace-project-export/20.0`
- Migration: none
