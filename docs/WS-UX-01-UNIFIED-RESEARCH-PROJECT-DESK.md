# WS-UX-01 — Unified Research Project Desk

**Date:** 2026-11-07  
**Product decision:** Workspace is the user's **primary research project environment**. Library, Research, Lab, Workbench and Publishing must be integrated capabilities within a single project context, not a chain of mandatory site changes.  
**Code:** `feature/ws-project-desk-unified-research`; source candidate only.  
**Status:** Additive Workspace shell UX candidate built; Research output persistence, cross-application workflow and live publishing remain **unavailable** until RH-PUB-01B–01F. No production deployment.

## Why this is needed

The current standalone Workspace shows technical sections such as Research Map, Library Bridge, Integrated Project, Research Objects, Datasets, Models & Runtimes, Visual Analysis and Session Timeline. While each may expose capabilities, the experience does not explain what a user should do with a **research project** or show a governed **research output** linked to that project. Research output control is presently blocked by the private identity/publication bridge; users should not have to manually copy sources, switch among multiple app accounts, or chase objects across technical screens.

## Target user experience

Users log into the existing Workspace account, select **one project**, and stay there. The project is the organizing boundary for:

1. **Overview:** project summary, the next meaningful action, linked sources/analyses/outputs, reviewer deadlines and actionable publishing status.
2. **Sources & evidence:** Library search/add-source **within** Workspace via a permissioned reference picker; document/citation identity, provenance and rights remain Library-owned.
3. **Analysis & figures:** invoke existing Workbench, Lab, Site Intelligence and Research methods in the project context; display outputs in Workspace while retaining backend provenance and source version.
4. **Research outputs:** one child output workspace per scientific report, policy brief, paper or public research overview. Each has its own manuscript, methods, figures, sources, revisions, rights, reviews and public release pointer.
5. **Review & publish:** select exact output revision, preview public release, request review, approve when authorized, publish/unlist/withdraw through the **Research-authoritative private service**; Workspace shows confirmed receipts/status rather than local optimistic flags.
6. **History & advanced tools:** project-level change timeline, reproducible execution records and optional specialist views for power users.

This is one visual project workflow, not six separately administered applications. Users retain deep links to Library or Research when advanced features require them, but ordinary source selection, revision, review and publishing should be embedded or shown in a same-origin panel.

## Implemented in WS-UX-01 shell candidate

- An additive **Project Desk** panel at the top of `standalone/index.html`, using `standalone/project-desk.js` and scoped `standalone/project-desk.css`.
- Projects selector reads the existing canonical Workspace project state and chooses a project through the existing project-list click handlers; **no new project-state authority or session handling**.
- New project opens the existing Workspace project creation form in the same context, not an unconnected modal.
- Restructures the existing live Workspace DOM panels into tabbed **Overview, Sources & evidence, Analysis & figures, Research outputs, History, Advanced tools, Projects**. Moves existing DOM nodes rather than rendering static copies, preserving backend implementations, event listeners, and feature modules.
- Existing sidebar destinations reveal the correct tab before their scroll behavior runs, avoiding navigation regressions.
- Research outputs shows **explicitly unavailable**, not invented counts or fictitious publish buttons. This page does not call private Research, create a Research output, or publish.
- Existing Library reference path remains available, as do local project creation and the current integrated analysis/evidence views.
- Scoped black/white/pure-red styling, keyboard-focus outlines, horizontal tab overflow on mobile. No brand-wide CSS changes.

## Architectural rule for completing the experience

**Workspace = integrated project UI and coordination. Research = authoritative scientific content, revisions, review/public release. Library = canonical source authority.** Users see only one coherent project experience, with the backends invoked behind a secured identity/session proxy.

- **One account:** reuse the existing Workspace session and certified `RH-PUB-01A` private introspection; no separate Research password.
- **One project identity:** Workspace's `project_id` is the parent and is mapped durably/immutably to Research Project; Research entries are child output workspaces. An output's lifecycle does not affect sibling outputs.
- **One user-facing action:** clicking “Attach source,” “Create output,” “Revise,” “Submit,” or “Publish” triggers a backend operation under the current verified project context, with clear status and actionable errors.
- **No silent data duplication:** pass permission-checked source IDs and versions, not raw files pasted between applications by the user.
- **No false publication authority:** WordPress Research Bridge is read-only. WordPress Publications blog posts are separate editorial objects. Private research publication occurs only after a reviewed, rights-cleared, approved Research release.
- **No fake UI:** disabled actions must say which dependency is missing and why, and authenticated authorization must always be enforced server-side.

## Phased implementation plan

| Work | Output | Gate |
| --- | --- | --- |
| WS-UX-01A | Project Desk top-level tabbed shell; existing project picker, existing panels/links and honest unavailable output state | Local source + CI + UX acceptance |
| RH-PUB-01A | Existing Workspace login → project-scoped Research identity/owner authority | Source built; real-account Contabo acceptance pending |
| RH-PUB-01B | Research output child-workspace registry; Workspace output list and create action | Requires certified owner binding for live writes |
| WS-UX-01B | Embedded Library source picker; inside-project research output editing and evidence panels | Library adapter & owner permissions |
| RH-PUB-01C + WS-UX-01C | Exact-revision review, rights checks, approved publish/unlist/withdraw, receipts, confirmed Workspace status | Research release service; review and audit |
| WS-UX-01D | Usability/accessible end-to-end acceptance for Wexford and Metrics | Two-owner isolation, logout replay, private/public separation, rollback |

## Acceptance walkthrough (one place, not multiple sites)

1. Sign into Workspace and select **Wexford ERW**.
2. Open **Sources & evidence** and add a Library source from inside the same project view; source remains Library-owned and linked by ID/version.
3. Open **Analysis & figures** and view or launch a Wexford calculation; figures retain run IDs, units and provenance.
4. Open **Research outputs**, select the scientific report, policy brief or public overview. Edit each independent output; no manual upload needed to move among services.
5. Use **Review & publish** within Workspace to publish only the reviewed public overview; policy brief and scientific report remain private. The Research public catalog shows only the approved output.
6. Return to the project overview and see Research-confirmed version, public URL and audit receipt. Withdraw and verify the public page updates safely.
7. Another account, revoked session, rights failure or private service outage cannot access/publish the output.

**This is the acceptance definition, not currently proven behavior.**

## Production safeguards

Do not deploy this shell candidate merely because it passes source tests. Validate the exact currently deployed Workspace shell/version and overlays: `standalone/index.html` on `main` declares v3.83.0 while older onboarding docs describe v3.70.0. Confirm actual runtime image, output of `window.SCWorkspaceStandaloneRuntime`, WordPress/standalone route and cache versions, and test all sidebar routes, project create/select, keyboard/mobile navigation and legacy local project recovery. Identity/private APIs must remain disabled until their separate acceptance. Preserve rollback to previous shell assets and don't replace the public Research WordPress plugin.
