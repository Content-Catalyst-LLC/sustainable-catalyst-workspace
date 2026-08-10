# Sustainable Catalyst Workspace v0.46.1 — Validation Report

Release date: 2026-08-10

## Scope

v0.46.1 is a schema-stable visual patch to v0.46.0 — Workspace Import & Interchange. It corrects the Workspace editorial header rule from 2px to 4px on desktop and mobile while retaining the complete v0.46.0 interchange feature set.

## Visual contract

- Active `.scw-editorial-header-bar`: 4px desktop.
- Mobile `.scw-editorial-header-bar`: 4px.
- Legacy 12px desktop / 9px mobile bar remains absent from the active v0.46.1 asset.
- 4px matches recurring Sustainable Catalyst hero/header top-rule treatment; smaller card rules commonly remain 3px.

## Data and governance boundary

- Storage schema: 35 → 35.
- Project schema: 20.0 → 20.0.
- Project Export schema: 20.0 → 20.0.
- Notebook Workspace schema: 8.0 → 8.0.
- No canonical data rewrite.
- No new server storage or network behavior.
- v0.46.0 staged import, no-silent-overwrite, provenance, and portable-project copy semantics retained.

## Working-tree validation

- 561 Python contract tests passed.
- 26 JavaScript runtime tests passed.
- 5 PHP runtime tests passed.
- 60 JavaScript syntax checks passed.
- 9 PHP syntax checks passed.
- 124 current JSON schema/release records parsed by the release validator.
- Dedicated v0.46.1 release validator passed.

## Package gate

A fresh-extraction validation is performed after repository and WordPress ZIP creation. The final release bundle is published only after that package gate succeeds.

## Fresh-extraction result

The repository ZIP and standalone WordPress plugin ZIP were extracted into clean directories after packaging.

- Dedicated release validator: PASS.
- Python contracts: 561 passed.
- JavaScript runtime tests: 26 passed.
- PHP runtime tests: 5 passed.
- JavaScript syntax: 60 files passed.
- PHP syntax: 9 files passed.
- Packaged plugin version: 0.46.1 confirmed.
- Packaged active header rule: 4px desktop / 4px mobile confirmed.
- Release artifact SHA-256 verification: PASS.
