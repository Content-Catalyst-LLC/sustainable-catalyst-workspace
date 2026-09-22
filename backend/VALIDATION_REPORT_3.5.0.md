# Workspace Backend Validation Report — v3.5.0

Release: **Catalyst Analytics R Runtime Adapter**

Validated release properties:
- Workspace service version 3.5.0.
- Catalyst Analytics R provider identity/version 2.1.0.
- Core contract `sc.core.analytical-runtime-provider.v1`.
- R package and declared ggplot2/rlang dependencies installed at Docker image build time.
- Production R service remains non-root and read-only.
- Fixed executable method allowlist; arbitrary R code/function dispatch remains disabled.
- Authenticated Workspace provider discovery, validation, execution and receipt APIs.
- Durable analytical-provider receipt migration with request/result SHA-256 fingerprints.
- WordPress proxy and typed-client surface added without exposing service credentials.
- Legacy bounded R operation service remains available.

Local release tests: v3.5 adapter tests 8/8 passed; registry tests 9/9 passed.
