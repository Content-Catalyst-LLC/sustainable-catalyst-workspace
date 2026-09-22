from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SC_WORKSPACE_", case_sensitive=False)

    service_name: str = "Sustainable Catalyst Workspace Backend"
    service_version: str = "3.1.0"
    environment: str = "production"
    database_url: str = "postgresql+psycopg://sc_workspace:change-me@127.0.0.1:5432/sc_workspace"
    service_token: str = ""
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
