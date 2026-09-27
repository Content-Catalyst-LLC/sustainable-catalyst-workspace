# Workspace backend v3.22.0.2 — Contabo

No database migration. The live rollback baseline remains v3.21.0 because v3.22.0 and v3.22.0.1 were never promoted. The deployer first builds v3.22.0.2 and runs an isolated hardened pre-switch certification proving Dynamo import, cache identity, and Adam training under UID 65532. Only after that passes does it switch production and run the end-to-end Workspace job smoke test.
