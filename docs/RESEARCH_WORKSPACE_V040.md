# Sustainable Catalyst Workspace v0.4.0 — Research Workspace

## Purpose
v0.4.0 turns the generic v0.3.0 Workspace Object model into a research workflow without making research concepts part of every object.

## Research contract
Each project now owns a `sc-workspace-research/1.0` sub-contract. It references Workspace Object IDs instead of duplicating object content.

### Questions
Projects can maintain up to 100 research questions with priority (`low`, `normal`, `high`) and status (`open`, `answered`, `deferred`). One question may be active.

### Sources and reading queue
Research source capture creates a canonical `source` Workspace Object and may place it in a project reading queue. Queue status is `unread`, `reading`, or `read`.

### Evidence
Evidence extraction creates canonical `evidence` Workspace Objects. A research evidence-link record can connect an evidence object to the source object from which it was extracted.

### Claims
Projects can maintain up to 100 research claims. Claim status is `exploratory`, `supported`, `contested`, or `rejected`. Claims reference evidence object IDs; they do not copy evidence content.

## Privacy boundary
All research data remains browser-local. Cross-product handoffs carry stable project/object IDs only. Questions, claims, evidence text, notes, and source titles are not serialized into handoff URLs.

## Migration
Storage schema 3 is migrated to schema 4 by adding an empty normalized research contract to every v0.3.0 project. Existing objects, notes, activity, and IDs are retained.
