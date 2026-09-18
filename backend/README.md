# Current Workspace backend: v2.31.0 — Local-First Synchronization Protocol

The Python/PostgreSQL backend remains authoritative. v2.30 adds a server-generated bootstrap projection and explicit thin-client state profile so browsers can rehydrate canonical read models into a memory-only cache while persisting only transient UI state.

# Sustainable Catalyst Workspace Backend v2.13.0

Workspace v2.13.0 deploys the first dedicated specialist runtime behind the polyglot scientific fabric: a bounded R statistical and econometric service.

The main API/worker remain Python/FastAPI/PostgreSQL. Python and SQL continue to execute through their existing bounded paths. R now executes through `sc-workspace-r-runtime`, an internal-only sidecar running a fixed R runner. Julia and WASM remain registered but unconfigured.

## R runtime operations

- `workspace.polyglot.r.describe`
- `workspace.polyglot.r.t-test`
- `workspace.polyglot.r.correlation`
- `workspace.polyglot.r.linear-model`
- `workspace.polyglot.r.logistic-model`
- `workspace.polyglot.r.anova`
- `workspace.polyglot.r.arima`
- `workspace.polyglot.r.econometric-ols`

Every result is content-addressed and receives a durable polyglot execution receipt. Model-producing R jobs also receive a statistical model receipt. Arbitrary R source, formulas, packages, runtime URLs and credentials are not accepted from clients.

## v2.24.0 — Backend Authority & Domain Service Consolidation

The backend is now explicitly canonical for project/notebook domain validation, revision preconditions, canonical fingerprints, provenance, persistence, and mutation receipts. The browser remains a rich presentation/interaction client and local-draft surface rather than the source of canonical domain truth.
