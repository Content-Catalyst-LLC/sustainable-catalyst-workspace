# Workspace v3.46.0.2 — Versioned Asset Continuity & Release Package Repair

This release permanently repairs the v3.46.0.1 versioned-asset mismatch.

- exact v3.46.0.2 CSS/JS current pair
- retained v3.46.0.1 CSS/JS predecessor pair
- WordPress enqueue bound to exact v3.46.0.2 assets
- deployment preflight clears PHP stat cache before inspecting files
- deployment guard verifies current and predecessor continuity
- packaging verifies both asset pairs inside the generated WordPress ZIP
- core Workspace runtime remains free of hard WordPress feature-script dependencies
- backend identity advances to v3.46.0.2
- no database migration
