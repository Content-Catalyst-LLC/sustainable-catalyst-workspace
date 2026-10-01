# Sustainable Catalyst Workspace — Standalone Web Shell v3.50.0

This directory is a host-independent web distribution of Workspace.

## Local preview

```bash
python3 serve.py --port 4173
```

Open `http://127.0.0.1:4173`.

## Architecture

The shell loads only host-neutral Workspace application modules plus the standalone host adapter. It does not load WordPress, a WordPress REST proxy, WordPress nonces, or WordPress plugin code.

The direct backend URL is configured in `config.js`. No backend request is made automatically at boot; use **Check backend** to exercise the direct API transport.

The browser-local state key defaults to the existing `sc_workspace` namespace. Because browser storage is origin-scoped, a separately hosted standalone application receives its own storage namespace unless it is deployed on the same origin as the current WordPress site.

## Scope of v3.50.0

This is the first independent web shell and exposes the canonical project lifecycle: list, create, open and delete. The large historical WordPress-rendered feature surface is not duplicated here. Those capabilities migrate behind the module registry in subsequent builds.
