# Sustainable Catalyst Workspace v2.0.3
## Workspace Root Scope & Cockpit CSS Recovery

This surgical patch restores the missing `scw-root` class on the live Workspace shell. Mature `.scw-root …` selectors now match the rendered application, recovering Project Cockpit grids, Work Mode Cards, metrics, and other root-scoped presentation that had fallen back to theme/global controls.

No routes, canonical project records, storage schemas, or migration semantics change. v2.0.2 is the exact rollback baseline.
