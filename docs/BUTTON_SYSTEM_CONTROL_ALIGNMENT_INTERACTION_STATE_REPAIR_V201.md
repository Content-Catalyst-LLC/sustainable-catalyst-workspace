# Workspace v2.0.1 — Button System, Control Alignment & Interaction-State Repair

This patch repairs inconsistent action controls observed in the v2.0.0 production interface without redesigning Workspace or changing project behavior.

## Repair scope

- one canonical `.scw-button` visual primitive across current Workspace surfaces;
- red primary actions, white institutional secondary actions, and neutral disabled controls;
- 40px default and 44px small-screen/touch minimum control heights;
- explicit focus-visible and forced-colors behavior;
- intentional two-column routing grids for Connected Knowledge and Connected Intelligence;
- full-row handling for the odd final Connected Knowledge route and Connected Intelligence export action;
- light information surfaces for context/result output so status panes do not resemble black CTAs;
- compact state treatment for the `Open` label on settings/connected-workflow drawers;
- alignment repair for dense action groups without changing their JavaScript behavior.

## Boundaries

The release does not change Storage 35, `sc-workspace-project/20.0`, `sc-workspace-project-export/20.0`, canonical project content, action semantics, automatic behavior, AI boundaries, telemetry, or product ownership.
