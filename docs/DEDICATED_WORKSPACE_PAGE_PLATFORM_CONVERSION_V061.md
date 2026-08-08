# Dedicated Workspace Page & Platform Conversion — v0.6.1

## Purpose

v0.6.1 makes Workspace ready to replace the general Platform landing page without making a destructive activation-time edit.

## Dedicated page

Use `[sc_workspace_platform]` for the full public Workspace presentation. It introduces the Research → Evidence → Analysis → Decision workflow and then embeds the complete Workspace application.

## Controlled conversion

Administrators use **Tools → Workspace Page**. The conversion:

- resolves the existing root page with slug `platform`;
- fails closed if that page cannot be found;
- captures a non-autoloaded rollback snapshot before writing;
- preserves page ID, slug, parent, status, and page template;
- changes only the page title to `Workspace` and content to `[sc_workspace_platform]`;
- records conversion state;
- redirects the legacy `/platform/workspace/` route to `/platform/` only after conversion;
- supports restoring the original title/content/excerpt from the snapshot.

The plugin does not rewrite custom navigation labels because those can be intentionally different from page titles.

## Data boundary

v0.6.1 does not change Workspace project/storage schemas. Storage remains schema 7 and projects remain `sc-workspace-project/5.0`.
