# Workspace v0.58.0 Validation Report

Release: **Scale, Performance & Large-Project Hardening**  
Date: 2026-08-10

## Architecture boundary

- Storage schema remains **35**.
- Project schema remains **sc-workspace-project/20.0**.
- Project Export remains **20.0**.
- Notebook Workspace remains **8.0**.
- Scale diagnostics are advisory only.
- Derived-index caching and bounded rendering do not mutate canonical research.
- No automatic deletion, archival, compaction, or migration was introduced.
- The 4px editorial header treatment is retained.

## First clean-extraction package gate

The provisional repository ZIP and standalone WordPress ZIP were extracted into clean directories and validated from the packaged bytes:

- 716 Python contract tests — PASS
- 38 JavaScript runtime tests — PASS
- 5 PHP runtime tests — PASS
- 98 repository JavaScript syntax checks — PASS
- 9 repository PHP syntax checks — PASS
- 168 current JSON schema/release records parsed — PASS
- Dedicated v0.58.0 release validator — PASS
- WordPress package version `0.58.0` — PASS
- 60 packaged plugin JavaScript files syntax-clean — PASS
- 4 packaged plugin PHP files syntax-clean — PASS

## Scale-specific coverage

Validation exercises derived-index cache reuse and invalidation, bounded 120-record result windows, manual window expansion, storage-pressure classification, synthetic large-project fixtures, advisory performance budgets, registry lineage, REST contract discovery, and non-destructive governance boundaries.

## Final sealed-artifact gate

The repository was repacked with this report embedded and the complete clean-extraction gate passed again: 716 Python contract tests, 38 JavaScript runtime tests, 5 PHP runtime tests, 98 JavaScript syntax checks, 9 PHP syntax checks, 168 current JSON records, and independent WordPress package validation at version 0.58.0 with 60 JavaScript and 4 PHP files syntax-clean.
