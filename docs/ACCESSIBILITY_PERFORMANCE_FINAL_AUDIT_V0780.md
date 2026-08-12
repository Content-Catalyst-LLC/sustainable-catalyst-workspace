# Accessibility & Performance Final Audit — v0.78.0

## Purpose

Run one release-facing audit across the existing v0.64 accessibility controls and v0.68 long-session performance controls before Workspace enters final beta defect closure.

## Automated blocking boundary

The final audit may block the automated release gate for structural accessibility failures (for example missing accessible names, duplicate identifiers, or v0.64 audit attention findings) and critical performance thresholds. Advisory performance pressure remains visible without being converted into a hidden score.

## Manual field validation remains required

Passing the automated gate is not WCAG certification or performance certification. Human validation still covers keyboard-only end-to-end completion, VoiceOver/Safari, at least one Windows screen reader, measured contrast, 200% zoom, 400%/320 CSS px reflow, forced colors, reduced motion, physical tablet touch operation, a representative four-hour session, a representative very large project, lower-resource hardware, background/foreground lifecycle behavior, and a production WordPress smoke test.

## Privacy and governance

The exported report contains structural counts, status labels, and timing/counter evidence. It excludes project/research content, source URLs, query text, account identity, device identity, and raw user-agent data. No report is submitted automatically. The audit does not optimize, delete, archive, upload, repair, or mutate canonical Workspace data.

## Schema stability

Storage 35, Project 20.0, and Project Export 20.0 remain unchanged. No migration is required.
