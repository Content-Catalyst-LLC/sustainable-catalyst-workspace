-- Workspace v2.4.0 — Dataset, Model & Execution Run Registry
-- Additive migration. No existing project, notebook, artifact, job, or recovery rows are altered or deleted.

CREATE TABLE IF NOT EXISTS workspace_dataset_heads (
    user_key varchar(128) NOT NULL,
    dataset_id varchar(160) NOT NULL,
    project_id varchar(160) NOT NULL DEFAULT '',
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    dataset_type varchar(64) NOT NULL DEFAULT 'other',
    source_kind varchar(64) NOT NULL DEFAULT 'metadata',
    artifact_id varchar(160) NOT NULL DEFAULT '',
    external_uri text NOT NULL DEFAULT '',
    revision integer NOT NULL DEFAULT 1,
    fingerprint varchar(64) NOT NULL,
    last_operation_id varchar(160) NOT NULL DEFAULT '',
    schema_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    lineage_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    tags_json jsonb NOT NULL DEFAULT '[]'::jsonb,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, dataset_id)
);

CREATE TABLE IF NOT EXISTS workspace_dataset_revisions (
    user_key varchar(128) NOT NULL,
    dataset_id varchar(160) NOT NULL,
    revision integer NOT NULL,
    project_id varchar(160) NOT NULL DEFAULT '',
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    dataset_type varchar(64) NOT NULL DEFAULT 'other',
    source_kind varchar(64) NOT NULL DEFAULT 'metadata',
    artifact_id varchar(160) NOT NULL DEFAULT '',
    external_uri text NOT NULL DEFAULT '',
    fingerprint varchar(64) NOT NULL,
    operation_id varchar(160) NOT NULL DEFAULT '',
    schema_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    lineage_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    tags_json jsonb NOT NULL DEFAULT '[]'::jsonb,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, dataset_id, revision)
);

CREATE INDEX IF NOT EXISTS workspace_dataset_heads_project_idx ON workspace_dataset_heads (user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_dataset_revisions_lookup_idx ON workspace_dataset_revisions (user_key, dataset_id, revision DESC);

CREATE TABLE IF NOT EXISTS workspace_model_heads (
    user_key varchar(128) NOT NULL,
    model_id varchar(160) NOT NULL,
    project_id varchar(160) NOT NULL DEFAULT '',
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    model_kind varchar(64) NOT NULL DEFAULT 'custom',
    framework varchar(160) NOT NULL DEFAULT '',
    algorithm varchar(160) NOT NULL DEFAULT '',
    version_label varchar(96) NOT NULL DEFAULT '',
    source_artifact_id varchar(160) NOT NULL DEFAULT '',
    execution_target varchar(64) NOT NULL DEFAULT '',
    execution_operation varchar(160) NOT NULL DEFAULT '',
    revision integer NOT NULL DEFAULT 1,
    fingerprint varchar(64) NOT NULL,
    last_operation_id varchar(160) NOT NULL DEFAULT '',
    input_schema_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    output_schema_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    configuration_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    lineage_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    tags_json jsonb NOT NULL DEFAULT '[]'::jsonb,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, model_id)
);

CREATE TABLE IF NOT EXISTS workspace_model_revisions (
    user_key varchar(128) NOT NULL,
    model_id varchar(160) NOT NULL,
    revision integer NOT NULL,
    project_id varchar(160) NOT NULL DEFAULT '',
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    model_kind varchar(64) NOT NULL DEFAULT 'custom',
    framework varchar(160) NOT NULL DEFAULT '',
    algorithm varchar(160) NOT NULL DEFAULT '',
    version_label varchar(96) NOT NULL DEFAULT '',
    source_artifact_id varchar(160) NOT NULL DEFAULT '',
    execution_target varchar(64) NOT NULL DEFAULT '',
    execution_operation varchar(160) NOT NULL DEFAULT '',
    fingerprint varchar(64) NOT NULL,
    operation_id varchar(160) NOT NULL DEFAULT '',
    input_schema_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    output_schema_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    configuration_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    lineage_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    tags_json jsonb NOT NULL DEFAULT '[]'::jsonb,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, model_id, revision)
);

