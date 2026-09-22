# Catalyst Analytics R v2.2 Provider Promotion — Workspace v3.9.1

## Runtime boundary
Platform Core declares analytical work. Workspace authenticates, resolves inputs, governs execution, captures environment/provenance, persists receipts, and invokes the bounded provider. Catalyst Analytics R performs only declared provider methods inside the hardened R runtime.

## Provider identity
- provider: `catalystanalyticsr`
- provider version: `2.2.0`
- Workspace adapter: `3.9.1`
- Core provider contract: `sc.core.analytical-runtime-provider.v1`
- diagnostics contract: `sc.analytics-r.statistical-diagnostics-validation.v1`
- runtime: R
- execution host: Workspace

## Security / execution
The R package is installed at Docker image build time. Production runs as UID 10001 with a read-only root filesystem, dropped capabilities, `no-new-privileges`, and a bounded tmpfs. Client-supplied packages, runtime URLs, arbitrary functions, and arbitrary code remain prohibited.

## Statistical validation boundary
Diagnostics, assumptions, robustness checks, and model-comparison evidence are stored and returned as evidence. Human review remains required; the runtime does not automatically declare research valid/invalid or select a scientific conclusion.

## Database impact
None. No migration 041 is introduced. Existing migration 036 receipts include the provider version and remain compatible; v3.9 migration 040 remains the release migration lineage.
