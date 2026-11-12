-- SC-RIGHTS-02: transactional outbox for source-rights notices, append-only delivery log, Research sync state.
CREATE TABLE IF NOT EXISTS workspace_research_rights_outbox (
    notice_id VARCHAR(96) PRIMARY KEY,
    user_key VARCHAR(128) NOT NULL,
    source_sha256 VARCHAR(64) NOT NULL,
    sequence INTEGER NOT NULL,
    licence_status VARCHAR(32) NOT NULL,
    priority INTEGER NOT NULL,
    state VARCHAR(24) NOT NULL DEFAULT 'queued',
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    lease_owner VARCHAR(128) NOT NULL DEFAULT '',
    lease_expires_at TIMESTAMPTZ,
    last_http_status INTEGER,
    last_error_code VARCHAR(64) NOT NULL DEFAULT '',
    last_error TEXT NOT NULL DEFAULT '',
    research_receipt JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    first_attempt_at TIMESTAMPTZ,
    applied_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_workspace_rights_outbox_sequence UNIQUE (user_key, source_sha256, sequence)
);
CREATE INDEX IF NOT EXISTS ix_workspace_research_rights_outbox_user_key ON workspace_research_rights_outbox (user_key);
CREATE INDEX IF NOT EXISTS ix_workspace_research_rights_outbox_state ON workspace_research_rights_outbox (state);

CREATE TABLE IF NOT EXISTS workspace_research_rights_delivery_events (
    id BIGSERIAL PRIMARY KEY,
    notice_id VARCHAR(96) NOT NULL DEFAULT '',
    user_key VARCHAR(128) NOT NULL DEFAULT '',
    kind VARCHAR(24) NOT NULL,
    outcome VARCHAR(48) NOT NULL DEFAULT '',
    http_status INTEGER,
    detail JSONB NOT NULL DEFAULT '{}'::jsonb,
    at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_workspace_research_rights_delivery_events_notice_id ON workspace_research_rights_delivery_events (notice_id);
CREATE INDEX IF NOT EXISTS ix_workspace_research_rights_delivery_events_at ON workspace_research_rights_delivery_events (at);
CREATE OR REPLACE FUNCTION workspace_rights_delivery_events_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'rights delivery events are append-only';
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS workspace_rights_delivery_events_append_only ON workspace_research_rights_delivery_events;
CREATE TRIGGER workspace_rights_delivery_events_append_only BEFORE UPDATE OR DELETE
    ON workspace_research_rights_delivery_events FOR EACH ROW EXECUTE FUNCTION workspace_rights_delivery_events_append_only();

CREATE TABLE IF NOT EXISTS workspace_research_rights_sync_state (
    user_key VARCHAR(128) NOT NULL,
    source_sha256 VARCHAR(64) NOT NULL,
    research_status VARCHAR(32) NOT NULL,
    research_sequence INTEGER NOT NULL DEFAULT 0,
    workspace_sequence INTEGER NOT NULL DEFAULT 0,
    live_figures INTEGER NOT NULL DEFAULT 0,
    attestation_id VARCHAR(96) NOT NULL DEFAULT '',
    attested_at TIMESTAMPTZ,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, source_sha256)
);

-- Notices issued before the outbox existed (SC-FIG-04.1) are queued once; Research replays applied ones.
INSERT INTO workspace_research_rights_outbox (notice_id, user_key, source_sha256, sequence, licence_status, priority, created_at)
SELECT n.notice_id, n.user_key, n.source_sha256, n.sequence, n.licence_status,
       CASE WHEN n.licence_status = 'restricted' THEN 0 ELSE 1 END, n.issued_at
FROM workspace_research_source_rights_notices n
ON CONFLICT DO NOTHING;
