# Sustainable Catalyst Workspace v0.64.1

## Accessibility Runtime & Desktop Layout Recovery

v0.64.1 is a surgical production hotfix over v0.64.0. It does not add a new product subsystem and does not migrate Workspace data.

### Runtime recovery

- Removes the self-referential `sc-workspace-accessibility-v1` WordPress script dependency.
- Keeps browser compatibility as the accessibility runtime prerequisite.
- Moves the current cumulative shell assets to `workspace-v0.64.1.css` and `workspace-v0.64.1.js`.
- Adds an automated static dependency-graph gate that fails on self-dependencies, missing dependency handles, or cycles among Workspace-enqueued scripts.

### Desktop layout recovery

- Replaces intrinsic minimum track pressure in the editorial hero with zero-minimum fractional tracks.
- Applies the same hardening to the Focused Research Workspace two-column shell.
- Explicitly sets `min-width: 0` on affected grid children and high-risk nested grids.
- Preserves the existing one-column breakpoints at 980px/900px and mobile behavior below them.
- Prevents the observed character-by-character headline/body wrapping caused by a collapsed text track.

### Regression coverage

The release contract covers 1600, 1440, 1280, 1024, 768, and 390px viewport targets. Automated browser rendering is a build-time regression aid; production WordPress field validation remains required, including confirming that the page renders through the footer without a PHP fatal.

### Boundaries

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Schema migration: **none**
- v0.64 keyboard/focus/accessibility behavior: **preserved**
- WCAG certification claim: **none**
