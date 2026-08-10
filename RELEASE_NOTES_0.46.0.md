# Sustainable Catalyst Workspace v0.46.0 — Workspace Import & Interchange

Released: 2026-08-10

## Added

- Workspace Interchange v2 (`sc-workspace-interchange/2.0`).
- Explicit interchange profiles for Workspace JSON, Obsidian-ready Markdown, Notion-style CSV, Zotero/CSL JSON, and portable Workspace Projects.
- Deterministic browser-local profile detection for common Markdown front matter, CSV column conventions, CSL JSON, and Workspace interchange packages.
- Multi-profile project export from Import & Interoperability.
- Import reports that preserve profile, fingerprint, object count, and review-required boundaries.
- Three new interchange schemas and a pure JavaScript interchange helper runtime.

## Preserved boundaries

- Storage remains 35; Project and Project Export remain 20.0.
- Every imported artifact is staged and reviewed before commit.
- Imported objects receive new local IDs and imported provenance.
- Portable Projects import as new local Project copies.
- No external metadata lookup, automatic AI, automatic trust elevation, server import pipeline, or silent canonical overwrite.

## Visual correction

The editorial black rule at the top of the Workspace page is now 2px on desktop and mobile, replacing the legacy 12px/9px rule so it matches the visual weight used elsewhere on Sustainable Catalyst.
