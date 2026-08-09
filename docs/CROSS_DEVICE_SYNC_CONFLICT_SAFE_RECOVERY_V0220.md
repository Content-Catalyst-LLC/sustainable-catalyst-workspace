# Cross-Device Sync & Conflict-Safe Recovery — v0.22.0

Workspace sync is explicit, account-bound, and conflict-safe. The browser remains the primary working environment. An enrolled project is synchronized only when the user invokes **Sync now**.

## Comparison model

Each enrolled project tracks the last accepted server revision and common SHA-256 project fingerprint. Status is derived from the local fingerprint, cloud fingerprint/revision, and common base: not uploaded, up to date, local ahead, remote ahead, conflict, remote missing, or error.

## Conflict model

The server rejects stale sync pushes with HTTP 409. Workspace never applies silent last-write-wins. A remote-ahead project can be pulled in place only when local has not diverged. A true conflict presents three human-controlled paths: inspect the cloud copy, explicitly keep local as the new sync head, or accept cloud while preserving the divergent local project as a separate conflict copy.

## Boundaries

Guest use remains fully supported. Sign-in and enrollment do not upload project content. There is no background synchronization, periodic polling, team storage, organization permissions, or institutional sync.
