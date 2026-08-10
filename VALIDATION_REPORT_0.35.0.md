# Sustainable Catalyst Workspace v0.35.0 Validation Report

Release: **v0.35.0 — Notebook-to-Workspace Intelligence**  
Date: **2026-08-09**

## Result

**PASS** — the v0.35.0 source tree passed the release validator and complete inherited/new contract and runtime checks used by the release package.

## Release contract validation

The v0.35 validator confirmed:

- plugin/runtime version 0.35.0;
- manifest lineage 0.34.0 → 0.35.0;
- storage migration 30 → 31;
- Project schema 15.0 → 16.0 and Project Export 15.0 → 16.0;
- Notebook Workspace 4.0, Notebook 3.0, Block 3.0, Notebook Export 4.0, Promotion 1.0;
- seven explicit promotion destinations: Source, Evidence, Dataset, Analysis, Decision, Document, Canvas;
- visible project-bound promotion lineage;
- multiple derivatives per notebook block;
- object and Canvas promotion runtime contracts;
- explicit destination selection and preservation of original notebook material;
- no automatic promotion, hidden classification, or AI requirement;
- preservation of v0.33 Source Capture and v0.34 collection/link state;
- Project REST v16 and account-persistence compatibility window;
- registry migration lineage and preserved v0.34 history;
- canonical Knowledge Library route and retained accessibility hardening.

## Test results

- Python contract tests: **438 passed**
- JavaScript runtime tests: **14 passed**
- PHP runtime tests: **5 passed**
- JavaScript syntax checks: **30 passed**
- PHP syntax checks: **9 passed**
- JSON release/schema files parsed: **79 passed**

## Promotion-specific runtime coverage

The v0.35 notebook promotion runtime verifies:

- current Notebook Workspace/Notebook/Block/Export/Promotion schema identifiers;
- the complete explicit destination set;
- deterministic interface suggestions without automatic execution;
- multiple promotion records from one notebook block;
- object and Canvas target kinds;
- portable export of promotion lineage;
- explicit governance flags in notebook export;
- preservation of original block content; and
- normalization of legacy v0.34/v0.33 notebook material into the v0.35 container.

## Packaging gate

The release bundle must additionally pass ZIP integrity, SHA-256 verification, and a fresh extracted-repository validation before distribution. Those checks are performed after this report is included in the package.
