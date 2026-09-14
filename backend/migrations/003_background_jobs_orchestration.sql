CREATE TABLE IF NOT EXISTS workspace_jobs (
    user_key VARCHAR(128) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    job_type VARCHAR(96) NOT NULL,
    target_product VARCHAR(64) NOT NULL,
    operation VARCHAR(160) NOT NULL,
    project_id VARCHAR(160) NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    priority INTEGER NOT NULL DEFAULT 5,
    attempt INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    progress INTEGER NOT NULL DEFAULT 0,
    idempotency_key VARCHAR(160) NOT NULL DEFAULT '',
    request_fingerprint VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_code VARCHAR(96) NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    cancellation_requested BOOLEAN NOT NULL DEFAULT FALSE,
    worker_id VARCHAR(160) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    queued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ NULL,
    finished_at TIMESTAMPTZ NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, job_id)
);
CREATE INDEX IF NOT EXISTS workspace_jobs_queue_idx ON workspace_jobs(status, priority DESC, queued_at ASC);
CREATE INDEX IF NOT EXISTS workspace_jobs_user_created_idx ON workspace_jobs(user_key, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_jobs_idempotency_idx ON workspace_jobs(user_key, idempotency_key) WHERE idempotency_key <> '';

CREATE TABLE IF NOT EXISTS workspace_job_events (
    user_key VARCHAR(128) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    sequence INTEGER NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, job_id, sequence)
);

CREATE TABLE IF NOT EXISTS workspace_worker_heartbeats (
    worker_id VARCHAR(160) PRIMARY KEY,
    version VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'idle',
    active_job_id VARCHAR(96) NOT NULL DEFAULT '',
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
