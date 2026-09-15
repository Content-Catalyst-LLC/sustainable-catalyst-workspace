# Sustainable Catalyst Workspace v2.14.0 — Julia Simulation & Numerical Modeling Runtime

Workspace is the governed research execution environment for Sustainable Catalyst. v2.14.0 extends the polyglot scientific fabric with a real Julia runtime alongside Python, bounded SQL, and R.

## Active scientific runtimes

- **Python** — NumPy, Pandas, SciPy and SymPy bounded operations
- **SQL** — bounded aggregate and grouped analytical operations
- **R** — statistical, inferential, time-series and econometric operations
- **Julia** — numerical simulation, optimization, eigen-analysis, Monte Carlo, numerical integration and parameter sweeps
- **WASM** — registered server-configured adapter, not yet deployed

## Julia operations

`workspace.polyglot.julia.ode-linear-rk4`, `workspace.polyglot.julia.lotka-volterra`, `workspace.polyglot.julia.monte-carlo-normal`, `workspace.polyglot.julia.quadratic-optimize`, `workspace.polyglot.julia.eigen-analysis`, `workspace.polyglot.julia.integrate-series`, `workspace.polyglot.julia.polynomial-roots`, and `workspace.polyglot.julia.parameter-sweep`.

Every Julia result is persisted as a content-addressed artifact with a polyglot execution receipt. Julia model/simulation operations also create a numerical-simulation receipt carrying solver, steps/seed metadata, metrics, request fingerprint and result SHA-256.

Arbitrary code execution remains disabled. Runtime URLs and credentials remain server-side only.
