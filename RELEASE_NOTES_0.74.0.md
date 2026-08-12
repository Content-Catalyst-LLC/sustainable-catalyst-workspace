# Sustainable Catalyst Workspace v0.74.0 — API, Embed & Integration Hardening

## Scope
Hardens the existing static read-only integration boundary. No live server project API and no canonical schema migration.

## Changes
- Integrity verification before API export and embed copy.
- 128 KiB API-envelope and 96 KiB embed payload caps.
- Trusted HTTPS renderer-origin validation (localhost HTTP allowed only for development).
- Fail-closed embed rendering with a generic no-data-fetch failure state.
- Explicit no-credentialed-fetch, no-postMessage, no-remote-write governance.
- Privacy-minimized integration safety report.
- New API/embed hardening REST contract.
- Existing v1 projection/envelope/embed schemas retained.

## Canonical contracts
Storage 35; Project 20.0; Project Export 20.0; no migration.
