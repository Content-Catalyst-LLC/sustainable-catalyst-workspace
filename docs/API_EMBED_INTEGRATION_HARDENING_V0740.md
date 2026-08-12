# Workspace v0.74.0 — API, Embed & Integration Hardening

v0.74.0 hardens the existing v0.55 static read-only integration boundary without creating a live server project API.

## Fail-closed integration

A projection must pass local integrity verification before JSON export or embed copy. Static embeds are bounded to 96 KiB, API envelopes to 128 KiB, and the renderer URL must use HTTPS and match the configured Workspace origin (localhost HTTP remains a development-only exception). Invalid descriptors render a generic unavailable state and never attempt to fetch private Workspace content.

## Explicit boundary

- Durable `scw://` references are identifiers, never credentials.
- Static embeds use no credentialed fetch.
- No `postMessage` bridge is established.
- No remote write or canonical mutation exists.
- The parent page is not implicitly trusted.
- Projection fingerprints are drift/integrity receipts, not signatures or authentication.
- Safety reports are privacy-minimized and omit project content, project titles, durable references, source URLs, user-agent strings, and device identifiers.

## Compatibility

The existing v1 durable-reference, projection, API-envelope, and embed-descriptor schemas remain in place. v0.74 adds hardening and safety-report contracts around them, so Storage 35 / Project 20.0 / Project Export 20.0 remain unchanged.
