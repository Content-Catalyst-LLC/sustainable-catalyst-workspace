# Workspace v2.30.0 — Thin Client State Architecture

Workspace now separates transient browser state from canonical Workspace state. The new TypeScript state runtime persists only an explicit transient allowlist, keeps canonical read models in a memory-only rehydratable cache, and routes canonical writes through backend commands. A new backend profile and bootstrap read model make the state boundary inspectable and fingerprinted. The v2.28.1 interaction repair and v2.29 typed-client proxy remain intact. No database migration is added; schema lineage remains through migration 028.
