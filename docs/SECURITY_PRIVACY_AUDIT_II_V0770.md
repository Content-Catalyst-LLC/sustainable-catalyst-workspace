# Workspace v0.77.0 — Security & Privacy Audit II

v0.77.0 re-audits Workspace after the public-beta hardening sequence. It does not add encryption, remote authorization, background security scanning, or automatic remediation.

## Runtime audit

The Security & Privacy surface now includes an Audit II panel that inspects metadata about Workspace-owned localStorage and sessionStorage surfaces, secure-context state, embedded-context state, and the count of script-readable Workspace-like cookie names. The report intentionally excludes storage values, storage key names, project content, source URLs, queries, account identity, device identity, user agent, referrer text, cookie names, and cookie values.

## Release-time source gates

The v0.77 release validator fails closed if the current plugin violates any of these release rules:

- cloud project/notebook REST routes must use the authenticated `cloud_permission` callback;
- public Workspace contract routes remain metadata-only GET contracts;
- current JavaScript assets may not introduce `eval`, `new Function`, or `document.write`;
- current assets may not contain obvious embedded secret/private-key literals;
- the current network-bearing application shell must keep cloud fetches same-origin and credential-scoped;
- the WordPress plugin header must remain inside WordPress's 8 KiB parser window;
- the WordPress enqueue graph must remain cycle-free.

These checks are release controls, not a penetration test or formal security certification.

## Existing boundaries retained

- Browser-local storage is not claimed to be application-level encrypted.
- FNV integrity receipts are not authentication or encryption.
- Durable references are not authorization credentials.
- Account/cloud deletion remains separate from local deletion.
- Workspace does not automatically delete, upload, disclose, repair, synchronize, or mutate canonical project data as part of the audit.
- Storage remains 35 and Project remains `sc-workspace-project/20.0`.
