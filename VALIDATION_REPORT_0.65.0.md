# Sustainable Catalyst Workspace v0.65.0 — Validation Report

## Release

**Responsive & Field-Use Experience**

v0.65.0 is a presentation/runtime hardening release over v0.64.1. It does not migrate canonical Workspace data.

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Schema migration: **none**

## Automated validation

| Gate | Result |
|---|---:|
| Python contract tests | **836 / 836 PASS** |
| JavaScript runtime suites | **46 / 46 PASS** |
| PHP runtime suites | **6 / 6 PASS** |
| JavaScript syntax checks | **127 PASS** |
| PHP syntax checks | **10 PASS** |
| JSON parse sweep | **353 PASS** |
| v0.65.0 release validator | **PASS** |
| Release-diff whitespace check | **PASS** |
| v0.64.1 desktop-layout regression fixture | **PASS** |
| v0.65.0 field-use Chromium matrix | **PASS** |

## v0.65.0 field-use coverage

The release adds an ephemeral `sc-workspace-field-use-profile/1.0` runtime profile. It classifies the active Workspace root as wide, compact, or narrow; detects fine/coarse/mixed pointer environments; and marks short viewports/orientation for bounded layout behavior.

The profile does **not** persist, upload, fingerprint a device, inspect project content, or mutate canonical Workspace data.

Responsive hardening includes:

- progressive reflow at 1180, 980, 760, 620, and 430px;
- zero-minimum containment for high-risk nested grids/flex layouts;
- 44px interaction floors for coarse/touch and narrow contexts;
- 16px form-control text on narrow/touch contexts to avoid mobile browser zoom behavior;
- locally bounded scrolling for tables/code instead of page-level horizontal overflow;
- short-landscape dialog bounds;
- continued horizontally scrollable primary/context navigation where hiding routes would be destructive.

## Chromium layout matrix

The v0.65 field-use fixture passed at:

- 1600 × 1000
- 1440 × 1000
- 1280 × 900
- 1024 × 800
- 834 × 1112
- 768 × 1024
- 430 × 900
- 390 × 844
- 844 × 390 short-landscape

No fixture produced page-level horizontal overflow. At 430px and 390px the tested Workspace action target remained 44px high. Dense-table overflow remained inside the table region. The short-landscape dialog remained bounded to the viewport.

The inherited v0.64.1 hero/focused-research fixture also continued to pass at 1600, 1440, 1280, 1024, 768, and 390px.

## Lab handoff alignment

The release adds two contextual Lab routes:

1. `Explore the Lab →` in Workspace Pathway 05, **Connected tools and reusable artifacts**.
2. `Open the Lab` inside **Connected workflows / Tools, returns & handoff history**.

No Lab CTA was added to the editorial hero; the hero remains focused on `Open Workspace` and `Explore the Library`.

## Preserved hardening

- v0.64 accessibility runtime and keyboard/focus behavior remain present.
- v0.64.1 accessibility-script self-dependency remains removed and the enqueue graph remains cycle-checked.
- v0.63 browser/device compatibility fallbacks remain present.
- v0.62 persistence, interrupted-write, last-known-good, and recovery-integrity safeguards remain present.

## Field-validation boundary

Automated browser fixtures are regression aids, not physical-device certification. Before treating v0.65 as field-certified, manually validate at minimum:

- Safari on macOS and iPadOS;
- Chrome/Edge on Windows;
- Firefox on desktop;
- Android tablet-class Chrome;
- touch interaction and on-screen keyboard behavior;
- 200% zoom and 400% reflow;
- VoiceOver and Windows screen-reader workflows;
- production WordPress rendering through the real footer and theme/container stack.

## Release status

**PASS — packaged for deployment and field validation.**
