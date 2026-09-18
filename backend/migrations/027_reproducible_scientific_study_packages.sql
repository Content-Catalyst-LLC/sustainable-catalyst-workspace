CREATE TABLE IF NOT EXISTS workspace_scientific_study_packages (
  user_key varchar(128) NOT NULL, package_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL, title text NOT NULL, description text NOT NULL DEFAULT '',
  project_revision integer NOT NULL DEFAULT 0, manifest_fingerprint varchar(64) NOT NULL, bundle_artifact_id varchar(160) NOT NULL, bundle_sha256 varchar(64) NOT NULL,
  bundle_bytes bigint NOT NULL DEFAULT 0, component_count integer NOT NULL DEFAULT 0, embedded_artifact_count integer NOT NULL DEFAULT 0, closure_verified boolean NOT NULL DEFAULT false,
  manifest_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (user_key, package_id)
);
CREATE INDEX IF NOT EXISTS workspace_scientific_study_packages_project_idx ON workspace_scientific_study_packages(user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_scientific_study_packages_manifest_idx ON workspace_scientific_study_packages(user_key, manifest_fingerprint);
CREATE TABLE IF NOT EXISTS workspace_scientific_study_package_receipts (
  user_key varchar(128) NOT NULL, receipt_id varchar(96) NOT NULL, package_id varchar(96) NOT NULL, action varchar(64) NOT NULL, status varchar(32) NOT NULL,
  manifest_fingerprint varchar(64) NOT NULL DEFAULT '', bundle_sha256 varchar(64) NOT NULL DEFAULT '', details_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_scientific_study_package_receipts_package_idx ON workspace_scientific_study_package_receipts(user_key, package_id, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_scientific_study_packages TO sc_workspace;
GRANT SELECT, INSERT ON workspace_scientific_study_package_receipts TO sc_workspace;
