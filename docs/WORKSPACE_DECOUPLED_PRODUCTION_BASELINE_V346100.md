# Workspace v3.46.10.0 — Decoupled Workspace Production Baseline

## Purpose
Close the v3.46.x decoupling series with a production baseline that future Workspace releases must preserve.

## Baseline architecture

```text
Workspace application core
├── host contract
├── transport
├── authentication
├── API client
├── canonical persistence
├── canonical state
├── project runtime
├── module registry
└── application kernel

Hosts
├── Standalone Web
│   ├── manifest-driven boot
│   ├── direct backend transport
│   └── production certification
└── WordPress
    ├── one thin adapter script
    ├── host/auth/proxy metadata
    └── no ownership of application state or project logic

Backend
└── canonical server-side authority
```

## Formal baseline contract
`production/decoupled-workspace-production-baseline-v3.46.10.0.json`

The contract freezes:
- WordPress is optional;
- WordPress owns no canonical project/state/persistence/module boot logic;
- WordPress PHP has one script entry point;
- standalone boot is production certified;
- standalone uses direct backend transport;
- backend remains canonical server authority;
- host distributions are generated from one canonical asset pipeline;
- shared host assets retain checksum parity;
- optional module failure isolation remains mandatory;
- no v3.46.10.0 DB/storage migration.

## Baseline runtime contract
`app/core/workspace-decoupled-production-baseline-v346100.js`

This can assert the production invariants against kernel, standalone runtime, and module-registry diagnostics.

## Certification
`build/certify_workspace_decoupled_baseline_v346100.py`

Report:
`production/decoupled-workspace-production-baseline-certification-v346100.json`

## Rollback
Previous/rollback release: `3.46.9.0`.

## Next
The WordPress decoupling series is complete at v3.46.10.0. The next Workspace feature line can proceed without making WordPress a core architectural dependency.
