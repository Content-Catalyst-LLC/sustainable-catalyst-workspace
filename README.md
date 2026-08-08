# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across the Sustainable Catalyst platform.

## Current release

**v0.6.1 — Dedicated Workspace Page & Platform Conversion**

Workspace now supports the complete first operating loop inside persistent Projects:

- Research — questions, sources, reading queues, evidence, and claims.
- Analysis — datasets, variables, assumptions, methods, comparisons, and findings.
- Decision — options, criteria, assessments, risks, rationale, confidence, and durable Decision objects.

v0.6.1 adds the dedicated public Platform presentation and a reversible administrator-controlled conversion of `/platform/` to Workspace.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

After conversion, the canonical public route is:

```text
/platform/
```

The legacy `/platform/workspace/` route redirects only after the administrator performs the conversion.

## Controlled Platform conversion

Open **Tools → Workspace Page** in WordPress. The conversion is not run during activation. It backs up the existing Platform page and preserves its page ID, slug, parent, publication status, and page template. Rollback is available from the same tool.

## Persistence boundary

Workspace remains usable without signing in. Projects and objects are stored on the current device. Optional WordPress authentication identifies the current account session only; v0.6.1 does not upload, claim, or synchronize local project content.

## Contracts

- Project: `sc-workspace-project/5.0`
- Object: `sc-workspace-object/1.0`
- Research: `sc-workspace-research/1.0`
- Analysis: `sc-workspace-analysis/1.0`
- Decision: `sc-workspace-decision/1.0`
- Identity: `sc-workspace-identity/1.0`
- Platform: `sc-workspace-platform-contract/1.0`
- Storage schema: `7`

## Product Registry

- Canonical ID: `sustainable-catalyst-workspace`
- Family: `commercial`
- Console screen: `commercial`
- Display order: `400`
- Lifecycle: `experimental`
- Access: free public
- Canonical repository: `Content-Catalyst-LLC/sustainable-catalyst-workspace`
- Product URL after conversion: `/platform/`

See `docs/DEDICATED_WORKSPACE_PAGE_PLATFORM_CONVERSION_V061.md` for the conversion contract.
