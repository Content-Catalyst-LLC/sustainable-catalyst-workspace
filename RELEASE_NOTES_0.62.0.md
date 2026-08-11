# Sustainable Catalyst Workspace v0.62.0 — Product Hardening II: Persistence, Corruption & Recovery Integrity

## Purpose
Harden the browser-local persistence boundary so a failed, interrupted, or unexpectedly changed save is detectable before recovery becomes guesswork.

## Added
- Verified-save integrity receipts for the canonical `sc_workspace` browser-local state.
- A small write transaction journal that records pre-write and target fingerprints without duplicating the target Workspace payload.
- Interrupted-write reconciliation that can distinguish a completed write, an aborted-before-write state, and an unresolved transaction without rewriting canonical research.
- Checksum-bound last-known-good snapshots while retaining the existing `sc-workspace-last-known-good/1.0` envelope for compatibility.
- Persistence Integrity review surface with current-state, integrity-baseline, last-known-good, and write-journal status.
- Explicit current-state and last-known-good recovery candidate exports.
- Privacy-minimized persistence-integrity diagnostic export.
- REST contract: `/wp-json/sc-workspace/v1/persistence-integrity-contract`.

## Save protocol
1. Serialize the normalized Workspace state.
2. Preserve the previous readable state as last-known-good when possible.
3. Write a transaction journal containing fingerprints and sizes, not the target research payload.
4. Write the canonical state.
5. Read it back and require exact equality.
6. Write the verified-save integrity receipt and clear the journal.
7. If any step after staging fails, retain the journal and last-known-good state for diagnosis.

## Recovery behavior
- Unreadable canonical state continues to be quarantined and may be opened from last-known-good in memory.
- A readable state with an integrity mismatch is **not** overwritten automatically. Workspace loads it but surfaces an integrity-drift warning for review.
- Recovery candidate exports are manual-review artifacts and can contain private project/research content.
- Existing project/version restore-point workflows remain the preferred non-destructive path for selective recovery.

## Integrity boundary
v0.62 uses FNV-1a 32-bit only as a lightweight corruption/drift detector. It is **not encryption, authentication, tamper resistance, or a cryptographic signature**.

## Schema / governance
No canonical schema migration. Storage remains **35**, Project remains **20.0**, Project Export remains **20.0**, and Notebook Workspace remains **8.0**. No automatic canonical repair, overwrite, recovery apply, cloud upload, telemetry, or hidden score was added.
