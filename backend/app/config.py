from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SC_WORKSPACE_", case_sensitive=False)

    service_name: str = "Sustainable Catalyst Workspace Backend"
    service_version: str = "2.2.0"
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

    request_id_header: str = "X-Request-ID"
    user_id_header: str = "X-SC-User-ID"

    @property
    def token_configured(self) -> bool:
        return bool(self.service_token.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
