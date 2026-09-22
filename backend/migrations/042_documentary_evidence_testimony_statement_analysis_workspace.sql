CREATE TABLE IF NOT EXISTS workspace_investigation_document_heads (
    user_key varchar(128) NOT NULL, document_id varchar(160) NOT NULL, project_id varchar(160) NOT NULL,
    document_type varchar(48) NOT NULL, title varchar(1000) NOT NULL, description text NOT NULL DEFAULT '',
    source_ref varchar(2000) NOT NULL, source_fingerprint varchar(128) NOT NULL, authority varchar(500) NOT NULL DEFAULT '',
    published_at varchar(64) NOT NULL DEFAULT '', review_state varchar(32) NOT NULL DEFAULT 'open',
    revision integer NOT NULL DEFAULT 1, document_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, document_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_document_heads_project_idx ON workspace_investigation_document_heads(user_key, project_id, document_type, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_document_heads_fp_idx ON workspace_investigation_document_heads(user_key, project_id, document_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_investigation_document_revisions (
    user_key varchar(128) NOT NULL, document_id varchar(160) NOT NULL, revision integer NOT NULL, project_id varchar(160) NOT NULL,
    document_type varchar(48) NOT NULL, title varchar(1000) NOT NULL, description text NOT NULL DEFAULT '',
    source_ref varchar(2000) NOT NULL, source_fingerprint varchar(128) NOT NULL, authority varchar(500) NOT NULL DEFAULT '',
    published_at varchar(64) NOT NULL DEFAULT '', review_state varchar(32) NOT NULL DEFAULT 'open',
    document_fingerprint varchar(64) NOT NULL, metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, document_id, revision)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_document_revisions_project_idx ON workspace_investigation_document_revisions(user_key, project_id, document_id, revision DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_document_excerpts (
    user_key varchar(128) NOT NULL, excerpt_id varchar(160) NOT NULL, project_id varchar(160) NOT NULL,
    document_id varchar(160) NOT NULL, text text NOT NULL, locator varchar(1000) NOT NULL,
    document_fingerprint varchar(64) NOT NULL, excerpt_fingerprint varchar(64) NOT NULL,
    note text NOT NULL DEFAULT '', metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, excerpt_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_document_excerpts_fp_idx ON workspace_investigation_document_excerpts(user_key, project_id, excerpt_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_document_excerpts_document_idx ON workspace_investigation_document_excerpts(user_key, project_id, document_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_testimony_heads (
    user_key varchar(128) NOT NULL, testimony_id varchar(160) NOT NULL, project_id varchar(160) NOT NULL,
    testimony_type varchar(48) NOT NULL, title varchar(1000) NOT NULL, text text NOT NULL,
    speaker_entity_id varchar(160) NOT NULL DEFAULT '', source_document_id varchar(160) NOT NULL DEFAULT '',
    source_ref varchar(2000) NOT NULL DEFAULT '', source_fingerprint varchar(128) NOT NULL,
    occurred_at varchar(64) NOT NULL DEFAULT '', review_state varchar(32) NOT NULL DEFAULT 'open',
    revision integer NOT NULL DEFAULT 1, testimony_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, testimony_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_testimony_heads_project_idx ON workspace_investigation_testimony_heads(user_key, project_id, speaker_entity_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_testimony_heads_fp_idx ON workspace_investigation_testimony_heads(user_key, project_id, testimony_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_investigation_testimony_revisions (
    user_key varchar(128) NOT NULL, testimony_id varchar(160) NOT NULL, revision integer NOT NULL, project_id varchar(160) NOT NULL,
    testimony_type varchar(48) NOT NULL, title varchar(1000) NOT NULL, text text NOT NULL,
    speaker_entity_id varchar(160) NOT NULL DEFAULT '', source_document_id varchar(160) NOT NULL DEFAULT '',
    source_ref varchar(2000) NOT NULL DEFAULT '', source_fingerprint varchar(128) NOT NULL,
    occurred_at varchar(64) NOT NULL DEFAULT '', review_state varchar(32) NOT NULL DEFAULT 'open',
    testimony_fingerprint varchar(64) NOT NULL, metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, testimony_id, revision)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_testimony_revisions_project_idx ON workspace_investigation_testimony_revisions(user_key, project_id, testimony_id, revision DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_documentary_context_links (
    user_key varchar(128) NOT NULL, link_id varchar(160) NOT NULL, project_id varchar(160) NOT NULL,
    source_kind varchar(48) NOT NULL, source_id varchar(160) NOT NULL,
    target_kind varchar(48) NOT NULL, target_ref varchar(2000) NOT NULL, relation varchar(64) NOT NULL,
    source_fingerprint varchar(128) NOT NULL DEFAULT '', note text NOT NULL DEFAULT '',
    link_fingerprint varchar(64) NOT NULL, metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, link_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_documentary_context_links_fp_idx ON workspace_investigation_documentary_context_links(user_key, project_id, link_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_documentary_context_links_source_idx ON workspace_investigation_documentary_context_links(user_key, project_id, source_kind, source_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_documentary_context_links_target_idx ON workspace_investigation_documentary_context_links(user_key, project_id, target_kind, target_ref);

CREATE TABLE IF NOT EXISTS workspace_investigation_testimony_relations (
    user_key varchar(128) NOT NULL, relation_id varchar(160) NOT NULL, project_id varchar(160) NOT NULL,
    from_testimony_id varchar(160) NOT NULL, to_testimony_id varchar(160) NOT NULL, relation varchar(64) NOT NULL,
    note text NOT NULL DEFAULT '', relation_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, relation_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_testimony_relations_fp_idx ON workspace_investigation_testimony_relations(user_key, project_id, relation_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_testimony_relations_from_idx ON workspace_investigation_testimony_relations(user_key, project_id, from_testimony_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_testimony_relations_to_idx ON workspace_investigation_testimony_relations(user_key, project_id, to_testimony_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_documentary_snapshots (
    user_key varchar(128) NOT NULL, snapshot_id varchar(160) NOT NULL, project_id varchar(160) NOT NULL,
    graph_fingerprint varchar(64) NOT NULL, analysis_fingerprint varchar(64) NOT NULL,
    snapshot_fingerprint varchar(64) NOT NULL, document_count integer NOT NULL DEFAULT 0,
    excerpt_count integer NOT NULL DEFAULT 0, testimony_count integer NOT NULL DEFAULT 0,
    context_link_count integer NOT NULL DEFAULT 0, testimony_relation_count integer NOT NULL DEFAULT 0,
    issue_count integer NOT NULL DEFAULT 0, context_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, snapshot_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_documentary_snapshots_project_idx ON workspace_investigation_documentary_snapshots(user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_documentary_snapshots_fp_idx ON workspace_investigation_documentary_snapshots(user_key, project_id, snapshot_fingerprint);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sc_workspace') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
            workspace_investigation_document_heads,
            workspace_investigation_document_revisions,
            workspace_investigation_document_excerpts,
            workspace_investigation_testimony_heads,
            workspace_investigation_testimony_revisions,
            workspace_investigation_documentary_context_links,
            workspace_investigation_testimony_relations,
            workspace_investigation_documentary_snapshots
        TO sc_workspace;
    END IF;
END $$;
