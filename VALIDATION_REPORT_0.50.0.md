# Sustainable Catalyst Workspace v0.50.0 — Validation Report

Release: **Workspace Experience Consolidation**  
Date: **2026-08-10**

## Release boundary

- Storage schema: **35 → 35**
- Project schema: **20.0 → 20.0**
- Project Export schema: **20.0 → 20.0**
- Notebook Workspace schema: **8.0 → 8.0**
- New presentation schemas: `sc-workspace-experience/1.0`, `sc-workspace-experience-preferences/1.0`
- Canonical data migration: **none**
- Editorial header rule: **4px retained**

## Working-tree validation

- Release validator: PASS
- Python contract tests: **611 PASS**
- JavaScript runtime tests: **30 PASS**
- PHP runtime tests: **5 PASS**
- JavaScript syntax checks: **72 PASS**
- PHP syntax checks: **9 PASS**
- Current schema/release JSON records: **134 PASS**
- WordPress plugin JavaScript files: **42**
- WordPress plugin PHP files: **4**

## Experience-specific checks

- Five primary areas retained: Start / Projects / Research / Review / Exchange
- Comfortable and Compact density preferences remain browser-local
- Command palette requires explicit user invocation (`Ctrl/Meta + K`)
- `Alt + 1…5` only activates existing primary routes
- `/` only focuses an existing search control in the current view
- Help/terminology surface does not modify project state
- Mobile primary/context navigation uses horizontal scrolling rather than a five-row stack
- Primary Workspace controls maintain a 44px minimum interaction target
- Reduced-motion and forced-color behaviors retained
- 4px Sustainable Catalyst editorial header rule retained on desktop and mobile
- No automatic project creation, canonical mutation, AI invocation, upload, or background action introduced

## Package validation

Fresh extraction of the provisional repository and WordPress ZIPs passed the same release gates:

- Release validator: PASS
- Python contract tests: **611 PASS**
- JavaScript runtime tests: **30 PASS**
- PHP runtime tests: **5 PASS**
- JavaScript syntax checks: **72 PASS**
- PHP syntax checks: **9 PASS**
- Current schema/release JSON records: **134 PASS**
- Independent WordPress plugin version: **0.50.0 PASS**
- WordPress plugin JavaScript syntax: **42 PASS**
- WordPress plugin PHP syntax: **4 PASS**
- Repository ZIP integrity: PASS
- WordPress ZIP integrity: PASS

The repository is repacked after embedding this validation receipt and is subjected to a final clean-extraction gate before the outer bundle is sealed.

## Final repacked package gate

The final repacked repository ZIP was extracted into a clean directory after the validation receipt was embedded and passed the complete release gate again:

- 611 Python contract tests — PASS
- 30 JavaScript runtime tests — PASS
- 5 PHP runtime tests — PASS
- 72 JavaScript syntax checks — PASS
- 9 PHP syntax checks — PASS
- 134 current schema/release JSON records — PASS
- Dedicated v0.50.0 release validator — PASS
- Standalone WordPress package version `0.50.0` — PASS
- 42 packaged WordPress JavaScript files — syntax PASS
- 4 packaged WordPress PHP files — syntax PASS

This final gate validates the repacked repository artifact rather than only the working source tree.
