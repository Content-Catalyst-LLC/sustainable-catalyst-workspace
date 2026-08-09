# Sustainable Catalyst Workspace v0.30.0
## Public Beta & Product Readiness

Release date: 2026-08-09

v0.30.0 is a consolidation release that makes the existing Workspace capability set easier to enter, navigate, diagnose, and recover without introducing another major subsystem.

### Public Beta Start

Workspace now opens on **Start**, not the project-management surface. Start provides:

- a compact local Workspace summary;
- **New blank project**;
- **Continue recent project**;
- direct Knowledge Library handoff to `/knowledge-libraries/`;
- four guided first-project pathways: Research Investigation, Analytical Assessment, Decision Case, and Publication Preparation;
- a recent-work surface;
- local runtime capability checks.

Guided pathways use the existing human-controlled workflow system. They do not generate findings, infer completion, or bypass the underlying research/analysis/decision structures.

### Runtime readiness

The Start surface reports local availability of:

- browser-local storage;
- SHA-256/Web Crypto integrity support;
- file import/export APIs;
- session/postMessage return handoffs.

Capability status is descriptive and has no hidden readiness score.

### Accessibility and navigation

- Arrow Left / Arrow Right / Home / End navigation across top-level Workspace views.
- `aria-current="page"` follows the active view.
- Stronger `:focus-visible` treatment.
- Responsive horizontal navigation.
- Reduced-motion handling.
- Forced-colors/high-contrast resilience.
- Advanced views remain lazy-rendered on selection rather than booting every environment eagerly.

### Data and governance boundary

No schema migration is required:

- Workspace storage: **27 → 27**
- Project schema: **`sc-workspace-project/12.0` → unchanged**

Guest/local Workspace remains first-class. Signing in does not upload project data. Account backup and cross-device sync remain explicit. Lifecycle state remains human-declared. No automatic telemetry or hidden readiness score is introduced.

### New contracts

- `sc-workspace-public-beta-readiness/1.0`
- `/wp-json/sc-workspace/v1/public-beta-contract`

### Validation

The release validates the full inherited Workspace contract suite plus public-beta product-readiness behavior, helper runtime, PHP syntax, registry migration, platform conversion, account persistence, conflict-safe sync, return/AI adapters, Project Diff, Safe Actions, Reconciliation, Decision Receipts, Audit Trail, and Project Lifecycle.
