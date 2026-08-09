# Project Version History & Restore Points — v0.23.0

The version-history ledger is Workspace-level state and does not change the canonical project schema. Each restore point stores a normalized project snapshot, byte estimate, and SHA-256 fingerprint. Restore is copy-based: `cloneProject()` remaps project/object/relationship identities, preventing a historical state from overwriting the active project. Limits: 20 points/project, 80/Workspace, 1.5 MB/point. Restore-point history is browser-local and is not synchronized to the account cloud store.
