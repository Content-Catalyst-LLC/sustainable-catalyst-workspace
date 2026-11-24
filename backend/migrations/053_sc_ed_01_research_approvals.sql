-- SC-ED-01: authenticated, persisted Research publication approvals (records signed at decision time).
CREATE TABLE IF NOT EXISTS workspace_research_approval_grants (
    grant_id VARCHAR(96) PRIMARY KEY,
    owner_user_key VARCHAR(128) NOT NULL,
    grantee_user_key VARCHAR(128) NOT NULL,
    role VARCHAR(48) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at TIMESTAMPTZ NULL
);
CREATE INDEX IF NOT EXISTS ix_workspace_research_approval_grants_owner_user_key ON workspace_research_approval_grants (owner_user_key);
CREATE INDEX IF NOT EXISTS ix_workspace_research_approval_grants_grantee_user_key ON workspace_research_approval_grants (grantee_user_key);

CREATE TABLE IF NOT EXISTS workspace_research_approval_requests (
    approval_id VARCHAR(96) PRIMARY KEY,
    owner_user_key VARCHAR(128) NOT NULL,
    requester_user_key VARCHAR(128) NOT NULL,
    requester_auth VARCHAR(96) NOT NULL DEFAULT '',
    project_id VARCHAR(160) NOT NULL,
    dimension VARCHAR(32) NOT NULL,
    action VARCHAR(64) NOT NULL,
    subject_ref VARCHAR(320) NOT NULL,
    subject_title TEXT NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL,
    approval_json JSONB NOT NULL,
    decision_json JSONB NULL,
    record_json JSONB NULL,
    record_sha256 VARCHAR(64) NOT NULL DEFAULT '',
    decider_user_key VARCHAR(128) NOT NULL DEFAULT '',
    decider_auth VARCHAR(96) NOT NULL DEFAULT '',
    grant_id VARCHAR(96) NOT NULL DEFAULT '',
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at TIMESTAMPTZ NULL
);
CREATE INDEX IF NOT EXISTS ix_workspace_research_approval_requests_owner_user_key ON workspace_research_approval_requests (owner_user_key);
CREATE INDEX IF NOT EXISTS ix_workspace_research_approval_requests_requester_user_key ON workspace_research_approval_requests (requester_user_key);
CREATE INDEX IF NOT EXISTS ix_workspace_research_approval_requests_subject_ref ON workspace_research_approval_requests (subject_ref);

-- A decided request is final: only pending -> decided/withdrawn transitions are allowed, and nothing is deleted.
CREATE OR REPLACE FUNCTION workspace_research_approval_final() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'research approval requests are append-only';
    END IF;
    IF OLD.status <> 'pending' THEN
        RAISE EXCEPTION 'research approval request % is %, and final', OLD.approval_id, OLD.status;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS workspace_research_approval_final ON workspace_research_approval_requests;
CREATE TRIGGER workspace_research_approval_final BEFORE UPDATE OR DELETE ON workspace_research_approval_requests
    FOR EACH ROW EXECUTE FUNCTION workspace_research_approval_final();
