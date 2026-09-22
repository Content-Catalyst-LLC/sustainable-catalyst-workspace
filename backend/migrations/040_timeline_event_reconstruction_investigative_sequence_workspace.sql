CREATE TABLE IF NOT EXISTS workspace_investigation_event_heads (
    user_key varchar(128) NOT NULL,
    event_id varchar(160) NOT NULL,
    project_id varchar(160) NOT NULL,
    title varchar(500) NOT NULL,
    description text NOT NULL DEFAULT '',
    start_at timestamptz NULL,
    end_at timestamptz NULL,
    time_precision varchar(32) NOT NULL DEFAULT 'unknown',
    time_status varchar(32) NOT NULL DEFAULT 'unknown',
    location_ref varchar(1200) NOT NULL DEFAULT '',
    review_state varchar(32) NOT NULL DEFAULT 'open',
    revision integer NOT NULL DEFAULT 1,
    event_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, event_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_heads_project_idx
    ON workspace_investigation_event_heads(user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_heads_time_idx
    ON workspace_investigation_event_heads(user_key, project_id, start_at, end_at);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_heads_fingerprint_idx
    ON workspace_investigation_event_heads(user_key, project_id, event_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_investigation_event_revisions (
    user_key varchar(128) NOT NULL,
    event_id varchar(160) NOT NULL,
    revision integer NOT NULL,
    project_id varchar(160) NOT NULL,
    title varchar(500) NOT NULL,
    description text NOT NULL DEFAULT '',
    start_at timestamptz NULL,
    end_at timestamptz NULL,
    time_precision varchar(32) NOT NULL DEFAULT 'unknown',
    time_status varchar(32) NOT NULL DEFAULT 'unknown',
    location_ref varchar(1200) NOT NULL DEFAULT '',
    review_state varchar(32) NOT NULL DEFAULT 'open',
    event_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, event_id, revision)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_revisions_project_idx
    ON workspace_investigation_event_revisions(user_key, project_id, event_id, revision DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_event_statement_links (
    user_key varchar(128) NOT NULL,
    link_id varchar(96) NOT NULL,
    project_id varchar(160) NOT NULL,
    event_id varchar(160) NOT NULL,
    statement_id varchar(160) NOT NULL,
    relation varchar(48) NOT NULL,
    note text NOT NULL DEFAULT '',
    link_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, link_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_event_statement_links_fp_idx
    ON workspace_investigation_event_statement_links(user_key, project_id, link_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_statement_links_event_idx
    ON workspace_investigation_event_statement_links(user_key, project_id, event_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_statement_links_statement_idx
    ON workspace_investigation_event_statement_links(user_key, project_id, statement_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_event_relations (
    user_key varchar(128) NOT NULL,
    relation_id varchar(96) NOT NULL,
    project_id varchar(160) NOT NULL,
    from_event_id varchar(160) NOT NULL,
    to_event_id varchar(160) NOT NULL,
    relation varchar(48) NOT NULL,
    note text NOT NULL DEFAULT '',
    relation_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, relation_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_event_relations_fp_idx
    ON workspace_investigation_event_relations(user_key, project_id, relation_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_relations_from_idx
    ON workspace_investigation_event_relations(user_key, project_id, from_event_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_event_relations_to_idx
    ON workspace_investigation_event_relations(user_key, project_id, to_event_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_timeline_snapshots (
    user_key varchar(128) NOT NULL,
    snapshot_id varchar(96) NOT NULL,
    project_id varchar(160) NOT NULL,
    timeline_fingerprint varchar(64) NOT NULL,
    graph_fingerprint varchar(64) NOT NULL,
    snapshot_fingerprint varchar(64) NOT NULL,
    event_count integer NOT NULL DEFAULT 0,
    event_statement_link_count integer NOT NULL DEFAULT 0,
    event_relation_count integer NOT NULL DEFAULT 0,
    temporal_issue_count integer NOT NULL DEFAULT 0,
    context_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, snapshot_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_timeline_snapshots_project_idx
    ON workspace_investigation_timeline_snapshots(user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_timeline_snapshots_fp_idx
    ON workspace_investigation_timeline_snapshots(user_key, project_id, snapshot_fingerprint);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sc_workspace') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
            workspace_investigation_event_heads,
            workspace_investigation_event_revisions,
            workspace_investigation_event_statement_links,
            workspace_investigation_event_relations,
            workspace_investigation_timeline_snapshots
        TO sc_workspace;
    END IF;
END $$;
