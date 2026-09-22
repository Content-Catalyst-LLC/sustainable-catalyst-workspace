# Workspace v3.5.0 — Catalyst Analytics R Runtime Adapter

Workspace v3.5.0 makes Catalyst Analytics R v2.1.0 a first-class, build-time-installed analytical provider inside the hardened Workspace R runtime.

## Release scope
- Installs `catalystanalyticsr` 2.1.0 and its declared runtime dependencies into the R image during image construction.
- Preserves the production R container as `read_only: true`; live package installation is not required or permitted.
- Adds authenticated manifest, validation, and execution endpoints for the Core contract `sc.core.analytical-runtime-provider.v1`.
- Enforces a fixed provider method allowlist and rejects arbitrary R code, arbitrary function dispatch, client-supplied packages, and client-supplied runtime URLs.
- Adds durable analytical-provider execution receipts with request/result fingerprints and execution/environment references.
- Adds WordPress server-proxy and typed-client endpoints for provider discovery, validation, execution, and receipt lookup.
- Preserves the prior eight bounded generic R operations for backward compatibility.

Forecasting remains `projection_only` for Catalyst Analytics R v2.1.0 and is not exposed as an executable provider method until the provider implements the corresponding exported runtime method.
