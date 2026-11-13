-- SC-FIG-04.1: owner-signed source rights notices for Research (append-only).
CREATE TABLE IF NOT EXISTS workspace_research_source_rights_notices (
    notice_id VARCHAR(96) PRIMARY KEY,
    user_key VARCHAR(128) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    dataset_id VARCHAR(160) NOT NULL,
    dataset_revision INTEGER NOT NULL,
    source_sha256 VARCHAR(64) NOT NULL,
    licence_status VARCHAR(32) NOT NULL,
    sequence INTEGER NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    notice_json JSONB NOT NULL,
    notice_sha256 VARCHAR(64) NOT NULL UNIQUE,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_workspace_source_rights_sequence UNIQUE (user_key, source_sha256, sequence)
);
CREATE INDEX IF NOT EXISTS ix_workspace_research_source_rights_notices_user_key
    ON workspace_research_source_rights_notices (user_key);

CREATE OR REPLACE FUNCTION workspace_source_rights_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'source rights notices are append-only';
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS workspace_source_rights_append_only ON workspace_research_source_rights_notices;
CREATE TRIGGER workspace_source_rights_append_only BEFORE UPDATE OR DELETE ON workspace_research_source_rights_notices
    FOR EACH ROW EXECUTE FUNCTION workspace_source_rights_append_only();
