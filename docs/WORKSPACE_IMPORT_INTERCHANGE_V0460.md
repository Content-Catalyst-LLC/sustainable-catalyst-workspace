# Workspace v0.46.0 — Workspace Import & Interchange

v0.46.0 consolidates the earlier Import & Interoperability and Share/portability foundations into a clearer exchange layer. It remains local-first and schema-stable: Storage 35, Project 20.0, Project Export 20.0, Notebook Workspace 8.0, and Notebook Export 8.0 do not change.

## Interchange profiles

- **Workspace structured JSON** — `sc-workspace-interchange/2.0`, preserving canonical objects plus explicit traceability relationships in a portable copy.
- **Obsidian-ready Markdown** — deterministic Markdown with YAML front matter and Workspace object identifiers; Markdown imports recognize a bounded set of common front-matter fields.
- **Notion-style CSV** — flattened object rows with common `Name`, `Tags`, `URL`, `Notes`/`Content`, and Workspace-specific columns. Import uses deterministic column aliases.
- **Zotero / CSL JSON** — exports only bibliographic information already recorded on Source/provenance records and stages imported CSL items as draft Source objects. No DOI or metadata lookup occurs.
- **Workspace portable Project** — uses the existing SHA-256-fingerprinted Project package and import-as-new-copy boundary.

## Import boundary

Files are read in the browser. Workspace detects a compatibility profile deterministically, shows the staged objects, and requires an explicit commit. Imported records receive imported provenance and new local object IDs. Interchange never upgrades imported content into verified evidence automatically.

## Export boundary

External profiles are deterministic transformations of recorded Workspace data. They do not modify canonical source records, perform network enrichment, or imply that an external tool will round-trip every Workspace-specific field.

## Visual alignment

The Workspace editorial header rule is reduced from the legacy 12px desktop / 9px mobile treatment to a consistent 2px black rule, matching the restrained line weight used across the broader Sustainable Catalyst site.
