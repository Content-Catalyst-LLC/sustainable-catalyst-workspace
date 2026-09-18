# Workspace v2.24.0 — Backend Authority & Domain Service Consolidation

## Canonical-state rule

Workspace now applies the following architectural rule:

> Logic that determines what a canonical Workspace project or notebook means, whether it is valid, how its revision changes, how it is fingerprinted, how it is persisted, and what provenance accompanies the mutation belongs to the backend.

The browser remains a rich client for presentation, interaction, local drafts, selections, viewport state, and rendering.

## Authority profile

`GET /v1/domain-authority` returns `sc-workspace-domain-authority/1.0` with:

- `mode: server-authoritative`
- `canonicalStore: postgresql`
- `backendAuthoritativeState: true`
- `browserAuthoritativeState: false`
- `clientRole: presentation-interaction-local-drafts`

## Authoritative validation

`POST /v1/domain-authority/validate` validates project or notebook documents without persisting them. Project schemas 12.0 through 20.0 remain supported; notebook schema 3.0 remains supported. Duplicate explicit object/cell IDs are rejected.

## Mutation receipts

Every successful project/notebook backup, sync, or delete emits an immutable row in `workspace_domain_mutation_receipts` containing:

- object kind and ID
- command and status
- prior and resulting revision
- request SHA-256
- canonical document SHA-256
- validation decision
- revision/mutation policy context
- provenance context
- server timestamp

Receipts are discoverable through `/v1/domain-mutation-receipts`.

## Compatibility

Existing `/v1/projects` and `/v1/notebooks` API contracts remain in place. v2.24 consolidates authority behind those APIs rather than requiring a new frontend mutation protocol in the same release.
