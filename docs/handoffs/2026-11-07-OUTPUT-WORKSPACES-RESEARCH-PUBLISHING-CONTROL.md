# Workspace handoff — Separate publication output workspaces and Research publishing controls

**Prepared:** 2026-11-07  
**Status:** Implementation contract, **not yet implemented/deployed**.  
**Research authoritative build spec:** RH-PUB-01, `docs/RH-PUB-01-PUBLICATION-OUTPUT-WORKSPACES.md` in the private Research repository (not public).  
**Cross-product names:** [Publications/Press ownership ADR](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-platform-core/blob/main/docs/PRODUCT-BOUNDARIES-PUBLICATIONS-PRESS-RESEARCH-2026-11-07.md).

## User-facing intent

In every Workspace parent project, add **Outputs & Publishing**. The user can create multiple distinct publication-output workspaces; each is a Research-owned `ResearchEntry` and `EntryWorkspace` under the shared Research project, not a new web server, account, independent Library or unrelated Workspace project.

Required example, **illustrative only**:
- Wexford ERW project — **Scientific Report** (private draft)
- Wexford ERW project — **Policy Brief** (in review; separate private/public revisions)
- Wexford ERW project — **Public Research Overview** (approved and published to public Research)

One output can be released, updated or withdrawn without affecting either sibling.

## Workspace screens

1. **Outputs & Publishing index**, sortable by output kind, owner, draft revision, review status, public version, last published time and current research-public visibility.
2. **Create output** dialog: title, output type, inherited parent Workspace project, optional source-collection link; defaults `private`.
3. **Open Research analysis** authenticated deep link to the correct Research entry workspace (no token in URL, no duplicate login).
4. **Review & Rights** screen for exact revision hash, source/license/attribution checks, required reviewer(s), requested changes and embargo.
5. **Public Preview** of the exact selected, approved revision and public metadata. Must distinguish Research public catalog from **WordPress Publications** post.
6. **Publishing** panel with user-triggered `Request review`, `Approve` (authorized reviewer), `Publish approved revision`, `Publish reviewed update`, `Unlist`, `Withdraw` and `View public`. Hide or disable controls for unauthorized states. Provide reason/confirmation for withdrawal and audit history.

## Control plane, not a second publishing source of truth

Workspace presents controls, initiates approved intents and displays **Research-confirmed outcomes**. Research checks the caller identity/owner/tenant through a certified server-side identity bridge, verifies a pinned immutable revision, rights, review policy and license, performs the publish/withdrawal transaction and returns a signed/verifiable receipt as appropriate. **Workspace must not set public Research visibility flags or claim success before Research reports success.**

The public Research page's WordPress bridge remains **GET-only**; it cannot publish, approve, edit or expose private outputs. WordPress Publications handles editorial posts/blogs, not the Research public research catalog.

## Suggested Workspace object and actions

Per output: stable `workspace_project_ref`, `workspace_output_ref`, `research_project_ref`, `research_entry_ref`, `output_kind`, owner/tenant scope, `draft_revision_ref`, `approved_release_ref`, `public_slug`, `release_state`, `rights_state`, `last_receipt_ref` and `updated_at`. Treat these as references/view state; **Research owns release state**.

Actions should use existing Workspace cross-product handoff and human governance adapters only after these are validated with real owner sessions; the current v3.61 governance contracts and v3.68 handoff fabric are **not evidence that real Research publish writes are enabled**.

## Dependency and acceptance

**Blocker: RH-PROD-05.1 real-account Workspace→Research identity + ownership + session revocation acceptance.** Without it, private publication actions must remain denied and no public cutover is allowed.

Acceptance: 1 parent project, 3 output workspaces; distinct locked revision streams; permissioned Workspace UI controls; publish only one approved output; others stay private; public Research count/content updates; source rights revocation and withdrawal prevent stale public content; two-owner isolation; audit/receipts; backup/restore and browser checks. No WordPress Publications blog post, Press release or outbound email is automatically produced.

**No production change, URL change, repository rename, new database per output or WordPress mutation is authorized by this handoff.**
