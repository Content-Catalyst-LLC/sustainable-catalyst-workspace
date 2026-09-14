# Python Scientific Compute Runtime v2.11.0

Workspace scientific compute is a **registered-operation runtime** inside the existing durable Python worker. The worker receives a normal Workspace job whose `targetProduct` is `workspace` and whose `operation` is one of the `workspace.compute.*` entries exposed by `/v1/compute/operations`.

The client supplies declarative data and parameters, never Python source. Each operation validates shape, size, identifiers, finiteness, and operation-specific bounds before invoking NumPy, Pandas, SciPy, or SymPy.

Successful execution produces three linked records:
1. the durable Workspace job result;
2. a canonical JSON content-addressed artifact;
3. a durable compute execution receipt binding the job/request fingerprint to the artifact SHA-256 and engine version.

If the job is attached to an execution run, the artifact is also registered as a run output so reproduction fingerprints cover the scientific result.

Worker hardening is defense in depth, not a claim of per-job container isolation. v2.11 uses one bounded worker container with a read-only root, dropped capabilities, no-new-privileges, bounded tmpfs, and global CPU/memory/PID limits. More granular runtime sandboxes can remain specialist adapters in later releases.
