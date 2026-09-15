# Workspace v2.14.0 — Julia Read-Only Cache Repair

This backend-only repair addresses the live Julia HTTP 422 observed after the executable-path repair. The Julia sidecar correctly located `/usr/local/julia/bin/julia`, but `using JSON3` attempted to create compile-cache/lock state while `JULIA_DEPOT_PATH` pointed only at the immutable `/opt/julia-depot` on a read-only root filesystem.

The repair preserves the security boundary:

- `/opt/julia-depot` remains immutable.
- `/tmp/sc-julia-depot` is the only writable Julia depot layer and lives on the existing bounded tmpfs.
- `JULIA_DEPOT_PATH=/tmp/sc-julia-depot:/opt/julia-depot`.
- Julia package images are disabled (`--pkgimages=no`) so the no-exec tmpfs is used only for cache/lock data, not executable package images.
- The runtime project is pinned to `/opt/julia-depot/environments/v1.11`.
- Automatic package precompile mutation is disabled.
- Deployment now runs a direct sidecar RK4 smoke test before the durable Workspace job.
