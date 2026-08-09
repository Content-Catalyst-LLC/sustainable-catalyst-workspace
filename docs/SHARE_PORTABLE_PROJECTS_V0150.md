# v0.15.0 — Share & Portable Projects

Workspace v0.15.0 adds explicit whole-project portability without adding cloud sync or live collaboration. A portable project is a privacy-minimized copy created by the user. It preserves the project’s content-bearing research, analysis, decision, Canvas, traceability, briefing, guided-workflow, and canonical-object structures while excluding device persistence metadata, handoff/session state, recent-tool history, and account identity.

## Sharing modes

- **Portable Project JSON** — integrity-manifested package intended for another Workspace installation or device.
- **Static Review Copy HTML** — readable non-interactive snapshot for review outside Workspace.
- **Import as Copy** — validates the package and creates a new local project ID. Existing local projects are never overwritten automatically.

## Integrity

When Web Crypto is available, the package includes a SHA-256 fingerprint calculated across the manifest and privacy-minimized project payload. Workspace verifies that fingerprint before allowing import.

## Privacy boundary

Always excluded: device ID/persistence metadata, WordPress/account identity, local handoff state, browser session metadata, recent-tool history. Activity and Responsible AI review history are opt-in because they can contain contextual material unnecessary for project transfer.

## Non-goals

No public share links, no server upload, no collaborative editing, no background synchronization, no remote revocation, and no permission system are introduced in v0.15.0.
