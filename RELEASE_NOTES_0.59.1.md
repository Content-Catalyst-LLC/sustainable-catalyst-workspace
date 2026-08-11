# Sustainable Catalyst Workspace v0.59.1 — Focused Application Shell & Route Isolation

## Purpose

v0.59.1 is a surgical interface correction after visual review of the public Workspace page. It keeps the v0.59.0 Security, Privacy & Data-Portability Audit intact while preventing the application from reading as one extremely long stacked document.

## Changes

- Force-hide inactive top-level Workspace routes with an explicit theme-resistant `[hidden]` rule.
- Preserve the five primary areas: Start, Projects, Research, Review, Exchange.
- Add a focused internal Research tool switcher: Overview, Search, Collections, Cross-project, Tasks, Assistant, Citations, Composition.
- Show one Research tool surface at a time.
- Keep the Research overview concise and operational.
- Preserve selected canonical research context while moving between Research tools.
- Add keyboard navigation across the Research tool strip.
- Apply the inactive-route isolation in print as well as screen layouts.
- Retain the 4px editorial header treatment.

## Data boundary

No Storage, Project, Project Export, or Notebook schema changes are introduced. Route isolation is presentation-only and does not move, copy, rewrite, publish, delete, or infer canonical research.

## Retained v0.59.0 boundary

The Security, Privacy & Data-Portability Audit remains unchanged, including browser-local threat-model disclosures, complete Workspace-prefixed portability export, and typed-confirmation verified browser-local deletion.
