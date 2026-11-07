# Handoff — Workspace coordination across Library, Research, Publications and Press

**Date:** 2026-11-07
**Status:** Owner-approved product boundaries, documentation only.
**Canonical ADR:** [Platform Core: Publications / Press / Research ownership](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-platform-core/blob/main/docs/PRODUCT-BOUNDARIES-PUBLICATIONS-PRESS-RESEARCH-2026-11-07.md)

## Workspace's responsibility

**Workspace coordinates projects, people, milestones, review obligations, permissions, and deliverables across applications.** It must not become another Library, Research science editor, WordPress CMS, or Press distribution engine.

The approved cross-product journey:
- **Library:** discover, save and preserve source references.
- **Research:** assemble evidence into investigations, analyses, scientific figures, reports and findings.
- **Workspace:** manage project scope, collaborators, milestones, reviews and project status throughout this lifecycle.
- **WordPress Publications:** create and publish blog posts, editorial articles and public summaries linked to approved source research.
- **Press:** the eventual public-facing identity of existing Engagement & Communications, for institutional/media communication, press releases, newsletters and outreach.

This is a conceptual flow, **not a claim that these handoffs currently work end-to-end**.

## Routing boundaries

- Workspace project != Research investigation != WordPress post != Press communication campaign. Link these objects using distinct stable IDs, version identifiers and product authorities.
- Workspace records a handoff's intent, origin, destination, ownership, approval state and return status; it does not copy a private document into a public URL or transfer raw credentials.
- WordPress retains authority for editorial blog posts and permalinks. Research retains research/scientific source lineage; Library retains evidence originals; Press retains institutional communication objects and privacy/delivery controls.
- Handoff operations require the existing authorized identity and tenant scope, explicit disclosure/rights approval for public data, and audit logging where supported.
- Corrections, withdrawals, and blocked approvals must be visible to project coordinators rather than silently republishing.

## Product decision vs deployment

**Approved:** The naming/function split between WordPress Publications and Press (as Engagement & Communications' future public label).

**Not authorized:** Retitling or renaming repositories/WordPress menus, any real SSO federation, changing public/private Research API routes, duplicating accounts, transferring sources, enabling outbound mail, or promoting unreviewed content.

A separate reviewed implementation plan must define acceptance checks, permission mapping, rollback and deployment for any actual integration.
