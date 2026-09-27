# Validation Report — Workspace v3.20.0

## Result

**PASS for the v3.20.0 release delta.**

### Validation performed

- Python bytecode compilation passed for `backend/app` and `backend/neural-runtime`.
- New neural runtime tests passed.
- Existing scikit-learn ML runtime regression tests passed.
- Existing v3.19.0 predictive-investigation regression tests passed.
- Typed client generation/check passed at 291 endpoints.

Targeted release/regression run:

- **17 passed**
- no failures

Full historical backend suite comparison:

- v3.19.0 baseline: **214 passed / 46 failed**
- v3.20.0 tree: **220 passed / 46 failed**

The 46 full-suite failures are legacy historical tests pinned to earlier release-version strings, obsolete endpoint counts, or earlier migration assumptions. v3.20.0 adds six passing tests and does not increase the baseline failure count.

### Safety and architecture checks

Validated:

- classical ML and neural runtime identities remain separate;
- neural operations are bounded and declarative;
- arbitrary code execution remains disabled;
- client-supplied packages and runtime credentials are rejected;
- serialized neural modules are rejected;
- v3.20.0 training is disabled;
- CPU-only device policy is explicit;
- neural job dispatch uses the existing Workspace polyglot fabric;
- typed OpenAPI projection has no missing operations.

### Database

No migration is required. The existing v3.19.0 schema is sufficient for the runtime foundation because neural executions use the generic polyglot execution receipt and artifact model.
