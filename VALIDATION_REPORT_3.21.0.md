# Workspace v3.21.0 Validation Report

Release: **Neural Dataset, Tensor & Transformation Interchange**

Validated in the build environment:

- Release validator: PASS.
- Generated typed-client contract: PASS, 291 typed endpoints.
- Python bytecode compilation for modified backend/neural modules: PASS.
- Shell syntax for apply/deploy/package/install scripts: PASS.
- WordPress PHP syntax for plugin bootstrap and primary Workspace class: PASS.
- Neural foundation + v3.21 interchange focused regression suite: **13 passed**.
- Repository-wide backend suite: **227 passed / 46 legacy failures**. The 46 failures are the existing historical release-lineage/version assertions pinned to older Workspace releases; this build adds no new failure category.
- Neural operation registry: 8 bounded operations.
- Classical scikit-learn runtime remains separate from the PyTorch neural runtime.
- Training remains disabled.
- External dataset reads from the neural container remain disabled.
- Database migration: none.
- v3.20.0.1 version-matched stable shell asset fix is carried forward as v3.21.0 assets.
- Clean v3.20.0.1 payload application simulation: PASS.
- Backend package `.env` exclusion: PASS.
- ZIP integrity across release bundle, backend, WordPress plugin, repository and tiny patch: PASS.

VPS Docker execution is performed by `DEPLOY_WORKSPACE_BACKEND_V32100_CONTABO.sh`, which additionally verifies live backend health, direct neural-runtime health, a real transformation job, runtime registry/OpenAPI coherence, and container hardening.
