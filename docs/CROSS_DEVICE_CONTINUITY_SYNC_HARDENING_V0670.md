# v0.67.0 Cross-Device Continuity & Sync Hardening

Workspace remains local-first. Cross-device continuity is explicit, account-scoped, revision-conditional, and recoverable. The v0.67 operation journal exists to distinguish a request that definitely completed from one whose result was not observed by the browser. Operation IDs provide idempotent retry for pushes. Pulls establish a local sync-safety restore point before canonical replacement. Device migration is portable-file based and imports as a new local copy with sync disabled.

Manual backup and sync are intentionally different operations. A manual backup may create or replace a manual-backup record, but it may not replace an active sync head because doing so would bypass the revision precondition.
