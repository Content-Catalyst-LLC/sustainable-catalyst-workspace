# Workspace v3.46.6.0 — Standalone Web Application Shell

## Purpose
Deliver the first independently bootable Sustainable Catalyst Workspace web application outside WordPress.

## New standalone distribution
`standalone/`

The distribution contains:
- `index.html`
- `config.js`
- `bootstrap.js`
- `workspace-standalone-shell-v34660.css`
- `assets/` with the canonical host-neutral Workspace runtime
- `asset-manifest-v34660.json`
- `serve.py`
- `README.md`

## New canonical application components
- `app/standalone/workspace-standalone-runtime-v34660.js`
- `adapters/standalone/workspace-standalone-host-adapter-v34660.js`
- `app/core/workspace-application-kernel-v34660.js`

## Standalone boot path

```text
index.html
  -> config.js
  -> bootstrap.js
  -> host contract
  -> direct transport
  -> anonymous auth context
  -> API client
  -> persistence runtime
  -> canonical state store
  -> project runtime
  -> module registry
  -> application kernel
  -> standalone host adapter
  -> standalone runtime
  -> standalone UI shell
```

WordPress is absent from this path.

## Functional scope
The first standalone shell exposes the canonical project lifecycle:
- list projects
- create project
- open project
- delete project
- inspect runtime
- manually test direct backend health

It deliberately does not reproduce the entire historical WordPress-rendered Workspace interface. Additional feature surfaces move behind the module registry progressively.

## Network behavior
No backend request is made automatically at page load. The configured API base is used only when a user or application operation calls the API. The included **Check backend** control verifies direct transport explicitly.

## Storage behavior
The shell uses the existing `sc_workspace` browser-storage namespace by default and preserves unknown top-level state fields. Browser storage remains origin-scoped.

## WordPress continuity
The WordPress adapter remains supported in parallel and advances to v3.46.6.0 with the same host-neutral kernel.

## Migration
- database migration: none
- browser storage schema migration: none

## Next
v3.46.7.0 — WordPress Thin Adapter.
