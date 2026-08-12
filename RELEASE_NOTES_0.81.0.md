# Sustainable Catalyst Workspace v0.81.0 — WordPress & Deployment Hardening

Release date: 2026-08-12

v0.81.0 is the first deployment-hardening release after Workspace Release Candidate I. It remains inside the feature freeze: no new product subsystem, no canonical schema migration, and no automatic change to project data.

## Release focus

- Add a fail-closed WordPress bootstrap guard so a partial plugin upload cannot proceed into a fatal `require_once` chain.
- Add activation preflight for required release files and supported WordPress/PHP runtime versions.
- Record bounded, metadata-only deployment observations for upgrade diagnostics.
- Detect mixed/stale cumulative JavaScript and CSS assets in the browser.
- Verify current plugin, localized runtime, release-candidate stage, asset filenames, and optional version query strings.
- Add **Review → Deployment** with privacy-minimized diagnostics and an exportable production checklist.
- Keep browser/project storage outside cache-purge logic: project storage is application data, not disposable cache content.
- Preserve explicit v0.80.0 rollback compatibility and require a rollback artifact in the release bundle.

## Defects closed during hardening

- The central Review navigation registry had not been advanced for `final-audit`, `beta-closure`, and `release-candidate`, which could make those valid surfaces route differently depending on the navigation path. v0.81 registers all RC-era Review surfaces, including Deployment and Recovery Drills, in one canonical map.
- Registry recovery was not retrying the most recent v0.78-v0.80 pending keys. The current registry boot path now includes those recent pending states.
- The registry admin notice still named v0.79.0 instead of deriving the currently installed Workspace version.

## Deployment boundaries

v0.81 does **not** automatically purge caches, roll back the plugin, migrate projects, change canonical project data, upload diagnostics, or treat local Workspace storage as cache. Production cache/CDN invalidation remains an explicit hosting operation after plugin replacement.

## Compatibility

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project Export schema: `sc-workspace-project-export/20.0`
- Rollback target: v0.80.0
- Schema migration required: no

See `VALIDATION_REPORT_0.81.0.md` and `docs/WORDPRESS_DEPLOYMENT_HARDENING_V0810.md` for the automated and manual deployment gates.
