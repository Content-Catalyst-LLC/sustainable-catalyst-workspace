# Sustainable Catalyst Workspace v0.74.0 — Validation Report

Release: **v0.74.0 — API, Embed & Integration Hardening**

## Release gate

**PASS**

## Automated validation

- Python contract tests: **915 / 915 PASS**
- JavaScript syntax checks: **156 PASS**
- JavaScript runtime suites: **55 / 55 PASS**
- PHP syntax checks: **11 PASS**
- PHP runtime suites: **6 / 6 PASS**
- JSON records parsed: **425 PASS**
- v0.74.0 release validator: **PASS**
- WordPress enqueue dependency graph: **PASS**
- Git release-diff whitespace check: **PASS**
- WordPress bounded 8 KiB plugin-header metadata check: **PASS**

## Browser / layout regression

The following automated Chromium fixtures passed:

- v0.64.1 desktop-layout recovery matrix
- v0.65.0 responsive / field-use matrix
- v0.70.0 Public Product Beta III journey matrix
- v0.71.0 first-run matrix
- v0.72.0 workflow-guidance matrix
- v0.73.0 shared-review hardening matrix
- v0.74.0 API/embed/integration hardening matrix

The v0.74.0 API/embed fixture passed at:

- 1440 × 1000
- 1024 × 800
- 834 × 1112
- 768 × 1024
- 430 × 900
- 390 × 844

No page-level horizontal overflow was detected and phone-scale integration actions retain the field-use touch-target requirement.

## Integration hardening assertions

Validated behavior includes:

- static read-only projection model retained;
- API payload cap: **128 KiB**;
- embed payload cap: **96 KiB**;
- descriptor integrity/drift verification before export/copy;
- trusted renderer-origin validation;
- HTTPS renderer origin required except localhost development;
- credentialed fetch disabled;
- `postMessage` bridge disabled;
- remote canonical mutation disabled;
- durable references treated as identifiers rather than authorization;
- malformed or policy-invalid embeds fail closed;
- failure rendering does not fetch project content;
- privacy-minimized integration safety reports contain diagnostics rather than research content.

The integrity fingerprint is a drift/corruption detection receipt. It is **not** a cryptographic signature, authentication mechanism, or authorization credential.

## Canonical schema status

No migration is introduced by v0.74.0.

- Storage: **35**
- Project: **sc-workspace-project/20.0**
- Project Export: **sc-workspace-project-export/20.0**
- Existing v1 durable-reference, projection, API-envelope, and embed schemas remain supported.

## WordPress package metadata

Required plugin metadata is within WordPress's bounded header-read window. In the validated source tree:

- `Plugin Name:` begins at byte 13
- `Version:` begins at byte 117
- `Author:` begins at byte 136
- `Requires at least:` begins at byte 215
- `Requires PHP:` begins at byte 241
- `Description:` begins at byte 262

Expected uploaded version: **0.74.0**.

## Product boundary

v0.74.0 does not create:

- a live server-side project API;
- remote project writes;
- credentialed embed fetches;
- a parent/embed `postMessage` trust bridge;
- automatic publication;
- automatic cross-origin trust;
- new canonical research objects;
- canonical schema migration.

Production field validation should still confirm the final WordPress page, trusted renderer URL, and representative external embedding contexts on the real deployment.
