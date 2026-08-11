# Workspace v0.64.0 — Accessibility & Keyboard-First Product Audit

## Release objective
v0.64.0 hardens Workspace so that navigation, modal interaction, route changes, review surfaces, and major controls can be operated and inspected without depending on a pointer. The release targets **WCAG 2.2 AA** while preserving the existing Storage 35 / Project 20.0 boundary.

## Runtime changes
- Adds a local accessibility audit surface under **Review → Accessibility**.
- Adds Arrow-key/Home/End movement within Workspace navigation groups while preserving native Enter/Space activation.
- Adds modal Tab containment, Escape close where a close control exists, and focus restoration to the invoking control.
- Normalizes top-level Workspace section visibility so every registered route, including newer Review/Exchange surfaces, uses the same route switch.
- Strengthens `:focus-visible` presentation and forced-colors handling.
- Suppresses unnecessary smooth motion/transitions when `prefers-reduced-motion: reduce` is active.
- Preserves tablet touch-target sizing in touch-capable contexts.

## Accessibility audit boundary
Automated checks inspect structural/runtime facts such as skip navigation, labeled sections, modal semantics, live status regions, form-control naming, motion preference handling, and host viewport zoom restrictions.

Automated checks **do not certify WCAG conformance**. v0.64 therefore exports an explicit manual checklist for:
- keyboard-only end-to-end workflows;
- focus order and focus restoration;
- visible focus;
- 200% zoom and 400%/320 CSS-pixel reflow;
- VoiceOver + Safari;
- Windows screen-reader coverage (NVDA/JAWS/Narrator);
- forced colors / high contrast;
- reduced motion;
- touch targets;
- measured contrast;
- error identification and announcement.

## Privacy and governance
The accessibility report contains no project/object/source content, source URLs, raw user-agent value, or device identifier. Nothing is submitted automatically. No canonical research is changed by an audit. No accessibility/productivity score is computed.

## Compatibility continuity
v0.63 browser/device capability fallbacks remain the runtime compatibility layer. v0.64 uses those export fallbacks when exporting accessibility reports/checklists and does not replace capability detection with browser-family assumptions.
