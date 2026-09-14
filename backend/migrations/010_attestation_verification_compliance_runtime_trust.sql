-- Workspace v2.10.0 — Attestation Verification, Compliance Gates & Runtime Trust
CREATE TABLE IF NOT EXISTS workspace_runtime_trust_policy_heads (
  user_key VARCHAR(128) NOT NULL,
  trust_policy_id VARCHAR(160) NOT NULL,
  project_id VARCHAR(160) NOT NULL DEFAULT '', name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
  revision INTEGER NOT NULL DEFAULT 1, fingerprint VARCHAR(64) NOT NULL, last_operation_id VARCHAR(160) NOT NULL DEFAULT '',
  allowed_sources_json JSONB NOT NULL DEFAULT '[]'::jsonb, allowed_attestors_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  accepted_classifications_json JSONB NOT NULL DEFAULT '[]'::jsonb, require_budget_compliant BOOLEAN NOT NULL DEFAULT TRUE,
  require_sandbox_compliant BOOLEAN NOT NULL DEFAULT TRUE, require_evidence_digest BOOLEAN NOT NULL DEFAULT TRUE,
  allowed_sandbox_modes_json JSONB NOT NULL DEFAULT '[]'::jsonb, downstream_scopes_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, trust_policy_id)
);
CREATE TABLE IF NOT EXISTS workspace_runtime_trust_policy_revisions (
  user_key VARCHAR(128) NOT NULL, trust_policy_id VARCHAR(160) NOT NULL, revision INTEGER NOT NULL,
  project_id VARCHAR(160) NOT NULL DEFAULT '', name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', fingerprint VARCHAR(64) NOT NULL,
  operation_id VARCHAR(160) NOT NULL DEFAULT '', allowed_sources_json JSONB NOT NULL DEFAULT '[]'::jsonb, allowed_attestors_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  accepted_classifications_json JSONB NOT NULL DEFAULT '[]'::jsonb, require_budget_compliant BOOLEAN NOT NULL DEFAULT TRUE,
  require_sandbox_compliant BOOLEAN NOT NULL DEFAULT TRUE, require_evidence_digest BOOLEAN NOT NULL DEFAULT TRUE,
  allowed_sandbox_modes_json JSONB NOT NULL DEFAULT '[]'::jsonb, downstream_scopes_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, trust_policy_id, revision)
);
CREATE TABLE IF NOT EXISTS workspace_compliance_waivers (
  user_key VARCHAR(128) NOT NULL, waiver_id VARCHAR(96) NOT NULL, attestation_id VARCHAR(96) NOT NULL,
  downstream_scopes_json JSONB NOT NULL DEFAULT '[]'::jsonb, waived_checks_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  reason TEXT NOT NULL, human_authorized BOOLEAN NOT NULL DEFAULT TRUE, expires_at TIMESTAMPTZ NULL, notes TEXT NOT NULL DEFAULT '',
  fingerprint VARCHAR(64) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), PRIMARY KEY (user_key, waiver_id)
);
CREATE TABLE IF NOT EXISTS workspace_attestation_verification_receipts (
  user_key VARCHAR(128) NOT NULL, verification_id VARCHAR(96) NOT NULL, attestation_id VARCHAR(96) NOT NULL, attestation_fingerprint VARCHAR(64) NOT NULL,
  trust_policy_id VARCHAR(160) NOT NULL, trust_policy_revision INTEGER NOT NULL, trust_policy_fingerprint VARCHAR(64) NOT NULL,
  downstream_scope VARCHAR(64) NOT NULL, waiver_id VARCHAR(96) NOT NULL DEFAULT '', eligible BOOLEAN NOT NULL DEFAULT FALSE,
  classification VARCHAR(32) NOT NULL, checks_json JSONB NOT NULL DEFAULT '[]'::jsonb, notes TEXT NOT NULL DEFAULT '', fingerprint VARCHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), PRIMARY KEY (user_key, verification_id)
);
CREATE INDEX IF NOT EXISTS workspace_runtime_trust_policy_project_idx ON workspace_runtime_trust_policy_heads(user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_compliance_waiver_attestation_idx ON workspace_compliance_waivers(user_key, attestation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_attestation_verification_attestation_idx ON workspace_attestation_verification_receipts(user_key, attestation_id, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_runtime_trust_policy_heads, workspace_runtime_trust_policy_revisions, workspace_compliance_waivers, workspace_attestation_verification_receipts TO sc_workspace;
