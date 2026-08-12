# Sustainable Catalyst Workspace v0.75.0 — Validation Report

Release: **v0.75.0 — Institutional Package & Handoff Validation**

## Release gate

**PASS**

## Automated validation

- Python contract tests: **929 / 929 PASS**
- JavaScript syntax checks: **160 PASS**
- JavaScript runtime suites: **56 / 56 PASS**
- PHP syntax checks: **11 PASS**
- PHP runtime suites: **6 / 6 PASS**
- JSON records parsed: **432 PASS**
- v0.75.0 release validator: **PASS**
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
- v0.75.0 institutional validation matrix

The v0.75.0 institutional-validation fixture passed at:

- 1440 × 1000
- 1024 × 800
- 834 × 1112
- 768 × 1024
- 430 × 900
- 390 × 844

No page-level horizontal overflow was detected. Institutional-validation controls retain a 44 px minimum action height in the narrow-screen fixture.

## Institutional transfer assertions

Validated behavior includes:

- frozen institutional research-package scope must exactly match its disclosure manifest before transfer;
- receiving institution or organization and transfer purpose are explicit transfer requirements;
- source-project revision drift is detected and presented as a stale-snapshot attention state;
- stale frozen packages require explicit human acknowledgement before export;
- Catalyst Intelligence promotion packages are checked for manifest consistency and SHA-256 payload integrity;
- returned institutional receipts must match a locally prepared handoff and source project;
- exact duplicate fingerprinted receipts are blocked;
- unsigned receipts remain reviewable but require explicit human acknowledgement before commit;
- chronologically unusual receipts require explicit review before commit;
- validation reports are privacy-minimized and exclude project content, record titles, purpose text, recipient labels, source URLs, account identity, and device identifiers;
- readiness remains an explainable checklist rather than a numeric readiness or quality score.

SHA-256 validation is used for integrity verification of promotion/receipt payloads where present. Package validation does not establish institutional identity, authorization, or legal acceptance.

## Backward-compatibility boundary

Older institutional research-package construction remains supported. v0.75.0 applies the new recipient, purpose, scope, freshness, and integrity requirements at the validation/freeze/export boundary rather than making historical package data unreadable.

## Canonical schema status

No migration is introduced by v0.75.0.

- Storage: **35**
- Project: **sc-workspace-project/20.0**
- Project Export: **sc-workspace-project-export/20.0**

## WordPress package metadata

Required plugin metadata remains within WordPress's bounded header-read window:

- `Plugin Name:` begins at byte 13
- `Version:` begins at byte 117
- `Author:` begins at byte 136
- `Requires at least:` begins at byte 215
- `Requires PHP:` begins at byte 241
- `Description:` begins at byte 262

Expected uploaded version: **0.75.0**.

## Product boundary

v0.75.0 does not create:

- an institutional tenant inside Workspace;
- organization membership or server permissions;
- automatic package upload;
- automatic ingestion into Catalyst Intelligence;
- automatic source-project mutation or conversion;
- a remotely writable institutional project;
- automatic acceptance of stale or unverifiable transfer artifacts.

Production field validation should still exercise a real two-system handoff with a representative institutional package and receipt on the deployed WordPress site. Passing the Workspace validation gate does not certify the receiving institution or receiving system.
