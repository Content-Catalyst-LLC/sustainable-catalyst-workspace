# v0.62.0 — Persistence, Corruption & Recovery Integrity

## Design goal
Make browser-local persistence failure observable and recoverable without turning a diagnostic signal into permission to rewrite user research.

## Canonical boundary
The canonical Workspace payload remains `localStorage['sc_workspace']`. v0.62 does not change Storage 35, Project 20.0, or Notebook Workspace 8.0.

## Auxiliary stores
- `sc_workspace_last_good_v1` — previous readable canonical state, now optionally checksum-bound.
- `sc_workspace_persistence_integrity_v0620` — metadata-only verified-save receipt.
- `sc_workspace_persistence_txn_v0620` — metadata-only prepared/failed transaction journal.
- `sc_workspace_recovery_v0_8_2` — retained quarantine store for damaged payloads.

The transaction journal intentionally does not store the target Workspace payload. This avoids doubling large-state storage pressure during every save.

## Transaction protocol
A normal save stages previous/target fingerprints, writes the canonical payload, reads it back byte-for-byte, then records a verified-save receipt and removes the journal. If the page or storage operation fails between those steps, the journal remains.

At startup Workspace may reconcile the journal only when the current bytes conclusively match either the prepared target or the pre-write state. Reconciliation updates/removes auxiliary metadata only. It never changes canonical project content.

## Integrity drift
A readable current payload that does not match the last verified-save receipt is classified as integrity drift. Workspace does not decide whether the cause is corruption, manual developer-tool editing, browser behavior, or another same-origin writer. It preserves and loads the readable state and asks for review.

## Recovery exports
The Persistence Integrity surface can explicitly export:
- the current canonical state as a recovery candidate;
- the last-known-good snapshot as a recovery candidate;
- a metadata-only integrity diagnostic.

The two recovery candidates contain Workspace content and must be treated as private research files. The diagnostic excludes raw project content.

## Non-claims
The FNV-1a receipt is a lightweight drift detector. It provides no encryption, authentication, authorization, cryptographic integrity, or malicious-tamper resistance.

## Failure policy
When evidence is ambiguous, preserve evidence and require a human decision. v0.62 therefore does not automatically overwrite a readable canonical state, apply a recovery candidate, delete quarantine material, or upload recovery data.
