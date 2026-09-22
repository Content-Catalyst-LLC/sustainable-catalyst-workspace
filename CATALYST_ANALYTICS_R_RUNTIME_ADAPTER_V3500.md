# Catalyst Analytics R Runtime Adapter — Workspace v3.5.0

## Boundary
Platform Core owns the analytical request contract. Workspace owns authenticated execution, input resolution, environment capture, resource policy, persistence, and receipts. Catalyst Analytics R owns the bounded statistical/sustainability computation.

## Runtime
The package is installed at Docker image build time. Production retains a read-only root filesystem and a non-root runtime user. The adapter never calls `install.packages()` in production.

## Security
Execution is limited to the provider manifest plus the Workspace v3.5 executable allowlist. Arbitrary code, arbitrary R functions, client-selected package installation, and client-selected runtime URLs are rejected.

## Provenance
Every execution records a durable Workspace receipt containing request and result fingerprints, provider identity/version, Core contract, method reference, execution reference, environment reference, timestamps, status, and bounded error metadata.
