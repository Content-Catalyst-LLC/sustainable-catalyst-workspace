CREATE TABLE IF NOT EXISTS workspace_investigation_entity_heads (
    user_key varchar(128) NOT NULL, entity_id varchar(160) NOT NULL, project_id varchar(160) NOT NULL,
    entity_type varchar(48) NOT NULL, canonical_name varchar(500) NOT NULL, description text NOT NULL DEFAULT '',
    review_state varchar(32) NOT NULL DEFAULT 'open', revision integer NOT NULL DEFAULT 1,
    entity_fingerprint varchar(64) NOT NULL, metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, entity_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_heads_project_idx ON workspace_investigation_entity_heads(user_key, project_id, entity_type, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_heads_name_idx ON workspace_investigation_entity_heads(user_key, project_id, canonical_name);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_heads_fp_idx ON workspace_investigation_entity_heads(user_key, project_id, entity_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_revisions (
    user_key varchar(128) NOT NULL, entity_id varchar(160) NOT NULL, revision integer NOT NULL, project_id varchar(160) NOT NULL,
    entity_type varchar(48) NOT NULL, canonical_name varchar(500) NOT NULL, description text NOT NULL DEFAULT '',
    review_state varchar(32) NOT NULL DEFAULT 'open', entity_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, entity_id, revision)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_revisions_project_idx ON workspace_investigation_entity_revisions(user_key, project_id, entity_id, revision DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_aliases (
    user_key varchar(128) NOT NULL, alias_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL, entity_id varchar(160) NOT NULL,
    alias varchar(500) NOT NULL, normalized_alias varchar(500) NOT NULL, alias_type varchar(48) NOT NULL DEFAULT 'name', language varchar(32) NOT NULL DEFAULT '',
    source_ref varchar(1200) NOT NULL DEFAULT '', source_fingerprint varchar(128) NOT NULL DEFAULT '', alias_fingerprint varchar(64) NOT NULL,
    note text NOT NULL DEFAULT '', metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, alias_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_entity_aliases_fp_idx ON workspace_investigation_entity_aliases(user_key, project_id, alias_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_aliases_lookup_idx ON workspace_investigation_entity_aliases(user_key, project_id, normalized_alias);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_aliases_entity_idx ON workspace_investigation_entity_aliases(user_key, project_id, entity_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_identifiers (
    user_key varchar(128) NOT NULL, identifier_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL, entity_id varchar(160) NOT NULL,
    namespace varchar(160) NOT NULL, value varchar(1000) NOT NULL, normalized_value varchar(1000) NOT NULL, status varchar(32) NOT NULL DEFAULT 'observed',
    source_ref varchar(1200) NOT NULL DEFAULT '', source_fingerprint varchar(128) NOT NULL DEFAULT '', identifier_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, identifier_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_entity_identifiers_fp_idx ON workspace_investigation_entity_identifiers(user_key, project_id, identifier_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_identifiers_lookup_idx ON workspace_investigation_entity_identifiers(user_key, project_id, namespace, normalized_value);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_identifiers_entity_idx ON workspace_investigation_entity_identifiers(user_key, project_id, entity_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_relationships (
    user_key varchar(128) NOT NULL, relationship_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL,
    from_entity_id varchar(160) NOT NULL, to_entity_id varchar(160) NOT NULL, relation varchar(64) NOT NULL,
    evidence_ref varchar(1200) NOT NULL DEFAULT '', source_fingerprint varchar(128) NOT NULL DEFAULT '', note text NOT NULL DEFAULT '',
    relationship_fingerprint varchar(64) NOT NULL, metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, relationship_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_entity_relationships_fp_idx ON workspace_investigation_entity_relationships(user_key, project_id, relationship_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_relationships_from_idx ON workspace_investigation_entity_relationships(user_key, project_id, from_entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_relationships_to_idx ON workspace_investigation_entity_relationships(user_key, project_id, to_entity_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_context_links (
    user_key varchar(128) NOT NULL, link_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL, entity_id varchar(160) NOT NULL,
    target_kind varchar(48) NOT NULL, target_ref varchar(1200) NOT NULL, relation varchar(64) NOT NULL,
    source_fingerprint varchar(128) NOT NULL DEFAULT '', note text NOT NULL DEFAULT '', link_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, link_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_entity_context_links_fp_idx ON workspace_investigation_entity_context_links(user_key, project_id, link_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_context_links_entity_idx ON workspace_investigation_entity_context_links(user_key, project_id, entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_context_links_target_idx ON workspace_investigation_entity_context_links(user_key, project_id, target_kind, target_ref);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_match_candidates (
    user_key varchar(128) NOT NULL, candidate_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL,
    left_entity_id varchar(160) NOT NULL, right_entity_id varchar(160) NOT NULL, basis_json jsonb NOT NULL DEFAULT '[]'::jsonb,
    signals_json jsonb NOT NULL DEFAULT '{}'::jsonb, source_ref varchar(1200) NOT NULL DEFAULT '', source_fingerprint varchar(128) NOT NULL DEFAULT '',
    review_state varchar(32) NOT NULL DEFAULT 'pending', review_note text NOT NULL DEFAULT '', candidate_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_key, candidate_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_entity_match_candidates_fp_idx ON workspace_investigation_entity_match_candidates(user_key, project_id, candidate_fingerprint);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_match_candidates_state_idx ON workspace_investigation_entity_match_candidates(user_key, project_id, review_state, updated_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_match_reviews (
    user_key varchar(128) NOT NULL, review_id varchar(96) NOT NULL, candidate_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL,
    review_state varchar(32) NOT NULL, note text NOT NULL DEFAULT '', review_fingerprint varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, review_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_match_reviews_candidate_idx ON workspace_investigation_entity_match_reviews(user_key, project_id, candidate_id, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_investigation_entity_resolution_snapshots (
    user_key varchar(128) NOT NULL, snapshot_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL,
    graph_fingerprint varchar(64) NOT NULL, diagnostics_fingerprint varchar(64) NOT NULL, snapshot_fingerprint varchar(64) NOT NULL,
    entity_count integer NOT NULL DEFAULT 0, relationship_count integer NOT NULL DEFAULT 0, context_link_count integer NOT NULL DEFAULT 0,
    match_candidate_count integer NOT NULL DEFAULT 0, unresolved_match_count integer NOT NULL DEFAULT 0,
    context_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_key, snapshot_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_resolution_snapshots_project_idx ON workspace_investigation_entity_resolution_snapshots(user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_entity_resolution_snapshots_fp_idx ON workspace_investigation_entity_resolution_snapshots(user_key, project_id, snapshot_fingerprint);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sc_workspace') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
            workspace_investigation_entity_heads,
            workspace_investigation_entity_revisions,
            workspace_investigation_entity_aliases,
            workspace_investigation_entity_identifiers,
            workspace_investigation_entity_relationships,
            workspace_investigation_entity_context_links,
            workspace_investigation_entity_match_candidates,
            workspace_investigation_entity_match_reviews,
            workspace_investigation_entity_resolution_snapshots
        TO sc_workspace;
    END IF;
END $$;
