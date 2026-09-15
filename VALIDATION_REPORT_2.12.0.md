# Workspace v2.12.0 Validation Report

Release: **Polyglot Scientific Runtime Fabric**

## Release gate
- backend current-suite: 25 passed
- v2.11 scientific compute regression (excluding its obsolete current-release identity assertion): 10 passed, 1 deselected
- v2.12 polyglot runtime tests: 8 passed
- total release gate: **43 passed, 1 historical release-identity assertion deselected**
- PHP syntax: **31/31 files passed**
- Python compileall: passed
- VPS deployment script `bash -n`: passed
- structural release validator: passed

## Historical suite
`PYTHONPATH=backend pytest -q`: **1,189 passed / 127 failed**. The 127 failures are historical tests that hard-code earlier current plugin versions/assets/README/release-lineage identities. No v2.12 functional test failed.

## Security assertions
- no arbitrary Python/R/Julia/SQL/WASM source execution
- no `subprocess`, `eval`, `exec`, or shell path in the polyglot fabric
- R/Julia/WASM endpoints and credentials are server-configured only
- SQL execution is declarative/registered; raw SQL text is not accepted
- worker sandbox remains read-only root, 2 CPU, 2 GiB, 256 PIDs, capability drop ALL, no-new-privileges

## Runtime coverage
Five runtime identities are registered: Python, R, Julia, SQL, WASM. Python and SQL are executable in-process in v2.12. R, Julia, and WASM are integration-ready server-configured adapters and intentionally report unconfigured until their runtime services are deployed.
