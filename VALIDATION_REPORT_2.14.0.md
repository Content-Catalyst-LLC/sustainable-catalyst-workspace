# Workspace v2.14.0 Validation Report

Release: **Julia Simulation & Numerical Modeling Runtime**  
Baseline: **v2.13.0 — R Statistical & Econometric Runtime**

## Release gate

- v2.14 structural validator: **PASS**
- Python compilation (`backend/app`, Julia sidecar service): **PASS**
- Backend API/unit suite: **26 passed**
- v2.11 scientific compute regression gate: **10 passed, 1 historical release-identity assertion deselected**
- v2.12 polyglot regression gate: **7 passed, 1 historical version/lineage assertion deselected**
- v2.13 R runtime regression gate: **9 passed, 1 historical version/lineage assertion deselected**
- v2.14 Julia runtime gate: **9 passed**
- Combined targeted gate: **61 passed, 3 deselected**
- WordPress PHP syntax: **31/31 files passed**
- VPS deployment shell syntax: **PASS**

## Historical repository suite

The unfiltered historical suite reports **1,207 passed / 129 failed**. The failures are accumulated historical release-contract tests that intentionally hard-code earlier current versions, asset filenames, README headings, and predecessor identities. No v2.14 functional Julia/runtime test is among those failures.

## v2.14 runtime scope

Julia is promoted from a registered adapter to a real server-configured runtime with eight bounded operations:

1. `workspace.polyglot.julia.ode-linear-rk4`
2. `workspace.polyglot.julia.lotka-volterra`
3. `workspace.polyglot.julia.monte-carlo-normal`
4. `workspace.polyglot.julia.quadratic-optimize`
5. `workspace.polyglot.julia.eigen-analysis`
6. `workspace.polyglot.julia.integrate-series`
7. `workspace.polyglot.julia.polynomial-roots`
8. `workspace.polyglot.julia.parameter-sweep`

The Julia service accepts no client-supplied Julia source, expressions, packages, runtime URLs, credentials, or shell commands. It invokes a fixed `/app/runner.jl` only.

## Persistence and provenance

Migration 014 creates `workspace_numerical_simulation_receipts`. Successful Julia jobs persist:

- the content-addressed result artifact;
- the normal polyglot execution receipt; and
- a numerical-simulation receipt with model kind, solver, steps, seed, metrics, request fingerprint, artifact ID and SHA-256.

## Runtime isolation

The release Docker contract requires the Julia runtime to use:

- dedicated `sc-workspace-julia-runtime` container;
- internal-only runtime network;
- no host-published port;
- read-only root filesystem;
- `cap_drop: ALL`;
- `no-new-privileges`;
- 2 CPU limit;
- 2 GiB memory limit;
- 128 PID limit;
- bounded `/tmp` tmpfs.

## Live-runtime verification boundary

The current build environment does not expose Docker or a Julia executable, so a real Julia process could not be executed locally during packaging. The VPS installer therefore contains a mandatory deployment smoke test that:

- starts the real Julia container;
- verifies its health and eight-operation allowlist;
- queues `workspace.polyglot.julia.ode-linear-rk4` through the durable Workspace worker;
- solves `dy/dt = -y`, `y(0)=1`, `dt=0.1`, 10 steps;
- requires a final state between 0.36 and 0.38 (approximately `e^-1`);
- verifies result artifact, polyglot receipt and numerical-simulation receipt persistence; and
- verifies the Julia container sandbox and internal-only network.

That VPS smoke is required to close the live v2.14 deployment.

## Package replay

- Actual v2.14 tiny-patch ZIP replayed onto a clean v2.13 repository baseline: **PASS**
- Changed/new files compared byte-for-byte against release source: **33/33 matched**
- Replayed targeted gate: **61 passed, 3 historical lineage assertions deselected**
- Replayed WordPress PHP syntax and deployment shell syntax: **PASS**
- Actual backend ZIP replay: **26/26 backend tests passed**, Python compilation passed, deployment shell syntax passed, Julia runtime files and migration 014 present.
