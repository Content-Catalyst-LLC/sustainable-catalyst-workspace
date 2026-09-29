# Validation Report — Workspace v3.42.0

## Release

**Workspace v3.42.0 — Advanced Accelerator Scheduling & Resource Governance**

Baseline and rollback: v3.41.0.1. Database migration: none.

## Certification results

- Authoritative overlay: **16 files applied successfully** to a clean v3.41.0.1 repository.
- Neural compatibility suite: **61/61 tests passed** across v3.33.0 through v3.42.0, including the v3.39.0.1 persistence repair and v3.41.0.1 frontend continuity repair.
- Neural runtime registry: **125 bounded operations**.
- Workspace polyglot neural registry: **125 operations**, including all eight v3.42 accelerator scheduling operations.
- Python compile: passed for backend configuration, API, polyglot bridge, and neural runtime.
- WordPress PHP syntax: passed for plugin bootstrap, Workspace class, and deployment hardening class.
- Frontend continuity: v3.42.0 current CSS **350,524 bytes**; current JS **5,618 bytes**; substantive cumulative asset checks pass.
- Canonical plugin root: `sustainable-catalyst-workspace`.
- Deployer: Bash syntax passes; all five embedded Python certification blocks parse successfully.

## Governance assertions

- Accelerator inventory is bound to existing governed v3.41 worker IDs and declared `cuda:N` devices.
- Requested capabilities must be supported by the owning governed worker before placement eligibility.
- Quota, admission, placement, reservation, preemption, and scheduling decisions are explicit artifacts with fingerprints and lineage.
- Reservation plans do not commit resources; preemption plans do not execute preemption and require operator approval when candidates are selected.
- Client-supplied scheduler/cluster URLs, cloud credentials/tokens, kubeconfig/Slurm configuration, SSH material, worker endpoints, and executable payloads are not accepted as scheduling controls.
- Infrastructure mutation is disabled in the neural runtime.
- Scheduling artifacts remain `isObservedEvidence=false`.
