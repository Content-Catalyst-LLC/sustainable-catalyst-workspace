# Sustainable Catalyst Workspace v0.55.0 — Validation Report

Release: **v0.55.0 — Workspace API & Embed Foundation**  
Date: **2026-08-10**

## Working-tree gate

The release working tree passed:

- 677 Python contract tests
- 35 JavaScript runtime tests
- 5 PHP runtime tests
- 87 JavaScript syntax checks
- 9 PHP syntax checks
- 157 current JSON schema/release records parsed
- dedicated v0.55.0 release validator

## Contract boundary

Validated behaviors include:

- schema-stable Storage 35 / Project 20.0 / Project Export 20.0 / Notebook Workspace 8.0
- durable `scw://project/{project_id}/{kind}/{id}` references
- durable references are identifiers, not authorization tokens
- canonical Workspace research remains private/browser-local by default
- public REST contract exposes API/embed capabilities only and does not enumerate or return user research
- public-readonly projections require explicit user creation
- static JSON API envelope export
- self-contained read-only embed descriptor/renderer
- no live server project API or server project discovery
- no automatic publication, refresh, AI action, or canonical mutation
- deterministic recursive projection fingerprint payload
- v0.54.0 Shared Review & Research Handoff retained as immediate predecessor
- 4px Workspace editorial header rule retained

## First packaged-artifact gate

A clean extraction of the provisional repository ZIP reproduced the full release gate:

- 677 Python contract tests
- 35 JavaScript runtime tests
- 5 PHP runtime tests
- 87 JavaScript syntax checks
- 9 PHP syntax checks
- 157 current JSON schema/release records

The independently extracted WordPress package reported `Version: 0.55.0` and passed syntax validation for **52 JavaScript files** and **4 PHP files**.

## Final repacked-artifact gate

After the first receipt was embedded and the repository was repacked, a second clean extraction reproduced the complete release gate:

- 677 Python contract tests
- 35 JavaScript runtime tests
- 5 PHP runtime tests
- 87 JavaScript syntax checks
- 9 PHP syntax checks
- 157 current JSON schema/release records

The final release is sealed only after this completed report is embedded and the sealed repository ZIP passes one additional clean-extraction verification. The WordPress plugin package is independently verified at `Version: 0.55.0` with 52 JavaScript files and 4 PHP files syntax-clean.
