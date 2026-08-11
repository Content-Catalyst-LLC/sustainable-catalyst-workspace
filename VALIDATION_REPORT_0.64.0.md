# Sustainable Catalyst Workspace v0.64.0 — Validation Report

Release: **v0.64.0 — Accessibility & Keyboard-First Product Audit**  
Predecessor: **v0.63.0**  
Release date: **2026-08-10 (America/Chicago)**

## Release gate

**PASS**

## Automated validation

- Python contract suite: **814 tests passed**.
- JavaScript runtime suite: **45 runtime files passed**.
- PHP runtime suite: **5 runtime files passed**.
- Repository JavaScript syntax sweep: **123 files passed**.
- Repository PHP syntax sweep: **9 files passed**.
- JSON parse sweep: **346 JSON files passed**.
- `scripts/validate_release.py`: **PASS**.
- Release-diff whitespace check against v0.63.0: **PASS**.

## v0.64.0 accessibility and keyboard checks

Validated:

- Storage schema remains **35**.
- Project schema remains **sc-workspace-project/20.0**.
- Project Export remains **20.0** and Notebook Workspace remains **8.0**.
- No canonical project/storage migration is introduced.
- Workspace targets **WCAG 2.2 AA** without claiming automated conformance certification.
- Primary and contextual navigation groups support Arrow-key and Home/End movement while preserving native activation behavior.
- Modal dialogs contain Tab/Shift+Tab focus while open and restore focus to the invoking control on close.
- Escape closes a dialog only when an explicit close/cancel control is available.
- Newer Review/Exchange routes use the same centralized top-level visibility rule as established Workspace sections, preventing keyboard/pointer route divergence.
- `:focus-visible` treatment is strengthened without removing native semantics.
- `prefers-reduced-motion: reduce` suppresses unnecessary motion and smooth scrolling.
- Forced-colors/high-contrast environments receive explicit focus treatment.
- Touch-capable contexts retain minimum control target sizing.
- A dedicated **Review → Accessibility** surface provides a local structural/runtime audit.
- Accessibility diagnostics do not include project/object/source content, source URLs, raw user-agent values, or device identifiers.
- No accessibility telemetry, automatic submission, hidden productivity/accessibility score, device fingerprinting, or canonical mutation is introduced.
- A manual WCAG 2.2 AA field checklist is exportable for keyboard-only flows, focus order, zoom/reflow, screen readers, forced colors, reduced motion, touch targets, measured contrast, and error identification/announcement.
- v0.63.0 browser/device compatibility fallbacks remain intact and are reused for accessibility report/checklist export.
- v0.62.0 persistence transaction, integrity receipt, and last-known-good protections remain intact.

## Manual audit boundary

The automated DOM/runtime checks are **diagnostic support, not WCAG certification**. Physical/manual validation remains required for complete keyboard task flows, VoiceOver + Safari, Windows screen readers (NVDA/JAWS/Narrator), 200% zoom, 400%/320 CSS-pixel reflow, forced colors/high contrast, reduced motion, touch behavior, measured contrast, and error announcement behavior.

## Result

**v0.64.0 passes the repository release gate and is ready for deployment and accessibility field validation.**
