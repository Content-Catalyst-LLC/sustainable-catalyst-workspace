# Workspace v0.36.0 — Notebook Synthesis & Citation Workspace

## Purpose

v0.36.0 adds a provenance-safe synthesis layer to Research Notebook. It transforms only material the user explicitly selects and stores the output as a reviewable project-bound synthesis record.

## Synthesis outputs

### Outline
Orders selected material into a structured heading-and-bullet draft while retaining source markers when recorded citation context exists.

### Citation Pack
Collects only citation information already present in notebook bibliographic context or Workspace object provenance. Workspace does not fill missing author, publisher, date, DOI, locator, or URL fields by inference.

### Source Matrix
Creates a reviewable matrix containing material type, title, recorded source context, excerpt, and citation marker for each selected item.

### Evidence Summary
Assembles selected excerpts and research material into an evidence-oriented review surface. It does not assign hidden strength, confidence, or credibility scores.

### Research Synthesis Draft
Assembles selected material into a readable draft in selection order, with carried citation markers where available. The result remains a draft for human interpretation and editing rather than an automatically asserted conclusion.

## Selection and provenance

Selections may include Research Notebook blocks and canonical Workspace objects. Every synthesis stores its selected references, normalized entries, citations, content, and timestamps. Removing a synthesis does not remove its source material.

## Document materialization

A user may explicitly create a normal Workspace Document from a synthesis. This produces a derivative; the synthesis and selected notebook/object material remain in place.

## Schemas and migration

- Workspace storage schema: 31 → 32
- Project schema: 16.0 → 17.0
- Project export schema: 16.0 → 17.0
- Notebook Workspace schema: 4.0 → 5.0
- Notebook schema: remains 3.0
- Notebook block schema: remains 3.0
- Notebook export schema: 4.0 → 5.0
- Notebook synthesis schema: 1.0
- Notebook synthesis export schema: 1.0

## Governance boundaries

v0.36.0 does not introduce automatic synthesis, automatic source selection, citation guessing, evidence scoring, semantic inference, source fetching, automatic AI, automatic upload, automatic publication, or mutation of selected source material.

## Foundation for v0.37.0

This release creates the explicit selection and citation substrate for **v0.37.0 — Grounded Notebook Assistance**, where questions can be asked against material the user deliberately chooses and responses must remain reviewable drafts with citations constrained to that grounding set.
