# Cross-Device Continuity & Account Sync Productionization — v1.7.0

The v1.7.0 continuity layer makes the existing account-sync path production-auditable while preserving browser-local ownership. A cloud head is a continuity copy, not the canonical Workspace project.

The deterministic planner derives an explicit next action from authentication state, enrollment, local/cloud fingerprints, the last trusted common fingerprint, remote existence, revision metadata, and any preserved interrupted operation. It never applies the action automatically.

Exported continuity receipts are metadata-only. They exclude project content, query text, source URLs, account profile information, and device identifiers.
