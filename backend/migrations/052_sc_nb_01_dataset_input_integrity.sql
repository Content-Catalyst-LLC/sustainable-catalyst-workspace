-- SC-NB-01 input integrity: dataset revisions pin the exact artifact snapshot they were registered
-- against. Existing rows keep artifact_sha256 = '' and cannot be bound as verified job inputs until
-- re-registered (a new dataset revision), so no historical record is silently upgraded.
ALTER TABLE workspace_dataset_heads ADD COLUMN IF NOT EXISTS artifact_revision INTEGER NOT NULL DEFAULT 0;
ALTER TABLE workspace_dataset_heads ADD COLUMN IF NOT EXISTS artifact_sha256 VARCHAR(64) NOT NULL DEFAULT '';
ALTER TABLE workspace_dataset_revisions ADD COLUMN IF NOT EXISTS artifact_revision INTEGER NOT NULL DEFAULT 0;
ALTER TABLE workspace_dataset_revisions ADD COLUMN IF NOT EXISTS artifact_sha256 VARCHAR(64) NOT NULL DEFAULT '';
