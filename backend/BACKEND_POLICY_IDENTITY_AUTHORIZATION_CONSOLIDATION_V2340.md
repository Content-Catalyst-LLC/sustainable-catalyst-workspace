# Workspace v2.34.0 — Backend Policy, Identity & Authorization Consolidation

v2.34.0 centralizes Workspace authentication context, principal identity, route policy selection, authorization evaluation, and decision audit in the Python backend.

## Authority model

- The WordPress server proxy authenticates to Workspace with the configured backend service bearer token.
- `X-SC-User-ID` identifies the human WordPress user and is validated server-side as a numeric user key.
- The backend resolves the canonical principal as `wp-user:<id>` under the fixed `wordpress-proxy` service principal.
- Browser-supplied roles and scopes are not trusted.
- User data remains isolated by the existing PostgreSQL `user_key` boundary.
- Authorization policy is default-deny and route actions are mapped server-side before route logic executes.

## Bounded actions

The consolidated policy recognizes read, write, execute, synchronization, handoff preparation, handoff acceptance, authorization inspection, and authorization evaluation. Unknown actions are denied.

## Durable audit

Migration 031 adds `workspace_authorization_decision_receipts`. Explicit authorization evaluations persist principal, action, resource, effect, reason, policy identity/revision, context, and a deterministic SHA-256 decision fingerprint.

## Client boundary

The typed client can inspect its server-resolved identity and request bounded policy evaluation through the WordPress server proxy. Service credentials remain server-side, and the browser never becomes the authorization authority.
