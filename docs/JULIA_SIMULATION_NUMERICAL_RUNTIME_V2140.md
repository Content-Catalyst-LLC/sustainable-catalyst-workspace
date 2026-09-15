# Julia Simulation & Numerical Modeling Runtime — v2.14.0

The v2.14 Julia runtime is a dedicated internal service behind the Workspace polyglot execution fabric. It uses a fixed Julia runner and a bounded operation registry rather than an interactive Julia shell.

The service runs on the internal `sc-workspace-runtime` Docker network with no host-published port. The container uses a read-only root filesystem, dropped Linux capabilities, `no-new-privileges`, bounded CPU/memory/PIDs, and `/tmp` as its only writable runtime area.

Each successful model/simulation creates a content-addressed result artifact, a polyglot execution receipt, and a numerical simulation receipt containing runtime, solver, step/seed metadata, request fingerprint, and result digest.
