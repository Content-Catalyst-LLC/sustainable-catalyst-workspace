# Workspace v0.63.0 — Cross-Browser & Device Compatibility

## Purpose
v0.63.0 hardens the existing Workspace application across browser engines, desktop operating systems, tablet-class environments, narrow windows, touch/pointer input, and WordPress embedding without changing canonical project or storage schemas.

## Compatibility strategy
Workspace now prefers **feature detection over browser-version gating**. Browser-family and platform-family labels are diagnostic only; capabilities decide which path is used.

The target matrix is:

- Chromium / Chrome family
- Microsoft Edge
- Safari / WebKit
- Firefox / Gecko
- macOS and Windows desktop environments
- iPadOS/iOS tablet-class and Android tablet-class environments
- desktop, tablet, and compact/narrow viewports
- top-level and embedded WordPress application contexts

Runtime capability checks do not claim that every physical browser/device combination has been manually certified. Manual QA remains a release-validation activity.

## Hardened runtime paths

### Browser-local persistence
The release probes localStorage and sessionStorage with temporary keys. Local project persistence remains a hard requirement; if it cannot be written and read back, Workspace reports **attention** rather than pretending the session is safely persistent.

### File import
Text-file import uses `File.text()` when available and falls back to `FileReader.readAsText()` when needed. Existing import schemas, size limits, fingerprints, staging, and copy-only governance remain unchanged.

### Client-side export
Portable exports prefer Blob + object URL + an attached download anchor. A small-data URI path exists only as a bounded fallback when object URLs are not available. The fallback is capped at 1 MiB rather than silently attempting unsafe/unbounded data-URI downloads.

### History API
History writes are guarded. If `pushState` / `replaceState` are unavailable or throw, Workspace remains navigable in-app and treats browser history participation as limited rather than breaking route changes.

### Viewport and embed behavior
A root-bound viewport adapter publishes `--scw-viewport-height`, `--scw-viewport-width`, device class, touch state, and embed state. It uses ResizeObserver / requestAnimationFrame when available and window resize fallbacks when they are not. This avoids assuming the Workspace always owns the entire browser window.

## Compatibility review surface
Review → **Compatibility** exposes a local audit of:

- local persistence
- tab route memory
- file import path
- file export path
- History API
- viewport measurement
- pointer/touch input
- embedded application context

A privacy-minimized JSON report can be exported manually. It omits raw user-agent strings, device identifiers, project/object content, source URLs, query strings, and page fragments.

## Governance boundaries

- Storage schema remains **35**.
- Project schema remains **sc-workspace-project/20.0**.
- No canonical data migration.
- No browser-family gating of research features.
- No automatic upload or telemetry.
- No device fingerprinting.
- No hidden compatibility score.
- No claim of manual certification for browsers/devices not actually exercised during QA.
