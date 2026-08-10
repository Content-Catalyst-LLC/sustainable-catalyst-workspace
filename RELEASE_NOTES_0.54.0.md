# Sustainable Catalyst Workspace v0.54.0 — Shared Review & Research Handoff

Release date: 2026-08-10

## Summary
v0.54.0 turns the v0.53 Collaboration Architecture into a controlled asynchronous research handoff workflow. A Workspace owner can select exactly which active project objects belong in a review, freeze that scope into a fingerprinted package, export it deliberately, and later import a response that must cryptographically match the originating package identity before it can be staged.

## New capabilities
- Browser-local Shared Review Handoff ledger.
- Explicit project + object scope selection; whole-project export is not the default.
- Frozen review package snapshots of selected Source, Evidence, Dataset, Analysis, Decision, Document, or Export objects.
- Relevant v0.53 collaboration ownership, comments, and proposals included as review context.
- Declared reviewer identities from the Collaboration Architecture policy.
- Deterministic package fingerprint and response-to-package matching.
- External reviewer package import and response export.
- Reviewer decision states: no decision, approved, changes requested.
- Response comments and proposed changes tied only to the review package's declared project/scope.
- Source-side response staging before commit.
- Explicit commit merges comments/proposals into the v0.53 Collaboration Architecture ledger.
- Imported proposal acceptance continues to record review state only and never applies a canonical project change.
- Unresolved project handoffs remain visibly unresolved rather than being rebound.
- Public `/wp-json/sc-workspace/v1/shared-review-handoff-contract` contract.

## Governance boundaries
- No live co-editing.
- No server collaboration tenant or organization membership.
- No automatic package transmission.
- No automatic response import.
- No silent canonical mutation.
- No automatic proposal application.
- Review packages are frozen portable copies of explicitly selected research objects; source Workspace records remain independently canonical.

## Compatibility
Storage remains 35. Project remains `sc-workspace-project/20.0`. Project Export remains `20.0`; Notebook Workspace remains `8.0`. The v0.53 Collaboration Architecture, v0.52 Research Tasks, v0.51 Grounded Research Assistant II, and all earlier capabilities remain available. The 4px editorial header rule is retained.
