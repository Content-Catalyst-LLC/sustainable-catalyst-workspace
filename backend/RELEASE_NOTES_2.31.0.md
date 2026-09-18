# Workspace v2.31.0 — Local-First Synchronization Protocol

Workspace v2.31.0 adds an offline-tolerant synchronization protocol without moving canonical authority into the browser. Clients may persist draft mutation envelopes in a local outbox. Every envelope carries a stable envelope ID, operation ID, device ID, base revision, optional base fingerprint, and client sequence. The backend validates the base revision/fingerprint, applies supported project/notebook mutations, writes a durable sync receipt, and requires deterministic canonical rehydration after both successful application and conflicts.

Conflicts are explicit and non-destructive. The server does not perform automatic semantic merges. Revision-vector reconciliation classifies server-ahead, client-ahead, missing-server, and up-to-date project states. Retry-safe envelope and operation IDs prevent duplicate application.

The v2.28.1 interaction repair, v2.29 typed WordPress proxy, and v2.30 thin-client state boundary remain intact.
