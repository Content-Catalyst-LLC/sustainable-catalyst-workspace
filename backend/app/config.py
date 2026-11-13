from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SC_WORKSPACE_", case_sensitive=False)

    service_name: str = "Sustainable Catalyst Workspace Backend"
    service_version: str = "3.83.0"
    environment: str = "production"
    database_url: str = "postgresql+psycopg://sc_workspace:change-me@127.0.0.1:5432/sc_workspace"
    database_url_file: str = ""  # Optional least-privilege authority DSN Docker secret path.
    service_token: str = ""
    session_signing_secret: str = ""
    session_signing_secret_file: str = ""  # Optional shared Workspace cookie-signing key, Docker secret path.
    session_cookie_name: str = "sc_workspace_session"
    session_issuer: str = "sustainable-catalyst-workspace"
    session_audience: str = "workspace.sustainablecatalyst.com"
    session_ttl_seconds: int = 28800
    # Separate secret for gated Research-to-Workspace introspection; never browser-facing.
    research_introspection_token: str = ""
    research_introspection_token_file: str = ""
    session_revocation_enforced: bool = False  # Enable only after migration + staging acceptance.
    # SC-AUTH-02: Sustainable Catalyst Identity (Platform Core OIDC provider).
    # Workspace is a confidential client (BFF); WordPress is never an identity source.
    sc_identity_issuer: str = ""  # exact public `iss`
    sc_identity_discovery_url: str = ""  # internal URL; defaults to issuer discovery
    sc_identity_client_id: str = ""
    sc_identity_client_secret: str = ""
    sc_identity_client_secret_file: str = ""
    sc_identity_redirect_uri: str = ""
    sc_identity_post_logout_redirect_uri: str = ""
    sc_identity_api_audience: str = "sc-workspace-api"
    sc_identity_allowed_bearer_clients: str = ""  # comma-separated azp allowlist; empty = no bearer clients
    sc_identity_require_mfa: bool = True
    sc_identity_mfa_amr: str = "otp,mfa,hwk,swk"
    sc_identity_step_up_max_age: int = 300
    # When true, legacy user context (service bearer + X-SC-User-ID) and the
    # trusted-service session exchange are refused.
    sc_identity_required: bool = False
    cors_allowed_origins: str = "https://workspace.sustainablecatalyst.com"
    # SC-SCI-02: Research Console origins added to the browser allowlist (CORS and the cookie-write Origin check),
    # without restating cors_allowed_origins.
    research_console_origins: str = ""
    # SC-SCI-02: sign-ins besides SC Identity that may receive a Research session. Only "erw-account-session"
    # (the existing ERW account sign-in, password only) is recognised; empty means SC Identity only.
    research_session_methods: str = ""
    auto_create_schema: bool = False

    max_projects_per_account: int = 100
    max_project_bytes: int = 10 * 1024 * 1024
    max_account_bytes: int = 512 * 1024 * 1024
    max_notebooks_per_account: int = 250
    max_notebook_bytes: int = 5 * 1024 * 1024

    object_storage_root: str = "/data/objects"
    max_artifacts_per_account: int = 500
    max_artifact_bytes: int = 25 * 1024 * 1024
    max_artifact_account_bytes: int = 2 * 1024 * 1024 * 1024
    max_recovery_snapshots_per_account: int = 50

    max_datasets_per_account: int = 500
    max_models_per_account: int = 250
    max_parameter_sets_per_account: int = 1000
    max_execution_runs_per_account: int = 5000
    max_execution_environments_per_account: int = 500
    max_runtime_adapters_per_account: int = 250
    max_reproduction_execution_plans_per_account: int = 1000
    max_runtime_handoff_receipts_per_account: int = 2000
    max_execution_policies_per_account: int = 250
    max_execution_policy_decisions_per_account: int = 5000
    max_runtime_execution_attestations_per_account: int = 5000
    max_runtime_trust_policies_per_account: int = 250
    max_compliance_waivers_per_account: int = 1000
    max_attestation_verifications_per_account: int = 5000
    runtime_attestation_token: str = ""
    # SC-MODEL-01 Research export: disabled unless explicitly configured.
    research_export_enabled: bool = False
    research_export_client_token: str = ""
    research_export_signing_key_file: str = ""
    research_export_grant_ttl_seconds: int = 900
    # SC-RIGHTS-02 rights delivery to Research: off unless a Research URL and delivery token file are set.
    research_rights_delivery_url: str = ""  # Research API base, e.g. http://research-api:8000/api/research/v1
    research_rights_delivery_token_file: str = ""
    research_rights_ops_token_file: str = ""  # Operator credential for the private delivery dashboard.
    research_rights_max_attempts: int = 12
    research_rights_backoff_base_seconds: float = 2.0
    research_rights_backoff_cap_seconds: float = 300.0
    research_rights_lease_seconds: float = 60.0
    research_rights_http_timeout_seconds: float = 10.0
    research_rights_attest_interval_seconds: float = 300.0
    research_rights_alert_restriction_seconds: float = 300.0  # A restriction unapplied for longer raises an alert.
    research_rights_batch: int = 20

    compute_max_rows: int = 50000
    compute_max_columns: int = 256
    compute_max_matrix_dimension: int = 512
    compute_max_symbolic_chars: int = 4000
    compute_max_symbolic_operations: int = 2000
    compute_max_optimizer_iterations: int = 1000
    compute_max_polynomial_degree: int = 256
    compute_max_result_bytes: int = 10 * 1024 * 1024

    runtime_r_url: str = ""
    runtime_r_token: str = ""
    runtime_julia_url: str = ""
    runtime_julia_token: str = ""
    runtime_ml_url: str = ""
    runtime_ml_token: str = ""
    runtime_neural_url: str = ""
    runtime_neural_token: str = ""
    runtime_interchange_url: str = ""
    runtime_interchange_token: str = ""
    runtime_forecast_url: str = ""
    runtime_forecast_token: str = ""
    runtime_probability_url: str = ""
    runtime_probability_token: str = ""
    runtime_uncertainty_url: str = ""
    runtime_uncertainty_token: str = ""
    runtime_optimization_url: str = ""
    runtime_optimization_token: str = ""
    runtime_decision_url: str = ""
    runtime_decision_token: str = ""
    runtime_reliability_url: str = ""
    runtime_reliability_token: str = ""
    runtime_wasm_url: str = ""
    runtime_wasm_token: str = ""
    # SC-SIM-01 G7/G8: governed adapters into existing Workbench and Decision Studio calculations.
    runtime_workbench_url: str = ""
    runtime_workbench_token: str = ""
    runtime_decision_studio_url: str = ""
    runtime_decision_studio_token: str = ""
    polyglot_timeout_seconds: float = 45.0
    polyglot_max_exchange_rows: int = 50000
    polyglot_max_exchange_columns: int = 256
    polyglot_max_payload_bytes: int = 10 * 1024 * 1024
    max_statistical_model_receipts_per_account: int = 5000
    max_numerical_simulation_receipts_per_account: int = 5000
    max_predictive_model_receipts_per_account: int = 5000
    max_model_evaluation_receipts_per_account: int = 10000
    max_interchange_receipts_per_account: int = 10000
    max_cross_runtime_verification_receipts_per_account: int = 10000
    max_forecast_receipts_per_account: int = 10000
    max_forecast_evaluation_receipts_per_account: int = 10000
    max_probabilistic_inference_receipts_per_account: int = 10000
    max_uncertainty_analysis_receipts_per_account: int = 10000
    max_optimization_receipts_per_account: int = 10000
    max_decision_optimization_receipts_per_account: int = 10000
    max_reliability_analysis_receipts_per_account: int = 10000
    max_scientific_study_packages_per_account: int = 250
    max_scientific_study_package_bytes: int = 25 * 1024 * 1024
    max_visualization_specs_per_account: int = 1000
    interchange_timeout_seconds: float = 60.0
    interchange_max_result_bytes: int = 25 * 1024 * 1024

    max_jobs_per_account: int = 1000
    default_job_max_attempts: int = 3
    worker_poll_seconds: float = 2.0
    worker_heartbeat_seconds: float = 10.0
    orchestration_timeout_seconds: float = 60.0

    route_core_url: str = ""
    route_core_token: str = ""
    route_lab_url: str = ""
    route_lab_token: str = ""
    route_workbench_url: str = ""
    route_workbench_token: str = ""
    route_decision_studio_url: str = ""
    route_decision_studio_token: str = ""
    route_library_url: str = ""
    route_library_token: str = ""
    route_site_intelligence_url: str = ""
    route_site_intelligence_token: str = ""

    # v3.1 Platform Core v3 unified research runtime integration.
    platform_core_url: str = ""
    platform_core_write_api_key: str = ""
    platform_core_timeout_seconds: float = 15.0

    @property
    def platform_core_configured(self) -> bool:
        return bool(self.platform_core_url.strip())

    @property
    def platform_core_write_configured(self) -> bool:
        return bool(self.platform_core_url.strip() and self.platform_core_write_api_key.strip())

    request_id_header: str = "X-Request-ID"
    user_id_header: str = "X-SC-User-ID"

    @property
    def token_configured(self) -> bool:
        return bool(self.service_token.strip())

    @property
    def runtime_attestation_token_configured(self) -> bool:
        return bool(self.runtime_attestation_token.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


def browser_origins(settings: "Settings | None" = None) -> set[str]:
    """Exact origins allowed to call Workspace from a browser with the session cookie."""
    settings = settings or get_settings()
    return {o.strip().rstrip("/") for o in (settings.cors_allowed_origins + "," + getattr(settings, "research_console_origins", "")).split(",") if o.strip()}
