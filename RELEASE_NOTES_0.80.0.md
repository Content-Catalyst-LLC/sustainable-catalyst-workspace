# Sustainable Catalyst Workspace v0.80.0 — Workspace Release Candidate I

Release date: 2026-08-11

## Purpose

Establish the formal Workspace Release Candidate boundary after Public Beta III defect closure. v0.80.0 freezes product scope and canonical schemas while adding release-candidate identity, certification/field-validation visibility, package/rollback requirements, and fail-closed RC release gates.

## Included

- Review → Release Candidate surface;
- explicit `release-candidate` runtime stage;
- feature-freeze policy: defect fixes, certification, deployment, compatibility, recovery, security, documentation, packaging, rollback, and field-validation fixes only;
- canonical Storage 35 / Project 20.0 / Project Export 20.0 freeze;
- inherited Public Beta III closure, recovery/disaster, Security & Privacy Audit II, and Accessibility & Performance Final Audit gates;
- privacy-minimized RC report and manual field-QA checklist export;
- required rollback artifact in the release bundle;
- WordPress 8 KiB metadata and dependency-cycle gates remain mandatory;
- no new product subsystem and no schema migration.

## Manual field validation still required

Production WordPress smoke testing, WordPress rollback rehearsal, assistive-technology testing, measured contrast/zoom/reflow/physical touch validation, representative multi-hour large-project use, real two-device continuity, and real shared/institutional handoffs remain human field-validation work.

## Schema stability

- Storage: 35
- Project: `sc-workspace-project/20.0`
- Project Export: `sc-workspace-project-export/20.0`
- Migration: none
