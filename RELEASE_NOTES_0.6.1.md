# Sustainable Catalyst Workspace v0.6.1 — Dedicated Workspace Page & Platform Conversion

Released: 2026-08-08

## Added

- Dedicated `[sc_workspace_platform]` public page experience.
- Research → Evidence → Analysis → Decision workflow presentation.
- Administrator-controlled **Tools → Workspace Page** conversion utility.
- Pre-write snapshot of the existing `/platform/` page.
- One-action rollback to the original Platform title/content/excerpt.
- `/wp-json/sc-workspace/v1/platform-contract` route.
- Canonical Workspace product URL advances to `/platform/`.
- Legacy `/platform/workspace/` redirects to `/platform/` only after a successful conversion.

## Safety

- No page is modified on plugin activation.
- Conversion fails closed if the root Platform page cannot be resolved.
- Page ID, slug, parent, publication status, and page template are not rewritten.
- Custom navigation labels are intentionally not rewritten.
- Storage schema remains 7; project schema remains `sc-workspace-project/5.0`.
- Workspace remains free, anonymous-capable, device-local, and without automatic cloud sync.
