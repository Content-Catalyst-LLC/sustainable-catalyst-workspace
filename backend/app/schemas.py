from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectStoreRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    schema_: Literal["sc-workspace-cloud-backup/1.0", "sc-workspace-sync-push/1.0"] = Field(alias="schema")
    sourceProjectId: str = Field(min_length=1, max_length=160)
    projectTitle: str | None = None
    clientUpdatedAt: str | None = None
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)
    project: dict[str, Any]


class NotebookStoreRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    schema_: Literal["sc-workspace-notebook-cloud-backup/1.0", "sc-workspace-notebook-sync-push/1.0"] = Field(alias="schema")
    sourceNotebookId: str = Field(min_length=1, max_length=160)
    sourceProjectId: str | None = Field(default=None, max_length=160)
    notebookTitle: str | None = None
    clientUpdatedAt: str | None = None
    notebookFingerprint: str | None = None
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)
    notebook: dict[str, Any]


class LegacyMigrationRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(min_length=1, max_length=160)
    revision: int = Field(default=1, ge=1)
    storageMode: str = Field(default="manual-backup", max_length=32)
    backedUpAt: str | None = None
    fingerprint: str | None = Field(default=None, max_length=128)
    payload: dict[str, Any]


class LegacyMigrationRequest(BaseModel):
    schema_: Literal["sc-workspace-legacy-user-meta-migration/1.0"] = Field(alias="schema")
    source: Literal["wordpress-user-meta"] = "wordpress-user-meta"
    dryRun: bool = True
    projects: list[LegacyMigrationRecord] = Field(default_factory=list)
    notebooks: list[LegacyMigrationRecord] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class ArtifactStoreRequest(BaseModel):
    schema_: Literal["sc-workspace-artifact-store/1.0"] = Field(alias="schema")
    artifactId: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    filename: str = Field(default="artifact", max_length=1024)
    mediaType: str = Field(default="application/octet-stream", max_length=255)
    contentBase64: str = Field(min_length=1)
    expectedRevision: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class RecoverySnapshotRequest(BaseModel):
    schema_: Literal["sc-workspace-recovery-snapshot-request/1.0"] = Field(alias="schema")
    reason: str = Field(default="manual", max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class JobCreateRequest(BaseModel):
    schema_: Literal["sc-workspace-job-request/1.0"] = Field(alias="schema")
    jobType: Literal["workspace-task", "compute-handoff"] = "workspace-task"
    targetProduct: Literal["workspace", "core", "lab", "workbench", "decision-studio", "library", "site-intelligence"] = "workspace"
    operation: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    priority: int = Field(default=5, ge=0, le=9)
    maxAttempts: int = Field(default=3, ge=1, le=5)
    idempotencyKey: str | None = Field(default=None, max_length=160)
    inputArtifactIds: list[str] = Field(default_factory=list, max_length=100)
    executionRunId: str | None = Field(default=None, max_length=96)
    payload: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class JobActionRequest(BaseModel):
    schema_: Literal["sc-workspace-job-action/1.0"] = Field(alias="schema")
    reason: str = Field(default="user-request", max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class DatasetStoreRequest(BaseModel):
    schema_: Literal["sc-workspace-dataset-record/1.0"] = Field(alias="schema")
    datasetId: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    name: str = Field(min_length=1, max_length=1000)
    description: str = Field(default="", max_length=12000)
    datasetType: Literal["table", "timeseries", "geospatial", "document", "image", "graph", "simulation", "external", "other"] = "other"
    sourceKind: Literal["artifact", "external", "library", "generated", "metadata"] = "metadata"
    artifactId: str | None = Field(default=None, max_length=160)
    externalUri: str | None = Field(default=None, max_length=4000)
    schemaDefinition: dict[str, Any] = Field(default_factory=dict)
    lineage: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list, max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class ModelStoreRequest(BaseModel):
    schema_: Literal["sc-workspace-model-record/1.0"] = Field(alias="schema")
    modelId: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    name: str = Field(min_length=1, max_length=1000)
    description: str = Field(default="", max_length=12000)
    modelKind: Literal["statistical", "forecasting", "machine-learning", "simulation", "optimization", "causal", "symbolic", "custom"] = "custom"
    framework: str = Field(default="", max_length=160)
    algorithm: str = Field(default="", max_length=160)
    versionLabel: str = Field(default="", max_length=96)
    sourceArtifactId: str | None = Field(default=None, max_length=160)
    executionTarget: Literal["", "workspace", "core", "lab", "workbench", "decision-studio", "library", "site-intelligence"] = ""
    executionOperation: str = Field(default="", max_length=160)
    inputSchema: dict[str, Any] = Field(default_factory=dict)
    outputSchema: dict[str, Any] = Field(default_factory=dict)
    configuration: dict[str, Any] = Field(default_factory=dict)
    lineage: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list, max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class ParameterSetStoreRequest(BaseModel):
    schema_: Literal["sc-workspace-parameter-set/1.0"] = Field(alias="schema")
    parameterSetId: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    modelId: str | None = Field(default=None, max_length=160)
    name: str = Field(min_length=1, max_length=1000)
    parameters: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class RegistryRevisionRef(BaseModel):
    revision: int | None = Field(default=None, ge=1)


class DatasetRunRef(RegistryRevisionRef):
    datasetId: str = Field(min_length=1, max_length=160)


class ModelRunRef(RegistryRevisionRef):
    modelId: str = Field(min_length=1, max_length=160)


class ParameterSetRunRef(RegistryRevisionRef):
    parameterSetId: str = Field(min_length=1, max_length=160)


class ArtifactRevisionRef(BaseModel):
    artifactId: str = Field(min_length=1, max_length=160)
    revision: int | None = Field(default=None, ge=1)


class RuntimeAdapterRunRef(RegistryRevisionRef):
    adapterId: str = Field(min_length=1, max_length=160)


class ExecutionEnvironmentStoreRequest(BaseModel):
    schema_: Literal["sc-workspace-execution-environment/1.0"] = Field(alias="schema")
    environmentId: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    name: str = Field(min_length=1, max_length=1000)
    description: str = Field(default="", max_length=12000)
    runtime: dict[str, Any] = Field(default_factory=dict)
    dependencies: dict[str, Any] = Field(default_factory=dict)
    lockArtifacts: list[ArtifactRevisionRef] = Field(default_factory=list, max_length=50)
    container: dict[str, Any] = Field(default_factory=dict)
    system: dict[str, Any] = Field(default_factory=dict)
    hardware: dict[str, Any] = Field(default_factory=dict)
    randomSeeds: dict[str, Any] = Field(default_factory=dict)
    environmentVariableNames: list[str] = Field(default_factory=list, max_length=200)
    configuration: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class ExecutionEnvironmentRunRef(RegistryRevisionRef):
    environmentId: str = Field(min_length=1, max_length=160)


class ExecutionRunCreateRequest(BaseModel):
    schema_: Literal["sc-workspace-execution-run/1.0"] = Field(alias="schema")
    runId: str | None = Field(default=None, max_length=96)
    projectId: str | None = Field(default=None, max_length=160)
    name: str = Field(default="Execution run", max_length=1000)
    datasetRefs: list[DatasetRunRef] = Field(default_factory=list, max_length=100)
    modelRef: ModelRunRef | None = None
    parameterSetRef: ParameterSetRunRef | None = None
    environmentRef: ExecutionEnvironmentRunRef | None = None
    runtimeAdapterRef: RuntimeAdapterRunRef | None = None
    targetProduct: Literal["", "workspace", "core", "lab", "workbench", "decision-studio", "library", "site-intelligence"] = ""
    operation: str = Field(default="", max_length=160)
    environment: dict[str, Any] = Field(default_factory=dict)
    idempotencyKey: str | None = Field(default=None, max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class ExecutionRunUpdateRequest(BaseModel):
    schema_: Literal["sc-workspace-execution-run-update/1.0"] = Field(alias="schema")
    status: Literal["planned", "queued", "running", "succeeded", "failed", "blocked", "cancelled"]
    progress: int = Field(default=0, ge=0, le=100)
    jobId: str | None = Field(default=None, max_length=96)
    resultSummary: dict[str, Any] = Field(default_factory=dict)
    errorCode: str = Field(default="", max_length=96)
    errorMessage: str = Field(default="", max_length=4000)

    model_config = ConfigDict(populate_by_name=True)


class ExecutionRunOutputRequest(BaseModel):
    schema_: Literal["sc-workspace-execution-run-output/1.0"] = Field(alias="schema")
    outputId: str = Field(min_length=1, max_length=160)
    artifactId: str | None = Field(default=None, max_length=160)
    role: str = Field(default="result", max_length=64)
    label: str = Field(default="", max_length=1000)
    mediaType: str = Field(default="application/octet-stream", max_length=255)
    sha256: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    bytes: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class RuntimeAdapterStoreRequest(BaseModel):
    schema_: Literal["sc-workspace-runtime-adapter/1.0"] = Field(alias="schema")
    adapterId: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    name: str = Field(min_length=1, max_length=1000)
    description: str = Field(default="", max_length=12000)
    runtimeFamily: Literal["python", "r", "julia", "custom"] = "custom"
    runtimeVersion: str = Field(default="", max_length=96)
    adapterType: Literal["metadata", "container", "remote-service"] = "metadata"
    dependencyManagers: list[str] = Field(default_factory=list, max_length=20)
    container: dict[str, Any] = Field(default_factory=dict)
    platformConstraints: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[str] = Field(default_factory=list, max_length=100)
    configuration: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)

    model_config = ConfigDict(populate_by_name=True)


class RuntimeCompatibilityCheckRequest(BaseModel):
    schema_: Literal["sc-workspace-runtime-compatibility-check/1.0"] = Field(alias="schema")
    environmentRef: ExecutionEnvironmentRunRef

    model_config = ConfigDict(populate_by_name=True)


class ReproductionPlanCreateRequest(BaseModel):
    schema_: Literal["sc-workspace-reproduction-plan/1.0"] = Field(alias="schema")
    planId: str | None = Field(default=None, max_length=96)
    originalRunId: str = Field(min_length=1, max_length=96)
    runtimeAdapterRef: RuntimeAdapterRunRef | None = None
    notes: str = Field(default="", max_length=12000)

    model_config = ConfigDict(populate_by_name=True)


class ReproductionVerificationCreateRequest(BaseModel):
    schema_: Literal["sc-workspace-reproduction-verification/1.0"] = Field(alias="schema")
    verificationId: str | None = Field(default=None, max_length=96)
    originalRunId: str = Field(min_length=1, max_length=96)
    reproductionRunId: str = Field(min_length=1, max_length=96)

    model_config = ConfigDict(populate_by_name=True)
