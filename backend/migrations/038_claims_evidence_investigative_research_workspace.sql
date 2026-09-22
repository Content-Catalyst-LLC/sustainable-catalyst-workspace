BEGIN;

CREATE TABLE IF NOT EXISTS workspace_investigation_statement_heads (
    user_key VARCHAR(128) NOT NULL,
    statement_id VARCHAR(160) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    statement_type VARCHAR(32) NOT NULL,
    title VARCHAR(500) NOT NULL DEFAULT '',
    statement_text TEXT NOT NULL,
    review_state VARCHAR(32) NOT NULL DEFAULT 'open',
    revision INTEGER NOT NULL DEFAULT 1,
    statement_fingerprint VARCHAR(64) NOT NULL,
    tags_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, statement_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_statement_project_idx
    ON workspace_investigation_statement_heads (user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_statement_type_idx
    ON workspace_investigation_statement_heads (user_key, project_id, statement_type);

CREATE TABLE IF NOT EXISTS workspace_investigation_statement_revisions (
    user_key VARCHAR(128) NOT NULL,
    statement_id VARCHAR(160) NOT NULL,
    revision INTEGER NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    statement_type VARCHAR(32) NOT NULL,
    title VARCHAR(500) NOT NULL DEFAULT '',
    statement_text TEXT NOT NULL,
    review_state VARCHAR(32) NOT NULL DEFAULT 'open',
    statement_fingerprint VARCHAR(64) NOT NULL,
    tags_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, statement_id, revision)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_statement_revision_project_idx
    ON workspace_investigation_statement_revisions (user_key, project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_evidence_links (
    user_key VARCHAR(128) NOT NULL,
    evidence_link_id VARCHAR(96) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    statement_id VARCHAR(160) NOT NULL,
    evidence_ref VARCHAR(1200) NOT NULL,
    evidence_kind VARCHAR(120) NOT NULL DEFAULT 'external-reference',
    relation VARCHAR(48) NOT NULL,
    source_fingerprint VARCHAR(128) NOT NULL DEFAULT '',
    locator VARCHAR(1000) NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    link_fingerprint VARCHAR(64) NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, evidence_link_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_evidence_project_idx
    ON workspace_investigation_evidence_links (user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_evidence_statement_idx
    ON workspace_investigation_evidence_links (user_key, statement_id, created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_evidence_fingerprint_idx
    ON workspace_investigation_evidence_links (user_key, project_id, link_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_investigation_statement_relations (
    user_key VARCHAR(128) NOT NULL,
    relation_id VARCHAR(96) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    from_statement_id VARCHAR(160) NOT NULL,
    to_statement_id VARCHAR(160) NOT NULL,
    relation VARCHAR(48) NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    relation_fingerprint VARCHAR(64) NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, relation_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_statement_relation_project_idx
    ON workspace_investigation_statement_relations (user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_statement_relation_from_idx
    ON workspace_investigation_statement_relations (user_key, from_statement_id);
CREATE INDEX IF NOT EXISTS workspace_investigation_statement_relation_to_idx
    ON workspace_investigation_statement_relations (user_key, to_statement_id);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_statement_relation_fingerprint_idx
    ON workspace_investigation_statement_relations (user_key, project_id, relation_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_investigative_research_workspace_snapshots (
    user_key VARCHAR(128) NOT NULL,
    snapshot_id VARCHAR(96) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    graph_fingerprint VARCHAR(64) NOT NULL,
    workspace_fingerprint VARCHAR(64) NOT NULL,
    statement_count INTEGER NOT NULL DEFAULT 0,
    evidence_link_count INTEGER NOT NULL DEFAULT 0,
    statement_relation_count INTEGER NOT NULL DEFAULT 0,
    node_count INTEGER NOT NULL DEFAULT 0,
    edge_count INTEGER NOT NULL DEFAULT 0,
    context_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, snapshot_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigative_snapshot_project_idx
    ON workspace_investigative_research_workspace_snapshots (user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigative_snapshot_graph_idx
    ON workspace_investigative_research_workspace_snapshots (user_key, graph_fingerprint);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sc_workspace') THEN
        GRANT SELECT, INSERT, UPDATE ON workspace_investigation_statement_heads TO sc_workspace;
        GRANT SELECT, INSERT ON workspace_investigation_statement_revisions TO sc_workspace;
        GRANT SELECT, INSERT ON workspace_investigation_evidence_links TO sc_workspace;
        GRANT SELECT, INSERT ON workspace_investigation_statement_relations TO sc_workspace;
        GRANT SELECT, INSERT ON workspace_investigative_research_workspace_snapshots TO sc_workspace;
    END IF;
END $$;

COMMIT;
