# Workspace v0.65.0 — Responsive & Field-Use Experience

## Purpose

This release makes the existing Workspace product usable across smaller laptops, tablets, narrow browser windows, touch/coarse-pointer environments, and short landscape viewports. It is a presentation/runtime hardening release, not a new research subsystem.

## Field-use profile

`sc-workspace-field-use-v1.js` derives a transient profile from root width, viewport height, orientation, pointer capabilities, and touch availability. The runtime exposes `wide`, `compact`, and `narrow` classes through `data-scw-viewport`; input is `fine`, `coarse`, or `mixed`. Short viewports receive `data-scw-short-viewport=1`.

The profile is deliberately non-identifying: no raw user agent, device ID, project content, canonical data, storage write, telemetry, or automatic submission is involved.

## Field priorities

Phones and very narrow windows prioritize capture, review, navigation, and lightweight editing. Dense graphs, tables, comparison surfaces, and composition tools remain available; the interface uses bounded local scrolling rather than widening the page or silently removing capability.

## Lab relationship

Workspace is the working hub, while Lab is a deliberate destination for specialized experimental/scientific tools. v0.65 adds contextual Lab handoffs in the public Pathways section and inside Connected workflows. The hero remains intentionally limited to Workspace and Knowledge Library actions.

## Manual QA matrix

Automated fixtures should cover 1600, 1440, 1280, 1024, 834/820, 768, 430, and 390px widths, plus a short landscape viewport. Physical Safari/iPadOS, Chrome/Android tablet, Windows/Edge, macOS/Safari/Chrome, Firefox, keyboard-only, touch, zoom, and screen-reader checks remain field-validation requirements.
