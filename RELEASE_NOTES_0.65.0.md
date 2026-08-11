# Sustainable Catalyst Workspace v0.65.0

## Responsive & Field-Use Experience

v0.65.0 hardens Workspace for smaller laptops, tablets, narrow browser windows, touch/coarse-pointer environments, and short landscape viewports without turning the product into a phone-first interface or changing canonical project/storage schemas.

### Runtime field-use profile

- Adds an ephemeral feature-detected field-use profile with `wide`, `compact`, and `narrow` viewport classes.
- Distinguishes fine, coarse, and mixed pointer environments without using browser-family gating.
- Detects short viewports and orientation for bounded dialog behavior.
- Writes only transient DOM data attributes/CSS variables; the profile is not persisted, uploaded, or used for device fingerprinting.

### Responsive hardening

- Adds systematic `min-inline-size: 0` containment to high-risk nested grids/flex layouts.
- Reflows dense two/three-column surfaces progressively on smaller laptops and tablets.
- Keeps primary/context navigation horizontally scrollable where collapsing it would hide routes.
- Provides bounded horizontal scrolling for tables/code rather than widening the entire Workspace page.
- Gives touch/coarse-pointer controls a 44px interaction floor and avoids sub-16px form controls on narrow/touch contexts.
- Caps dialogs against short landscape viewports and preserves reduced-motion/accessibility behavior from v0.64.

### Lab handoff alignment

- Adds `Explore the Lab →` to Workspace Pathway 05: Connected tools and reusable artifacts.
- Adds `Open the Lab` inside Connected workflows / handoff history.
- Does not add another hero CTA; Library and Workspace remain the primary public-entry actions.

### Boundaries

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Schema migration: **none**
- Device fingerprinting: **none**
- Field-use profile persistence: **none**
- Telemetry: **none**
- Automatic upload: **none**
- Canonical mutation: **none**
- Manual physical-device QA remains required.
