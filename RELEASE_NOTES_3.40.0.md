# Workspace v3.40.0 — Reproducible Deep Learning Research Packages

Workspace v3.40.0 adds a governed, content-addressed research-package layer over the neural runtime. It packages artifact references and reproducibility closure rather than arbitrary executable code.

## New bounded operations
1. `workspace.neural.research-package-plan`
2. `workspace.neural.research-package-create`
3. `workspace.neural.research-package-verify`
4. `workspace.neural.research-package-inspect`
5. `workspace.neural.research-package-reproduction-plan`
6. `workspace.neural.research-package-reproduction-verify`
7. `workspace.neural.research-package-export`
8. `workspace.neural.research-package-lineage`

The neural operation registry advances from 101 to 109. No database migration. Rollback baseline: v3.39.0.1.
