# Neural-Symbolic Research Intelligence Runtime v3.39.0

## Architecture
- Platform Core: governed research-object and provenance contracts.
- Workspace: bounded neural-symbolic computation.
- Research Lab: experiments and hypothesis workflows.

## Operations
1. neural-symbolic-symbol-contract
2. neural-symbolic-context-project
3. neural-symbolic-bind
4. neural-symbolic-rule-contract
5. neural-symbolic-constraint-evaluate
6. neural-symbolic-relation-score
7. neural-symbolic-infer
8. neural-symbolic-explain

## Rule language
Only declarative operators are accepted: `implies`, `requires`, `excludes`, `at-least-one`, and `all-or-none`. There is no `eval`, arbitrary Python, dynamic import, or external rule-engine execution.

## Epistemic boundary
All outputs are computation artifacts. `truthValueAssigned=false` and `isObservedEvidence=false`. Neural similarity is not logical proof, and symbolic inference is limited to consequences of operator-declared rules.
