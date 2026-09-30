# Workspace v3.46.2.0 — Transport, Authentication & API Adapter Decoupling

This release removes request and identity responsibilities from the host-adapter contract.

Canonical host-neutral components:
- `app/core/workspace-host-adapter-contract-v11.js`
- `app/core/workspace-application-kernel-v34620.js`
- `app/client/workspace-transport-v34620.js`
- `app/client/workspace-auth-context-v34620.js`
- `app/client/workspace-api-client-v34620.js`

WordPress now supplies separate host, proxy-transport, and REST-nonce authentication adapters. The proxy transport contains no authentication logic; the authentication adapter performs no network requests. Standalone Workspace can construct a direct backend transport and host-neutral auth context without WordPress.

The verified project lifecycle provider remains intact. Project runtime extraction is reserved for v3.46.3.0.

No database migration and no scientific-runtime behavior change.