CREATE INDEX IF NOT EXISTS workspace_model_heads_project_idx ON workspace_model_heads (user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_model_revisions_lookup_idx ON workspace_model_revisions (user_key, model_id, revision DESC);

CREATE TABLE IF NOT EXISTS workspace_parameter_set_heads (
    user_key varchar(128) NOT NULL,
    parameter_set_id varchar(160) NOT NULL,
    project_id varchar(160) NOT NULL DEFAULT '',
    model_id varchar(160) NOT NULL DEFAULT '',
    name text NOT NULL,
    revision integer NOT NULL DEFAULT 1,
    fingerprint varchar(64) NOT NULL,
    last_operation_id varchar(160) NOT NULL DEFAULT '',
    parameters_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, parameter_set_id)
);

CREATE TABLE IF NOT EXISTS workspace_parameter_set_revisions (
    user_key varchar(128) NOT NULL,
    parameter_set_id varchar(160) NOT NULL,
    revision integer NOT NULL,
    project_id varchar(160) NOT NULL DEFAULT '',
    model_id varchar(160) NOT NULL DEFAULT '',
    name text NOT NULL,
    fingerprint varchar(64) NOT NULL,
    operation_id varchar(160) NOT NULL DEFAULT '',
    parameters_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, parameter_set_id, revision)
);

CREATE INDEX IF NOT EXISTS workspace_parameter_set_model_idx ON workspace_parameter_set_heads (user_key, model_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS workspace_execution_runs (
    user_key varchar(128) NOT NULL,
    run_id varchar(96) NOT NULL,
    project_id varchar(160) NOT NULL DEFAULT '',
    name text NOT NULL DEFAULT 'Execution run',
    status varchar(32) NOT NULL DEFAULT 'planned',
    progress integer NOT NULL DEFAULT 0,
    job_id varchar(96) NOT NULL DEFAULT '',
    target_product varchar(64) NOT NULL DEFAULT 'workspace',
    operation varchar(160) NOT NULL DEFAULT '',
    dataset_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    model_ref jsonb NOT NULL DEFAULT '{}'::jsonb,
    parameter_set_ref jsonb NOT NULL DEFAULT '{}'::jsonb,
    environment_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    input_fingerprint varchar(64) NOT NULL,
    reproducibility_fingerprint varchar(64) NOT NULL,
    result_summary jsonb NOT NULL DEFAULT '{}'::jsonb,
    error_code varchar(96) NOT NULL DEFAULT '',
    error_message text NOT NULL DEFAULT '',
    idempotency_key varchar(160) NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz NULL,
    finished_at timestamptz NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, run_id)
);

CREATE TABLE IF NOT EXISTS workspace_execution_run_outputs (
    user_key varchar(128) NOT NULL,
    run_id varchar(96) NOT NULL,
    output_id varchar(160) NOT NULL,
    artifact_id varchar(160) NOT NULL DEFAULT '',
    role varchar(64) NOT NULL DEFAULT 'result',
    label text NOT NULL DEFAULT '',
    media_type varchar(255) NOT NULL DEFAULT 'application/octet-stream',
    sha256 varchar(64) NOT NULL DEFAULT '',
    bytes bigint NOT NULL DEFAULT 0,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, run_id, output_id)
);

CREATE TABLE IF NOT EXISTS workspace_execution_run_events (
    user_key varchar(128) NOT NULL,
    run_id varchar(96) NOT NULL,
    sequence integer NOT NULL,
    event_type varchar(64) NOT NULL,
    status varchar(32) NOT NULL,
    progress integer NOT NULL DEFAULT 0,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, run_id, sequence)
);

CREATE INDEX IF NOT EXISTS workspace_execution_runs_status_idx ON workspace_execution_runs (user_key, status, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_execution_runs_project_idx ON workspace_execution_runs (user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_execution_runs_job_idx ON workspace_execution_runs (user_key, job_id) WHERE job_id <> '';
CREATE UNIQUE INDEX IF NOT EXISTS workspace_execution_runs_idempotency_idx ON workspace_execution_runs (user_key, idempotency_key) WHERE idempotency_key <> '';
CREATE INDEX IF NOT EXISTS workspace_execution_run_events_idx ON workspace_execution_run_events (user_key, run_id, sequence);

ALTER TABLE workspace_jobs ADD COLUMN IF NOT EXISTS execution_run_id varchar(96) NOT NULL DEFAULT '';
CREATE INDEX IF NOT EXISTS workspace_jobs_execution_run_idx ON workspace_jobs (user_key, execution_run_id) WHERE execution_run_id <> '';
