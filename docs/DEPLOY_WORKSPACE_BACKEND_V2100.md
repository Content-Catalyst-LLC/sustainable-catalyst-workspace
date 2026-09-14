# Deploy Workspace Backend v2.10.0

The v2.10 upgrader preserves the prior `.env`, service token, dedicated runtime-attestation token, PostgreSQL database, and `sc-workspace-data` volume. It applies migrations 002–010, starts the API and worker on the existing Workspace port mapping, then exercises the v2.9 attestation path plus a v2.10 runtime-trust policy and downstream publication compliance verification.

The smoke test requires the final attestation verification to be `verified` and explicitly confirms that compliance receipts do not grant execution authorization.
