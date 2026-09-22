from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from .config import get_settings
from .db import initialize_schema, ping_database, session_scope
from .repository import (
    delete_notebook,
    delete_project,
    get_notebook,
    get_project,
    get_project_revision,
    list_notebooks,
    list_project_revisions,
    list_projects,
    notebook_metadata,
    project_metadata,
    store_notebook,
    store_project,
)
from .schemas import (
    ArtifactStoreRequest, DatasetStoreRequest, ExecutionEnvironmentStoreRequest, ExecutionRunCreateRequest, ExecutionRunOutputRequest,
    RuntimeAdapterStoreRequest, RuntimeCompatibilityCheckRequest, ReproductionPlanCreateRequest, ReproductionVerificationCreateRequest, CrossRuntimeVerificationCreateRequest,
    ReproductionExecutionPlanCreateRequest, ControlledRuntimeHandoffRequest, ExecutionPolicyStoreRequest, RuntimeExecutionAttestationRequest,
    RuntimeTrustPolicyStoreRequest, ComplianceWaiverCreateRequest, AttestationVerificationCreateRequest,
    ExecutionRunUpdateRequest, JobActionRequest, JobCreateRequest, LegacyMigrationRequest, ModelStoreRequest,
    NotebookStoreRequest, ParameterSetStoreRequest, ProjectStoreRequest, RecoverySnapshotRequest, DomainValidationRequest, CommandExecuteRequest, QueryExecuteRequest,
    NotebookExecutionPlanRequest, NotebookExecutionDispatchRequest, NotebookExecutionCancelRequest,
    ScientificStudyPackageCreateRequest, ScientificStudyPackageVerifyRequest, VisualizationSpecStoreRequest,
    LocalFirstSyncEnvelope, LocalFirstSyncReconcileRequest,
)
from .domain_authority import DomainValidationError, authority_profile, get_mutation_receipt, list_mutation_receipts, mutation_receipt_metadata, validate_domain_document
from .command_query import profile as command_query_profile, execute_command, execute_query, list_command_receipts, workspace_overview, project_read_model, notebook_read_model
from .notebook_orchestration import (profile as notebook_orchestration_profile, create_plan as create_notebook_execution_plan,
    get_plan as get_notebook_execution_plan, list_plans as list_notebook_execution_plans, plan_metadata as notebook_execution_plan_metadata,
    dispatch_plan as dispatch_notebook_execution_plan, cancel_plan as cancel_notebook_execution_plan, list_receipts as list_notebook_orchestration_receipts)
from .study_packages import (profile as study_package_profile, create_package as create_scientific_study_package, get_package as get_scientific_study_package,
    list_packages as list_scientific_study_packages, package_metadata as scientific_study_package_metadata, verify_package as verify_scientific_study_package,
    list_receipts as list_scientific_study_package_receipts, delete_package as delete_scientific_study_package)
from .client_contracts import profile as typed_client_contract_profile
from .frontend_runtime import profile as frontend_runtime_profile
from .production_certification import profile as production_architecture_certification_profile
from .backend_native_workspace import profile as backend_native_workspace_profile, bootstrap as backend_native_workspace_bootstrap
from .thin_client_state import profile as thin_client_state_profile, bootstrap as thin_client_state_bootstrap
from .local_first_sync import profile as local_first_sync_profile, bootstrap as local_first_sync_bootstrap, apply_envelope as apply_local_first_sync_envelope, reconcile as reconcile_local_first_sync, list_receipts as list_local_first_sync_receipts
from .scientific_objects import (profile as scientific_object_profile, list_objects as list_scientific_objects, get_object as get_scientific_object, history as scientific_object_history, relations as scientific_object_relations, OBJECT_KINDS as SCIENTIFIC_OBJECT_KINDS)
from .cross_product_handoffs import (profile as handoff_profile, create_handoff, get_handoff, accept_handoff, list_receipts as list_handoff_fabric_receipts, ResearchHandoffRequest, ResearchHandoffAcceptRequest)
from .authorization import (profile as authorization_profile, principal_payload as authorization_principal_payload, evaluate_and_record as evaluate_authorization_and_record, list_decisions as list_authorization_decisions, AuthorizationEvaluateRequest)
from .visualization_specs import (profile as visualization_spec_profile, store_spec as store_visualization_spec, get_spec as get_visualization_spec,
    list_specs as list_visualization_specs, list_revisions as list_visualization_spec_revisions, list_receipts as list_visualization_spec_receipts,
    delete_spec as delete_visualization_spec, metadata as visualization_spec_metadata)
from .security import ServiceIdentity, require_service_identity, require_runtime_attestation_identity
from .migration import apply_migration, list_receipts, migration_plan
from .object_store import artifact_metadata, delete_artifact, get_artifact, list_artifacts, read_artifact_content, store_artifact, verify_artifact_storage
from .recovery import create_snapshot, get_snapshot, list_snapshots, snapshot_metadata
from .jobs import create_job, get_job, job_metadata, list_job_events, list_jobs, list_worker_heartbeats, request_cancel, retry_job
from .routing import configured_route_count, route_registry
from .registry import (
    create_execution_run, dataset_metadata, get_dataset, get_dataset_revision, get_execution_run, get_model,
    get_model_revision, get_parameter_set, get_parameter_set_revision, list_dataset_revisions, list_datasets,
    list_execution_runs, list_model_revisions, list_models, list_parameter_set_revisions, list_parameter_sets,
    list_run_events, list_run_outputs, model_metadata, output_metadata, parameter_set_metadata, run_metadata,
    store_dataset, store_model, store_parameter_set, store_run_output, update_execution_run,
)
from .utils import iso
from .environments import environment_metadata, get_environment, get_environment_revision, list_environment_revisions, list_environments, store_environment
from .runtime_adapters import adapter_metadata, check_environment_compatibility, get_adapter, get_adapter_revision, list_adapter_revisions, list_adapters, store_adapter
from .reproduction import create_reproduction_plan, create_verification, get_reproduction_plan, get_verification, list_reproduction_plans, list_verifications, plan_metadata, verification_metadata
from .execution_control import create_execution_plan, dispatch_execution_plan, execution_plan_metadata, get_execution_plan, get_handoff_receipt, handoff_receipt_metadata, list_execution_plans, list_handoff_receipts
from .policy import get_policy, get_policy_revision, get_policy_decision, list_policies, list_policy_revisions, list_policy_decisions, policy_decision_metadata, policy_metadata, store_policy
from .telemetry import attestation_metadata, create_runtime_attestation, get_runtime_attestation, list_runtime_attestations
from .compute import compute_catalog, get_compute_receipt, list_compute_receipts, receipt_metadata as compute_receipt_metadata
from .polyglot import (runtime_catalog as polyglot_runtime_catalog, operation_catalog as polyglot_operation_catalog,
    list_receipts as list_polyglot_receipts, get_receipt as get_polyglot_receipt, receipt_metadata as polyglot_receipt_metadata,
    runtime_health as polyglot_runtime_health, list_statistical_receipts, get_statistical_receipt, statistical_receipt_metadata,
    list_numerical_receipts, get_numerical_receipt, numerical_receipt_metadata,
    list_predictive_model_receipts, get_predictive_model_receipt, predictive_model_receipt_metadata,
    list_model_evaluation_receipts, get_model_evaluation_receipt, model_evaluation_receipt_metadata,
    list_forecast_receipts, get_forecast_receipt, forecast_receipt_metadata,
    list_forecast_evaluation_receipts, get_forecast_evaluation_receipt, forecast_evaluation_receipt_metadata, list_probabilistic_inference_receipts, get_probabilistic_inference_receipt, probabilistic_inference_receipt_metadata,
    list_uncertainty_analysis_receipts, get_uncertainty_analysis_receipt, uncertainty_analysis_receipt_metadata,
    list_optimization_receipts, get_optimization_receipt, optimization_receipt_metadata,
    list_decision_optimization_receipts, get_decision_optimization_receipt, decision_optimization_receipt_metadata,
    list_reliability_analysis_receipts, get_reliability_analysis_receipt, reliability_analysis_receipt_metadata)
from .interchange import operation_catalog as interchange_operation_catalog, runtime_health as interchange_runtime_health, list_receipts as list_interchange_receipts, get_receipt as get_interchange_receipt, receipt_metadata as interchange_receipt_metadata
from .cross_runtime_verification import create_cross_runtime_verification, get_receipt as get_cross_runtime_verification_receipt, list_receipts as list_cross_runtime_verification_receipts, receipt_metadata as cross_runtime_verification_receipt_metadata, profile_catalog as cross_runtime_verification_profiles
from .compliance import (trust_policy_metadata, store_trust_policy, get_trust_policy, list_trust_policies, list_trust_policy_revisions,
    waiver_metadata, create_waiver, get_waiver, list_waivers, verification_metadata as compliance_verification_metadata,
    create_verification as create_compliance_verification, get_verification as get_compliance_verification, list_verifications as list_compliance_verifications)
from .platform_core_runtime import (
    profile as platform_core_runtime_profile, readiness as platform_core_runtime_readiness,
    ensure_session as ensure_platform_core_session, project_context as platform_core_project_context,
    bind_object as bind_platform_core_object, bind_execution as bind_platform_core_execution,
    bind_visual as bind_platform_core_visual, bind_package as bind_platform_core_package,
    bind_handoff as bind_platform_core_handoff, session_view as platform_core_session_view,
    list_receipts as list_platform_core_runtime_receipts, PlatformCoreRuntimeError,
    PlatformCoreSessionRequest, PlatformCoreObjectBindingRequest, PlatformCoreExecutionBindingRequest,
    PlatformCoreVisualBindingRequest, PlatformCorePackageBindingRequest, PlatformCoreHandoffBindingRequest,
    CORE_CONTRACT as PLATFORM_CORE_V3_CONTRACT, INTEGRATION_SCHEMA as PLATFORM_CORE_INTEGRATION_SCHEMA,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.auto_create_schema:
        initialize_schema()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get(settings.request_id_header) or str(uuid4())
    response = await call_next(request)
    response.headers[settings.request_id_header] = request_id
    return response


@app.exception_handler(HTTPException)
async def workspace_http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        body = {"ok": False, **detail}
    else:
        body = {"ok": False, "message": str(detail)}
    return JSONResponse(status_code=exc.status_code, content=body, headers=exc.headers)


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": settings.service_name,
        "version": settings.service_version,
        "persistence": "postgresql",
        "projectSchema": "sc-workspace-project/20.0",
        "notebookSchema": "sc-workspace-notebook/3.0",
        "localFirst": True,
        "objectStorage": "content-addressed-filesystem",
        "recoverySnapshots": True,
        "legacyMigration": True,
        "backgroundJobs": True,
        "computeOrchestration": True,
        "workerMode": "separate-process",
        "datasetRegistry": True,
        "modelRegistry": True,
        "executionRunRegistry": True,
        "reproducibilityLineage": True,
        "executionEnvironmentRegistry": True,
        "dependencyManifests": True,
        "dependencyLockArtifacts": True,
        "containerIdentityCapture": True,
        "runtimeVersionCapture": True,
        "randomSeedCapture": True,
        "runtimeAdapterRegistry": True,
        "runtimeCompatibilityChecks": True,
        "reproductionPlans": True,
        "reproductionVerification": True,
        "reproductionExecutionPlans": True,
        "controlledRuntimeHandoffs": True,
        "humanAuthorizedDispatch": True,
        "executionPolicyRegistry": True,
        "resourceBudgets": True,
        "runtimeSandboxing": True,
        "policyRequiredForControlledHandoffs": True,
        "adapterTrustLevels": True,
        "runtimeEnforcementTelemetry": True,
        "budgetAccounting": True,
        "executionAttestations": True,
        "dedicatedRuntimeAttestationCredential": True,
        "runtimeTrustPolicyRegistry": True,
        "attestationVerification": True,
        "downstreamComplianceGates": True,
        "humanComplianceWaivers": True,
        "pythonScientificComputeRuntime": True,
        "scientificComputeOperationRegistry": True,
        "computeResultArtifacts": True,
        "computeExecutionReceipts": True,
        "computeProgressEvents": True,
        "boundedScientificOperationsOnly": True,
        "polyglotScientificRuntimeFabric": True,
        "polyglotLanguages": ["python", "r", "julia", "ml", "forecast", "probability", "uncertainty", "optimization", "decision", "reliability", "sql", "wasm"],
        "arrowCompatibleInterchange": True,
        "polyglotExecutionReceipts": True,
        "rStatisticalEconometricRuntime": True,
        "rRuntimeConfigured": bool(settings.runtime_r_url.strip()),
        "rRuntimeBoundedOperations": 8,
        "statisticalModelReceipts": True,
        "juliaSimulationNumericalRuntime": True,
        "juliaRuntimeConfigured": bool(settings.runtime_julia_url.strip()),
        "juliaRuntimeBoundedOperations": 8,
        "numericalSimulationReceipts": True,
        "predictiveAnalyticsMachineLearningRuntime": True,
        "mlRuntimeConfigured": bool(settings.runtime_ml_url.strip()),
        "mlRuntimeBoundedOperations": 8,
        "predictiveModelReceipts": True,
        "modelEvaluationReceipts": True,
        "nativeArrowParquetInterchange": True,
        "interchangeRuntimeConfigured": bool(settings.runtime_interchange_url.strip()),
        "interchangeRuntimeBoundedOperations": 8,
        "interchangeReceipts": True,
        "interchangeFormats": ["arrow-ipc-stream", "parquet"],
        "crossRuntimeReproductionVerification": True,
        "toleranceAwareNumericComparison": True,
        "crossRuntimeVerificationReceipts": True,
        "forecastingTimeSeriesRuntime": True,
        "forecastRuntimeConfigured": bool(settings.runtime_forecast_url.strip()),
        "forecastRuntimeBoundedOperations": 8,
        "forecastReceipts": True,
        "forecastEvaluationReceipts": True,
        "forecastPredictionIntervals": True,
        "probabilisticBayesianRuntime": True,
        "probabilityRuntimeConfigured": bool(settings.runtime_probability_url.strip()),
        "probabilityRuntimeBoundedOperations": 6,
        "probabilisticInferenceReceipts": True,
        "credibleIntervals": True,
        "posteriorPredictiveChecks": True,
        "uncertaintyPropagation": True,
        "monteCarloUncertaintyQuantificationRuntime": True,
        "uncertaintyRuntimeConfigured": bool(settings.runtime_uncertainty_url.strip()),
        "uncertaintyRuntimeBoundedOperations": 8,
        "uncertaintyAnalysisReceipts": True,
        "seededMonteCarloSimulation": True,
        "bootstrapIntervals": True,
        "latinHypercubeSampling": True,
        "rankCorrelationSensitivity": True,
        "optimizationParameterSearchRuntime": True,
        "optimizationRuntimeConfigured": bool(settings.runtime_optimization_url.strip()),
        "optimizationRuntimeBoundedOperations": 8,
        "optimizationReceipts": True,
        "boxConstrainedOptimization": True,
        "gridAndRandomSearch": True,
        "multiObjectiveWeightedSearch": True,
        "robustScenarioRanking": True,
        "robustDecisionOptimizationRuntime": True,
        "decisionRuntimeConfigured": bool(settings.runtime_decision_url.strip()),
        "decisionRuntimeBoundedOperations": 8,
        "decisionOptimizationReceipts": True,
        "paretoFrontAnalysis": True,
        "minimaxRegretAnalysis": True,
        "constraintRobustnessAnalysis": True,
        "valueOfInformationAnalysis": True,
        "reliabilitySurvivalFailureTimeRuntime": True,
        "reliabilityRuntimeConfigured": bool(settings.runtime_reliability_url.strip()),
        "reliabilityRuntimeBoundedOperations": 8,
        "reliabilityAnalysisReceipts": True,
        "kaplanMeierSurvival": True,
        "weibullLifeModeling": True,
        "systemReliabilityAnalysis": True,
        "repairableAvailabilityAnalysis": True,
        "backendDomainAuthority": True,
        "backendAuthoritativeState": True,
        "browserAuthoritativeState": False,
        "serverSideDomainValidation": True,
        "serverSideRevisionAuthority": True,
        "domainMutationReceipts": True,
        "canonicalDomainStore": "postgresql",
        "domainAuthoritySchema": "sc-workspace-domain-authority/1.0",
        "workspaceCommandQueryApi": True,
        "serverSideCommandDispatch": True,
        "serverGeneratedReadModels": True,
        "commandReceipts": True,
        "queriesAreReadOnly": True,
        "commandQuerySchema": "sc-workspace-command-query/1.0",
        "rollingOriginBacktesting": True,
        "serverSideNotebookArtifactOrchestration": True,
        "notebookExecutionPlans": True,
        "artifactDependencyPinning": True,
        "dependencyAwareNotebookDispatch": True,
        "reproducibleScientificStudyPackages": True,
        "deterministicStudyManifests": True,
        "studyPackageArtifactSnapshots": True,
        "studyPackageIntegrityVerification": True,
        "scientificStudyPackageSchema": "sc-workspace-scientific-study-package/1.0",
        "declarativeVisualizationSpecificationApi": True,
        "rendererNeutralVisualizationSpecs": True,
        "visualizationSpecRevisionHistory": True,
        "visualizationSpecReceipts": True,
        "linkedVisualizationViews": True,
        "visualizationSourceProvenancePinning": True,
        "visualizationSpecSchema": "sc-workspace-visualization-spec/1.0",
        "browserDefinesAnalyticalMeaning": False,
        "typedClientContracts": True,
        "generatedTypeScriptClient": True,
        "typedClientTransport": "wordpress-server-proxy",
        "browserDirectBackendAccess": False,
        "typedClientContractSchema": "sc-workspace-typed-client-contract/1.0",
        "thinClientStateArchitecture": True,
        "thinClientStateSchema": "sc-workspace-thin-client-state/1.0",
        "canonicalClientCachePersistent": False,
        "persistentBrowserState": "transient-only",
        "canonicalMutationsViaCommandsOnly": True,
        "localFirstSynchronizationProtocol": True,
        "localFirstSyncSchema": "sc-workspace-local-first-sync/1.0",
        "offlineOutboxAuthoritative": False,
        "syncBaseRevisionRequired": True,
        "syncConflictDetection": True,
        "syncAutomaticSemanticMerge": False,
        "syncRevisionVectorReconciliation": True,
        "durableSyncReceipts": True,
        "crossProductResearchHandoffFabric": True,
        "crossProductHandoffSchema": "sc-workspace-cross-product-research-handoff-fabric/1.0",
        "handoffRevisionPinning": True,
        "handoffFingerprintPinning": True,
        "handoffDurableReceipts": True,
        "handoffGenericDestinationMutation": False,
        "unifiedScientificObjectApi": True,
        "scientificObjectSchema": "sc-workspace-scientific-object/1.0",
        "scientificObjectKindCount": len(SCIENTIFIC_OBJECT_KINDS),
        "scientificObjectRelations": True,
        "scientificObjectRevisionHistory": True,
        "scientificObjectGenericMutation": False,
        "backendPolicyIdentityAuthorizationConsolidation": True,
        "backendAuthorizationSchema": "sc-workspace-backend-authorization/1.0",
        "serverResolvedPrincipalIdentity": True,
        "routePolicyEnforcement": True,
        "authorizationDefaultEffect": "deny",
        "authorizationDecisionReceipts": True,
        "clientSuppliedRolesTrusted": False,
        "clientSuppliedScopesTrusted": False,
        "frontendLogicReductionLegacyJsRetirement": True,
        "frontendRuntimeSchema": "sc-workspace-frontend-runtime-policy/1.0",
        "frontendPrimaryShellThin": True,
        "legacyLocalCompatibilityLazy": True,
        "historicalVersionedFrontendAssetsRetired": True,
        "packageAssetNamesVersionDerived": True,
        "productionArchitectureCertification": True,
        "productionArchitectureCertificationSchema": "sc-workspace-production-architecture-certification/1.0",
        "architectureCertificationAutomated": True,
        "liveProductionCertificationAutomatic": False,
        "releaseMigrationLineage": "031_backend_policy_identity_authorization_consolidation.sql",
        "rollbackBaseline": "2.36.0",
        "backendNativeScientificWorkspace": True,
        "backendNativeScientificWorkspaceSchema": "sc-workspace-backend-native-scientific-workspace/1.0",
        "platformCoreV3UnifiedResearchRuntimeIntegration": True,
        "platformCoreRuntimeConfigured": settings.platform_core_configured,
        "platformCoreRuntimeWriteConfigured": settings.platform_core_write_configured,
        "platformCoreRuntimeContract": PLATFORM_CORE_V3_CONTRACT,
        "platformCoreReferenceFirst": True,
        "platformCoreObjectContentReplication": False,
        "platformCoreIntegrationSchema": PLATFORM_CORE_INTEGRATION_SCHEMA,
        "signedInLocalCanonicalFallback": False,
        "backendNativeBootstrap": True,
        "automaticReproductionExecution": False,
        "clientSuppliedRuntimeUrlsAllowed": False,
        "arbitraryCodeExecution": False,
    }


@app.get("/ready")
def ready():
    try:
        ping_database()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc.__class__.__name__}")
    if not settings.token_configured:
        raise HTTPException(status_code=503, detail="Service token is not configured.")
    if not settings.runtime_attestation_token_configured:
        raise HTTPException(status_code=503, detail="Runtime-attestation token is not configured.")
    return {"ok": True, "database": "ready", "serviceAuth": "ready", "runtimeAttestationAuth": "ready", "authorizationPolicy": "ready", "identityResolution": "ready", "productionArchitectureCertification": "ready", "backendNativeScientificWorkspace": "ready", "platformCoreRuntime": "configured" if settings.platform_core_configured else "optional-unconfigured"}


@app.get("/v1/capabilities")
def capabilities(identity: ServiceIdentity = Depends(require_service_identity)):
    return {
        "schema": "sc-workspace-backend-capabilities/1.0",
        "version": settings.service_version,
        "userScoped": True,
        "browserDirectAccess": False,
        "wordpressProxyRequired": True,
        "projectPersistence": True,
        "notebookPersistence": True,
        "backendDomainAuthority": True,
        "backendAuthoritativeState": True,
        "browserAuthoritativeState": False,
        "clientRole": "presentation-interaction-local-drafts",
        "canonicalDomainStore": "postgresql",
        "serverSideDomainValidation": True,
        "serverSideRevisionAuthority": True,
        "serverSideMutationPolicy": True,
        "domainMutationReceipts": True,
        "domainAuthoritySchema": "sc-workspace-domain-authority/1.0",
        "workspaceCommandQueryApi": True,
        "serverSideCommandDispatch": True,
        "serverGeneratedReadModels": True,
        "commandReceipts": True,
        "queriesAreReadOnly": True,
        "commandQuerySchema": "sc-workspace-command-query/1.0",
        "reproducibleScientificStudyPackages": True,
        "deterministicStudyManifests": True,
        "studyPackageArtifactSnapshots": True,
        "studyPackageIntegrityVerification": True,
        "studyPackageFormat": "zip+canonical-json",
        "declarativeVisualizationSpecificationApi": True,
        "rendererNeutralVisualizationSpecs": True,
        "visualizationSpecRevisionHistory": True,
        "visualizationSpecReceipts": True,
        "linkedVisualizationViews": True,
        "visualizationSourceProvenancePinning": True,
        "visualizationSpecSchema": "sc-workspace-visualization-spec/1.0",
        "rendererContract": "sc-workspace-renderer-contract/1.0",
        "browserDefinesAnalyticalMeaning": False,
        "typedClientContracts": True,
        "generatedTypeScriptClient": True,
        "typedClientTransport": "wordpress-server-proxy",
        "browserDirectBackendAccess": False,
        "typedClientContractSchema": "sc-workspace-typed-client-contract/1.0",
        "thinClientStateArchitecture": True,
        "thinClientStateSchema": "sc-workspace-thin-client-state/1.0",
        "canonicalClientCachePersistent": False,
        "persistentBrowserState": "transient-only",
        "canonicalMutationsViaCommandsOnly": True,
        "localFirstSynchronizationProtocol": True,
        "localFirstSyncSchema": "sc-workspace-local-first-sync/1.0",
        "offlineOutboxAuthoritative": False,
        "syncBaseRevisionRequired": True,
        "syncConflictDetection": True,
        "syncAutomaticSemanticMerge": False,
        "syncRevisionVectorReconciliation": True,
        "durableSyncReceipts": True,
        "unifiedScientificObjectApi": True,
        "scientificObjectKindCount": len(SCIENTIFIC_OBJECT_KINDS),
        "scientificObjectGenericMutation": False,
        "backendPolicyIdentityAuthorizationConsolidation": True,
        "backendAuthorizationSchema": "sc-workspace-backend-authorization/1.0",
        "serverResolvedPrincipalIdentity": True,
        "routePolicyEnforcement": True,
        "authorizationDefaultEffect": "deny",
        "authorizationDecisionReceipts": True,
        "clientSuppliedRolesTrusted": False,
        "clientSuppliedScopesTrusted": False,
        "frontendLogicReductionLegacyJsRetirement": True,
        "frontendRuntimeSchema": "sc-workspace-frontend-runtime-policy/1.0",
        "frontendPrimaryShellThin": True,
        "legacyLocalCompatibilityLazy": True,
        "historicalVersionedFrontendAssetsRetired": True,
        "packageAssetNamesVersionDerived": True,
        "backendNativeScientificWorkspace": True,
        "backendNativeScientificWorkspaceSchema": "sc-workspace-backend-native-scientific-workspace/1.0",
        "signedInLocalCanonicalFallback": False,
        "backendNativeBootstrap": True,
        "crossProductResearchHandoffFabric": True,
        "crossProductHandoffSchema": "sc-workspace-cross-product-research-handoff-fabric/1.0",
        "handoffRevisionPinning": True,
        "handoffFingerprintPinning": True,
        "handoffDurableReceipts": True,
        "handoffGenericDestinationMutation": False,
        "projectRevisionHistory": True,
        "notebookRevisionHistory": True,
        "revisionPreconditions": True,
        "idempotentOperations": True,
        "integrityAlgorithm": "SHA-256",
        "database": "PostgreSQL",
        "objectStorage": True,
        "objectStorageMode": "content-addressed-filesystem",
        "legacyUserMetaMigration": True,
        "migrationReceipts": True,
        "recoverySnapshots": True,
        "storageIntegrityChecks": True,
        "backgroundJobs": True,
        "durableJobQueue": True,
        "workerProcess": True,
        "jobEventHistory": True,
        "jobRetryAndCancel": True,
        "computeOrchestration": True,
        "orchestrationContract": "sc-workspace-compute-handoff/1.0",
        "serverConfiguredRoutesOnly": True,
        "configuredRouteCount": configured_route_count(),
        "datasetRegistry": True,
        "datasetRevisionHistory": True,
        "modelRegistry": True,
        "modelRevisionHistory": True,
        "parameterSetRegistry": True,
        "executionRunRegistry": True,
        "executionRunEvents": True,
        "executionRunOutputs": True,
        "jobExecutionRunLinkage": True,
        "reproducibilityFingerprints": True,
        "executionEnvironmentRegistry": True,
        "executionEnvironmentRevisionHistory": True,
        "dependencyManifests": True,
        "dependencyLockArtifacts": True,
        "containerIdentityCapture": True,
        "runtimeVersionCapture": True,
        "randomSeedCapture": True,
        "runtimeAdapterRegistry": True,
        "runtimeAdapterRevisionHistory": True,
        "runtimeCompatibilityChecks": True,
        "reproductionPlans": True,
        "reproductionVerification": True,
        "deterministicRerunComparison": True,
        "comparisonMode": "metadata-and-content-digests",
        "reproductionExecutionPlans": True,
        "controlledRuntimeHandoffs": True,
        "humanAuthorizedDispatch": True,
        "frozenExecutionEnvelope": True,
        "executionPolicyRegistry": True,
        "executionPolicyRevisionHistory": True,
        "executionPolicyDecisions": True,
        "resourceBudgets": True,
        "runtimeSandboxing": True,
        "sandboxEnforcementMode": "pre-dispatch-policy-gate",
        "policyRequiredForControlledHandoffs": True,
        "adapterTrustLevels": True,
        "runtimeEnforcementTelemetry": True,
        "budgetAccounting": True,
        "executionAttestations": True,
        "dedicatedRuntimeAttestationCredential": True,
        "runtimeTrustPolicyRegistry": True,
        "attestationVerification": True,
        "downstreamComplianceGates": True,
        "humanComplianceWaivers": True,
        "pythonScientificComputeRuntime": True,
        "scientificComputeOperationRegistry": True,
        "scientificComputeEngines": ["numpy", "pandas", "scipy", "sympy"],
        "computeResultArtifacts": True,
        "computeExecutionReceipts": True,
        "computeProgressEvents": True,
        "computeCancellationChecks": True,
        "polyglotScientificRuntimeFabric": True,
        "polyglotLanguages": ["python", "r", "julia", "ml", "forecast", "probability", "uncertainty", "optimization", "decision", "reliability", "sql", "wasm"],
        "arrowCompatibleInterchange": True,
        "polyglotExecutionReceipts": True,
        "polyglotRuntimeCatalog": True,
        "monteCarloUncertaintyQuantificationRuntime": True,
        "uncertaintyRuntimeConfigured": bool(settings.runtime_uncertainty_url.strip()),
        "uncertaintyRuntimeBoundedOperations": 8,
        "uncertaintyAnalysisReceipts": True,
        "seededMonteCarloSimulation": True,
        "bootstrapIntervals": True,
        "latinHypercubeSampling": True,
        "rankCorrelationSensitivity": True,
        "optimizationParameterSearchRuntime": True,
        "optimizationRuntimeConfigured": bool(settings.runtime_optimization_url.strip()),
        "optimizationRuntimeBoundedOperations": 8,
        "optimizationReceipts": True,
        "boxConstrainedOptimization": True,
        "gridAndRandomSearch": True,
        "multiObjectiveWeightedSearch": True,
        "robustScenarioRanking": True,
        "rStatisticalEconometricRuntime": True,
        "rRuntimeConfigured": bool(settings.runtime_r_url.strip()),
        "rRuntimeBoundedOperations": 8,
        "statisticalModelReceipts": True,
        "juliaSimulationNumericalRuntime": True,
        "juliaRuntimeConfigured": bool(settings.runtime_julia_url.strip()),
        "juliaRuntimeBoundedOperations": 8,
        "numericalSimulationReceipts": True,
        "predictiveAnalyticsMachineLearningRuntime": True,
        "mlRuntimeConfigured": bool(settings.runtime_ml_url.strip()),
        "mlRuntimeBoundedOperations": 8,
        "predictiveModelReceipts": True,
        "modelEvaluationReceipts": True,
        "nativeArrowParquetInterchange": True,
        "interchangeRuntimeConfigured": bool(settings.runtime_interchange_url.strip()),
        "interchangeRuntimeBoundedOperations": 8,
        "interchangeReceipts": True,
        "interchangeFormats": ["arrow-ipc-stream", "parquet"],
        "crossRuntimeReproductionVerification": True,
        "toleranceAwareNumericComparison": True,
        "crossRuntimeVerificationReceipts": True,
        "boundedScientificOperationsOnly": True,
        "runtimeAttestationAuth": "dedicated-server-token",
        "browserAttestationSubmissionAllowed": False,
        "hostFilesystemAccessAllowed": False,
        "dockerSocketAccessAllowed": False,
        "privilegedExecutionAllowed": False,
        "automaticReproductionExecution": False,
        "clientSuppliedRuntimeUrlsAllowed": False,
        "clientSuppliedRuntimeCredentialsAllowed": False,
        "arbitraryCodeExecution": False,
        "secretEnvironmentValuesCaptured": False,
        "limits": {
            "computeRows": settings.compute_max_rows,
            "computeColumns": settings.compute_max_columns,
            "computeMatrixDimension": settings.compute_max_matrix_dimension,
            "computeSymbolicExpressionChars": settings.compute_max_symbolic_chars,
            "computeResultBytes": settings.compute_max_result_bytes,
            "polyglotExchangeRows": settings.polyglot_max_exchange_rows,
            "polyglotExchangeColumns": settings.polyglot_max_exchange_columns,
            "polyglotPayloadBytes": settings.polyglot_max_payload_bytes,
            "statisticalModelReceipts": settings.max_statistical_model_receipts_per_account,
            "numericalSimulationReceipts": settings.max_numerical_simulation_receipts_per_account,
            "predictiveModelReceipts": settings.max_predictive_model_receipts_per_account,
            "modelEvaluationReceipts": settings.max_model_evaluation_receipts_per_account,
            "interchangeReceipts": settings.max_interchange_receipts_per_account,
            "projectsPerAccount": settings.max_projects_per_account,
            "projectBytes": settings.max_project_bytes,
            "accountBytes": settings.max_account_bytes,
            "notebooksPerAccount": settings.max_notebooks_per_account,
            "notebookBytes": settings.max_notebook_bytes,
            "artifactsPerAccount": settings.max_artifacts_per_account,
            "artifactBytes": settings.max_artifact_bytes,
            "artifactAccountBytes": settings.max_artifact_account_bytes,
            "recoverySnapshotsPerAccount": settings.max_recovery_snapshots_per_account,
            "datasetsPerAccount": settings.max_datasets_per_account,
            "modelsPerAccount": settings.max_models_per_account,
            "parameterSetsPerAccount": settings.max_parameter_sets_per_account,
            "executionRunsPerAccount": settings.max_execution_runs_per_account,
            "executionEnvironmentsPerAccount": settings.max_execution_environments_per_account,
            "runtimeAdaptersPerAccount": settings.max_runtime_adapters_per_account,
            "reproductionExecutionPlansPerAccount": settings.max_reproduction_execution_plans_per_account,
            "runtimeHandoffReceiptsPerAccount": settings.max_runtime_handoff_receipts_per_account,
            "executionPoliciesPerAccount": settings.max_execution_policies_per_account,
            "executionPolicyDecisionsPerAccount": settings.max_execution_policy_decisions_per_account,
            "runtimeExecutionAttestationsPerAccount": settings.max_runtime_execution_attestations_per_account,
            "runtimeTrustPoliciesPerAccount": settings.max_runtime_trust_policies_per_account,
            "complianceWaiversPerAccount": settings.max_compliance_waivers_per_account,
            "attestationVerificationsPerAccount": settings.max_attestation_verifications_per_account,
            "jobsPerAccount": settings.max_jobs_per_account,
            "defaultJobMaxAttempts": settings.default_job_max_attempts,
        },
    }


@app.get("/v1/authorization")
def authorization_profile_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-backend-authorization-response/1.0", "item": authorization_profile()}


@app.get("/v1/authorization/identity")
def authorization_identity_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-principal-identity-response/1.0", "item": authorization_principal_payload(identity)}


@app.post("/v1/authorization/evaluate")
def authorization_evaluate_route(payload: AuthorizationEvaluateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return evaluate_authorization_and_record(db, identity, payload)


@app.get("/v1/authorization/decisions")
def authorization_decisions_route(limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-authorization-decision-receipt-index/1.0", "items": list_authorization_decisions(db, identity.user_key, limit)}




def _raise_platform_core_runtime(exc: PlatformCoreRuntimeError):
    raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc


@app.get("/v1/platform-core-runtime")
def platform_core_runtime_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-platform-core-runtime-response/1.0", "item": platform_core_runtime_profile()}


@app.get("/v1/platform-core-runtime/readiness")
def platform_core_runtime_readiness_route(identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        return platform_core_runtime_readiness()
    except PlatformCoreRuntimeError as exc:
        _raise_platform_core_runtime(exc)


@app.post("/v1/platform-core-runtime/sessions")
def platform_core_runtime_session_create(payload: PlatformCoreSessionRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        with session_scope() as db:
            return ensure_platform_core_session(db, identity.user_key, payload)
    except PlatformCoreRuntimeError as exc:
        _raise_platform_core_runtime(exc)


@app.get("/v1/platform-core-runtime/projects/{project_id}")
def platform_core_runtime_project_context(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        with session_scope() as db:
            item = platform_core_project_context(db, identity.user_key, project_id)
            if item is None:
                raise HTTPException(status_code=404, detail={"code": "platform-core-session-not-found", "projectId": project_id})
            return item
    except PlatformCoreRuntimeError as exc:
        _raise_platform_core_runtime(exc)


@app.post("/v1/platform-core-runtime/object-bindings")
def platform_core_runtime_object_bind(payload: PlatformCoreObjectBindingRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        with session_scope() as db: return bind_platform_core_object(db, identity.user_key, payload)
    except PlatformCoreRuntimeError as exc: _raise_platform_core_runtime(exc)


@app.post("/v1/platform-core-runtime/execution-bindings")
def platform_core_runtime_execution_bind(payload: PlatformCoreExecutionBindingRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        with session_scope() as db: return bind_platform_core_execution(db, identity.user_key, payload)
    except PlatformCoreRuntimeError as exc: _raise_platform_core_runtime(exc)


@app.post("/v1/platform-core-runtime/visual-bindings")
def platform_core_runtime_visual_bind(payload: PlatformCoreVisualBindingRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        with session_scope() as db: return bind_platform_core_visual(db, identity.user_key, payload)
    except PlatformCoreRuntimeError as exc: _raise_platform_core_runtime(exc)


@app.post("/v1/platform-core-runtime/package-bindings")
def platform_core_runtime_package_bind(payload: PlatformCorePackageBindingRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        with session_scope() as db: return bind_platform_core_package(db, identity.user_key, payload)
    except PlatformCoreRuntimeError as exc: _raise_platform_core_runtime(exc)


@app.post("/v1/platform-core-runtime/handoff-bindings")
def platform_core_runtime_handoff_bind(payload: PlatformCoreHandoffBindingRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        with session_scope() as db: return bind_platform_core_handoff(db, identity.user_key, payload)
    except PlatformCoreRuntimeError as exc: _raise_platform_core_runtime(exc)


def _platform_core_session_view_route(session_id: str, view: str, identity: ServiceIdentity):
    try:
        with session_scope() as db: return platform_core_session_view(db, identity.user_key, session_id, view)
    except PlatformCoreRuntimeError as exc: _raise_platform_core_runtime(exc)


@app.get("/v1/platform-core-runtime/sessions/{session_id}/summary")
def platform_core_runtime_session_summary(session_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    return _platform_core_session_view_route(session_id, "summary", identity)

@app.get("/v1/platform-core-runtime/sessions/{session_id}/lineage")
def platform_core_runtime_session_lineage(session_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    return _platform_core_session_view_route(session_id, "lineage", identity)

@app.get("/v1/platform-core-runtime/sessions/{session_id}/bundle")
def platform_core_runtime_session_bundle(session_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    return _platform_core_session_view_route(session_id, "bundle", identity)

@app.get("/v1/platform-core-runtime/receipts")
def platform_core_runtime_receipts(projectId: str | None = None, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        items = list_platform_core_runtime_receipts(db, identity.user_key, projectId, limit)
        return {"schema": "sc-workspace-platform-core-runtime-receipt-index/1.0", "items": items, "count": len(items)}


@app.get("/v1/backend-native-workspace")
def backend_native_workspace_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-backend-native-scientific-workspace-response/1.0", "item": backend_native_workspace_profile()}


@app.get("/v1/backend-native-workspace/bootstrap")
def backend_native_workspace_bootstrap_route(projectId: str | None = None, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return backend_native_workspace_bootstrap(db, identity, projectId)

@app.get("/v1/frontend-runtime")
def frontend_runtime_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-frontend-runtime-policy-response/1.0", "item": frontend_runtime_profile()}


@app.get("/v1/production-certification")
def production_architecture_certification_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-production-architecture-certification-response/1.0", "item": production_architecture_certification_profile()}


@app.get("/v1/client-contracts")
def typed_client_contracts(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-typed-client-contract-response/1.0", "item": typed_client_contract_profile(app.openapi())}


@app.get("/v1/thin-client-state")
def thin_client_state_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-thin-client-state-response/1.0", "item": thin_client_state_profile()}


@app.get("/v1/thin-client-state/bootstrap")
def thin_client_state_bootstrap_route(projectId: str | None = None, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return thin_client_state_bootstrap(db, identity.user_key, projectId)


@app.get("/v1/sync")
def local_first_sync_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema":"sc-workspace-local-first-sync-response/1.0", "item": local_first_sync_profile()}


@app.get("/v1/sync/bootstrap")
def local_first_sync_bootstrap_route(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return local_first_sync_bootstrap(db, identity.user_key)


@app.post("/v1/sync/envelopes")
def local_first_sync_apply_route(payload: LocalFirstSyncEnvelope, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        status_code, result = apply_local_first_sync_envelope(db, identity.user_key, payload)
        if status_code != 200:
            return JSONResponse(status_code=status_code, content=result)
        return result


@app.post("/v1/sync/reconcile")
def local_first_sync_reconcile_route(payload: LocalFirstSyncReconcileRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return reconcile_local_first_sync(db, identity.user_key, payload)


@app.get("/v1/sync/receipts")
def local_first_sync_receipts_route(limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-local-first-sync-receipt-index/1.0","items":list_local_first_sync_receipts(db,identity.user_key,limit)}


@app.get("/v1/scientific-objects/profile")
def scientific_objects_profile_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "schema": "sc-workspace-scientific-object-api-response/1.0", "item": scientific_object_profile()}


@app.get("/v1/scientific-objects")
def scientific_objects_index_route(kind: str | None = None, projectId: str | None = None, q: str | None = None, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        items = list_scientific_objects(db, identity.user_key, kind, projectId, q, limit)
        return {"schema": "sc-workspace-scientific-object-index/1.0", "backendAuthoritative": True, "items": items, "count": len(items)}


@app.get("/v1/scientific-objects/{kind}/{object_id}")
def scientific_object_get_route(kind: str, object_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        item = get_scientific_object(db, identity.user_key, kind, object_id)
        if item is None:
            raise HTTPException(status_code=404, detail={"code": "scientific-object-not-found", "kind": kind, "objectId": object_id})
        return {"schema": "sc-workspace-scientific-object-response/1.0", "item": item}


@app.get("/v1/scientific-objects/{kind}/{object_id}/revisions")
def scientific_object_history_route(kind: str, object_id: str, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        item = get_scientific_object(db, identity.user_key, kind, object_id)
        if item is None:
            raise HTTPException(status_code=404, detail={"code": "scientific-object-not-found", "kind": kind, "objectId": object_id})
        return scientific_object_history(db, identity.user_key, kind, object_id, limit)


@app.get("/v1/scientific-objects/{kind}/{object_id}/relations")
def scientific_object_relations_route(kind: str, object_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return scientific_object_relations(db, identity.user_key, kind, object_id)


@app.get("/v1/handoffs/profile")
def handoff_profile_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok":True,"schema":"sc-workspace-cross-product-research-handoff-fabric-response/1.0","item":handoff_profile()}

@app.post("/v1/handoffs")
def handoff_create_route(payload: ResearchHandoffRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        try: return create_handoff(db,identity.user_key,payload)
        except ValueError as exc: raise HTTPException(status_code=409,detail={"code":"handoff-validation-failed","message":str(exc)}) from exc

@app.get("/v1/handoffs/{handoff_id}")
def handoff_get_route(handoff_id:str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        item=get_handoff(db,identity.user_key,handoff_id)
        if item is None: raise HTTPException(status_code=404,detail={"code":"handoff-not-found","handoffId":handoff_id})
        return {"schema":"sc-workspace-research-handoff-response/1.0","item":item}

@app.post("/v1/handoffs/{handoff_id}/accept")
def handoff_accept_route(handoff_id:str,payload:ResearchHandoffAcceptRequest,identity:ServiceIdentity=Depends(require_service_identity)):
    with session_scope() as db:
        try: result=accept_handoff(db,identity.user_key,handoff_id,payload)
        except ValueError as exc: raise HTTPException(status_code=409,detail={"code":"handoff-acceptance-failed","message":str(exc)}) from exc
        if result is None: raise HTTPException(status_code=404,detail={"code":"handoff-not-found","handoffId":handoff_id})
        return result

@app.get("/v1/handoff-receipts")
def handoff_receipts_route(limit:int=Query(default=100,ge=1,le=500),identity:ServiceIdentity=Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-research-handoff-receipt-index/1.0","items":list_handoff_fabric_receipts(db,identity.user_key,limit)}


@app.get("/v1/domain-authority")
def domain_authority_profile(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"ok": True, "item": authority_profile()}


@app.post("/v1/domain-authority/validate")
def domain_authority_validate(payload: DomainValidationRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    try:
        item = validate_domain_document(payload.objectKind, payload.document)
    except DomainValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.as_detail()) from exc
    return {"ok": True, "item": item}


@app.get("/v1/domain-mutation-receipts")
def domain_mutation_receipts_index(limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-domain-mutation-receipt-index/1.0", "items": list_mutation_receipts(db, identity.user_key, limit)}


@app.get("/v1/domain-mutation-receipts/{receipt_id}")
def domain_mutation_receipt_get(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_mutation_receipt(db, identity.user_key, receipt_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace domain mutation receipt not found.")
        return {"schema": "sc-workspace-domain-mutation-receipt-response/1.0", "item": mutation_receipt_metadata(row)}


@app.get("/v1/command-query")
def command_query_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-command-query-profile/1.0","item":command_query_profile()}


@app.get("/v1/commands")
def command_registry(identity: ServiceIdentity = Depends(require_service_identity)):
    p=command_query_profile(); return {"schema":"sc-workspace-command-registry/1.0","items":p["commands"],"serverAuthoritative":True}


@app.post("/v1/commands/execute")
def command_execute_route(payload: CommandExecuteRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return execute_command(db, identity.user_key, payload)


@app.get("/v1/command-receipts")
def command_receipts_index(limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-command-receipt-index/1.0","items":list_command_receipts(db,identity.user_key,limit)}


@app.get("/v1/queries")
def query_registry(identity: ServiceIdentity = Depends(require_service_identity)):
    p=command_query_profile(); return {"schema":"sc-workspace-query-registry/1.0","items":p["queries"],"readOnly":True}


@app.post("/v1/queries/execute")
def query_execute_route(payload: QueryExecuteRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return execute_query(db, identity.user_key, payload)


@app.get("/v1/notebook-orchestration")
def notebook_orchestration_contract(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-notebook-orchestration-profile/1.0","item":notebook_orchestration_profile()}


@app.post("/v1/notebook-execution-plans")
def notebook_execution_plan_create(payload: NotebookExecutionPlanRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-notebook-execution-plan-response/1.0","item":notebook_execution_plan_metadata(create_notebook_execution_plan(db,identity.user_key,payload))}


@app.get("/v1/notebook-execution-plans")
def notebook_execution_plan_index(limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-notebook-execution-plan-index/1.0","items":list_notebook_execution_plans(db,identity.user_key,limit)}


@app.get("/v1/notebook-execution-plans/{plan_id}")
def notebook_execution_plan_get(plan_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_notebook_execution_plan(db,identity.user_key,plan_id)
        if row is None: raise HTTPException(status_code=404, detail="Notebook execution plan not found.")
        return {"schema":"sc-workspace-notebook-execution-plan-response/1.0","item":notebook_execution_plan_metadata(row)}


@app.post("/v1/notebook-execution-plans/{plan_id}/dispatch")
def notebook_execution_plan_dispatch(plan_id: str, payload: NotebookExecutionDispatchRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=dispatch_notebook_execution_plan(db,identity.user_key,plan_id,payload.idempotencyKey or "",payload.reason)
        return {"schema":"sc-workspace-notebook-execution-plan-response/1.0","item":notebook_execution_plan_metadata(row)}


@app.post("/v1/notebook-execution-plans/{plan_id}/cancel")
def notebook_execution_plan_cancel(plan_id: str, payload: NotebookExecutionCancelRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=cancel_notebook_execution_plan(db,identity.user_key,plan_id,payload.reason)
        return {"schema":"sc-workspace-notebook-execution-plan-response/1.0","item":notebook_execution_plan_metadata(row)}


@app.get("/v1/notebook-orchestration-receipts")
def notebook_orchestration_receipt_index(limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-notebook-orchestration-receipt-index/1.0","items":list_notebook_orchestration_receipts(db,identity.user_key,limit)}


@app.get("/v1/scientific-study-packages/profile")
def scientific_study_package_profile_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-scientific-study-package-profile-response/1.0","item":study_package_profile()}


@app.post("/v1/scientific-study-packages")
def scientific_study_package_create_route(payload: ScientificStudyPackageCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=create_scientific_study_package(db,identity.user_key,payload)
        return {"schema":"sc-workspace-scientific-study-package-response/1.0","item":scientific_study_package_metadata(row)}


@app.get("/v1/scientific-study-packages")
def scientific_study_package_index(projectId: str | None = None, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-scientific-study-package-index/1.0","items":list_scientific_study_packages(db,identity.user_key,projectId,limit)}


@app.get("/v1/scientific-study-packages/{package_id}")
def scientific_study_package_get_route(package_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_scientific_study_package(db,identity.user_key,package_id)
        if row is None: raise HTTPException(status_code=404, detail="Scientific study package not found.")
        return {"schema":"sc-workspace-scientific-study-package-response/1.0","item":scientific_study_package_metadata(row),"manifest":row.manifest_json}


@app.post("/v1/scientific-study-packages/{package_id}/verify")
def scientific_study_package_verify_route(package_id: str, payload: ScientificStudyPackageVerifyRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return verify_scientific_study_package(db,identity.user_key,package_id,payload.deep)


@app.delete("/v1/scientific-study-packages/{package_id}")
def scientific_study_package_delete_route(package_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"deleted":delete_scientific_study_package(db,identity.user_key,package_id)}


@app.get("/v1/scientific-study-package-receipts")
def scientific_study_package_receipt_index(packageId: str | None = None, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-scientific-study-package-receipt-index/1.0","items":list_scientific_study_package_receipts(db,identity.user_key,packageId,limit)}


@app.get("/v1/visualization-specs/profile")
def visualization_spec_profile_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-visualization-spec-profile-response/1.0","item":visualization_spec_profile()}


@app.post("/v1/visualization-specs")
def visualization_spec_store_route(payload: VisualizationSpecStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_visualization_spec(db, identity.user_key, payload)
        return {"ok":True,"replayed":replayed,"schema":"sc-workspace-visualization-spec-response/1.0","item":visualization_spec_metadata(row),"spec":row.spec_json}


@app.get("/v1/visualization-specs")
def visualization_spec_index(projectId: str | None = None, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-visualization-spec-index/1.0","items":list_visualization_specs(db, identity.user_key, projectId, limit)}


@app.get("/v1/visualization-specs/{visualization_id}")
def visualization_spec_get_route(visualization_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_visualization_spec(db, identity.user_key, visualization_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Visualization specification not found.")
        return {"schema":"sc-workspace-visualization-spec-response/1.0","item":visualization_spec_metadata(row),"spec":row.spec_json}


@app.get("/v1/visualization-specs/{visualization_id}/revisions")
def visualization_spec_revision_index(visualization_id: str, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-visualization-spec-revision-index/1.0","items":list_visualization_spec_revisions(db, identity.user_key, visualization_id, limit)}


@app.delete("/v1/visualization-specs/{visualization_id}")
def visualization_spec_delete_route(visualization_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"deleted":delete_visualization_spec(db, identity.user_key, visualization_id)}


@app.get("/v1/visualization-spec-receipts")
def visualization_spec_receipt_index(visualizationId: str | None = None, limit: int = Query(default=100, ge=1, le=500), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-visualization-spec-receipt-index/1.0","items":list_visualization_spec_receipts(db, identity.user_key, visualizationId, limit)}


@app.get("/v1/read-models/workspace-overview")
def workspace_overview_route(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return workspace_overview(db, identity.user_key)


@app.get("/v1/read-models/projects/{project_id}")
def project_read_model_route(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return project_read_model(db, identity.user_key, project_id)


@app.get("/v1/read-models/notebooks/{notebook_id}")
def notebook_read_model_route(notebook_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return notebook_read_model(db, identity.user_key, notebook_id)


@app.get("/v1/projects")
def projects_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-cloud-index/1.1", "items": list_projects(db, identity.user_key), "automaticSync": False, "explicitSync": True, "store": "workspace-backend-postgresql"}


@app.post("/v1/projects")
def project_store(payload: ProjectStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_project(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": project_metadata(row)}


@app.get("/v1/projects/{project_id}")
def project_get(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_project(db, identity.user_key, project_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace account project copy not found.")
        return {"schema": "sc-workspace-cloud-backup-response/1.1", "item": project_metadata(row), "package": row.package}


@app.delete("/v1/projects/{project_id}")
def project_delete(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok": True, "deleted": delete_project(db, identity.user_key, project_id)}


@app.get("/v1/projects/{project_id}/revisions")
def project_revisions(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-backend-project-revisions/1.0", "projectId": project_id, "items": list_project_revisions(db, identity.user_key, project_id)}


@app.get("/v1/projects/{project_id}/revisions/{revision}")
def project_revision_get(project_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_project_revision(db, identity.user_key, project_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace project revision not found.")
        return {"schema": "sc-workspace-backend-project-revision/1.0", "projectId": project_id, "revision": revision, "backedUpAt": iso(row.backed_up_at), "fingerprint": row.fingerprint, "package": row.package}


@app.get("/v1/notebooks")
def notebooks_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-notebook-cloud-index/1.0", "items": list_notebooks(db, identity.user_key), "automaticSync": False, "explicitSync": True, "store": "workspace-backend-postgresql"}


@app.post("/v1/notebooks")
def notebook_store_route(payload: NotebookStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_notebook(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": notebook_metadata(row)}


@app.get("/v1/notebooks/{notebook_id}")
def notebook_get_route(notebook_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_notebook(db, identity.user_key, notebook_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Notebook account copy not found.")
        return {"schema": "sc-workspace-notebook-cloud-backup-response/1.0", "item": notebook_metadata(row), "package": row.package}


@app.delete("/v1/notebooks/{notebook_id}")
def notebook_delete_route(notebook_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok": True, "deleted": delete_notebook(db, identity.user_key, notebook_id)}


@app.post("/v1/migrations/legacy-user-meta/plan")
def legacy_migration_plan(payload: LegacyMigrationRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return migration_plan(db, identity.user_key, payload)


@app.post("/v1/migrations/legacy-user-meta/apply")
def legacy_migration_apply(payload: LegacyMigrationRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    payload.dryRun = False
    with session_scope() as db:
        return apply_migration(db, identity.user_key, payload)


@app.get("/v1/migrations/receipts")
def migration_receipts(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-migration-receipt-index/1.0", "items": list_receipts(db, identity.user_key)}


@app.get("/v1/artifacts")
def artifacts_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-artifact-index/1.0", "items": list_artifacts(db, identity.user_key)}


@app.post("/v1/artifacts")
def artifact_store_route(payload: ArtifactStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = store_artifact(db, identity.user_key, payload)
        return {"ok": True, "item": artifact_metadata(row)}


@app.get("/v1/artifacts/{artifact_id}")
def artifact_get_route(artifact_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    import base64
    with session_scope() as db:
        row = get_artifact(db, identity.user_key, artifact_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace artifact not found.")
        content = read_artifact_content(row)
        return {"schema": "sc-workspace-artifact-response/1.0", "item": artifact_metadata(row), "contentBase64": base64.b64encode(content).decode("ascii")}


@app.delete("/v1/artifacts/{artifact_id}")
def artifact_delete_route(artifact_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok": True, "deleted": delete_artifact(db, identity.user_key, artifact_id)}


@app.get("/v1/storage/integrity")
def storage_integrity(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        result = verify_artifact_storage(db, identity.user_key)
        return {"schema": "sc-workspace-storage-integrity/1.0", **result}


@app.post("/v1/recovery/snapshots")
def recovery_snapshot_create(payload: RecoverySnapshotRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = create_snapshot(db, identity.user_key, payload.reason)
        return {"ok": True, "item": snapshot_metadata(row)}


@app.get("/v1/recovery/snapshots")
def recovery_snapshot_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-recovery-snapshot-index/1.0", "items": list_snapshots(db, identity.user_key)}


@app.get("/v1/recovery/snapshots/{snapshot_id}")
def recovery_snapshot_get(snapshot_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_snapshot(db, identity.user_key, snapshot_id)
        return {"schema": "sc-workspace-recovery-snapshot/1.0", "item": snapshot_metadata(row), "manifest": row.manifest}


@app.get("/v1/orchestration/routes")
def orchestration_routes(identity: ServiceIdentity = Depends(require_service_identity)):
    return {
        "schema": "sc-workspace-orchestration-route-registry/1.0",
        "items": list(route_registry().values()),
        "serverConfiguredOnly": True,
        "browserSuppliedUrlsAllowed": False,
    }


@app.get("/v1/worker/status")
def worker_status(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-worker-status/1.0", "items": list_worker_heartbeats(db)}


@app.get("/v1/jobs")
def jobs_index(
    status: str | None = Query(default=None, max_length=32),
    targetProduct: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=100, ge=1, le=250),
    identity: ServiceIdentity = Depends(require_service_identity),
):
    with session_scope() as db:
        return {
            "schema": "sc-workspace-job-index/1.0",
            "items": list_jobs(db, identity.user_key, status, targetProduct, limit),
            "durable": True,
            "pollingSupported": True,
        }


@app.post("/v1/jobs")
def job_create_route(payload: JobCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = create_job(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": job_metadata(row)}


@app.get("/v1/jobs/{job_id}")
def job_get_route(job_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_job(db, identity.user_key, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace job not found.")
        return {"schema": "sc-workspace-job/1.0", "item": job_metadata(row), "result": row.result}


@app.get("/v1/jobs/{job_id}/events")
def job_events_route(job_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_job(db, identity.user_key, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace job not found.")
        return {"schema": "sc-workspace-job-event-index/1.0", "jobId": job_id, "items": list_job_events(db, identity.user_key, job_id)}


@app.post("/v1/jobs/{job_id}/cancel")
def job_cancel_route(job_id: str, payload: JobActionRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = request_cancel(db, identity.user_key, job_id, payload.reason)
        return {"ok": True, "item": job_metadata(row)}


@app.post("/v1/jobs/{job_id}/retry")
def job_retry_route(job_id: str, payload: JobActionRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = retry_job(db, identity.user_key, job_id, payload.reason)
        return {"ok": True, "item": job_metadata(row)}


@app.get("/v1/polyglot/runtimes")
def polyglot_runtimes_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema": "sc-workspace-polyglot-runtime-index/1.0", "version": settings.service_version, "items": polyglot_runtime_catalog()}


@app.get("/v1/polyglot/operations")
def polyglot_operations_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema": "sc-workspace-polyglot-operation-index/1.0", "version": settings.service_version, "items": polyglot_operation_catalog()}


@app.get("/v1/polyglot/receipts")
def polyglot_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-polyglot-execution-receipt-index/1.0", "items": list_polyglot_receipts(db, identity.user_key, limit)}


@app.get("/v1/polyglot/receipts/{receipt_id}")
def polyglot_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_polyglot_receipt(db, identity.user_key, receipt_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace polyglot execution receipt not found.")
        return {"schema": "sc-workspace-polyglot-execution-receipt/1.0", "item": polyglot_receipt_metadata(row)}

@app.get("/v1/polyglot/runtimes/r/status")
def r_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema": "sc-workspace-runtime-status/1.0", "item": polyglot_runtime_health("r")}


@app.get("/v1/statistical-model-receipts")
def statistical_model_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-statistical-model-receipt-index/1.0", "items": list_statistical_receipts(db, identity.user_key, limit)}


@app.get("/v1/statistical-model-receipts/{receipt_id}")
def statistical_model_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_statistical_receipt(db, identity.user_key, receipt_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace statistical model receipt not found.")
        return {"schema": "sc-workspace-statistical-model-receipt/1.0", "item": statistical_receipt_metadata(row)}


@app.get("/v1/polyglot/runtimes/julia/status")
def julia_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema": "sc-workspace-runtime-status/1.0", "item": polyglot_runtime_health("julia")}


@app.get("/v1/numerical-simulation-receipts")
def numerical_simulation_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-numerical-simulation-receipt-index/1.0", "items": list_numerical_receipts(db, identity.user_key, limit)}


@app.get("/v1/numerical-simulation-receipts/{receipt_id}")
def numerical_simulation_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_numerical_receipt(db, identity.user_key, receipt_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace numerical simulation receipt not found.")
        return {"schema": "sc-workspace-numerical-simulation-receipt/1.0", "item": numerical_receipt_metadata(row)}



@app.get("/v1/polyglot/runtimes/ml/status")
def ml_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema": "sc-workspace-runtime-status/1.0", "item": polyglot_runtime_health("ml")}


@app.get("/v1/predictive-model-receipts")
def predictive_model_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-predictive-model-receipt-index/1.0","items":list_predictive_model_receipts(db,identity.user_key,limit)}


@app.get("/v1/predictive-model-receipts/{receipt_id}")
def predictive_model_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_predictive_model_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace predictive model receipt not found.")
        return {"schema":"sc-workspace-predictive-model-receipt/1.0","item":predictive_model_receipt_metadata(row)}


@app.get("/v1/model-evaluation-receipts")
def model_evaluation_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-model-evaluation-receipt-index/1.0","items":list_model_evaluation_receipts(db,identity.user_key,limit)}


@app.get("/v1/model-evaluation-receipts/{receipt_id}")
def model_evaluation_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_model_evaluation_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace model evaluation receipt not found.")
        return {"schema":"sc-workspace-model-evaluation-receipt/1.0","item":model_evaluation_receipt_metadata(row)}


@app.get("/v1/polyglot/runtimes/forecast/status")
def forecast_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-runtime-status/1.0","item":polyglot_runtime_health("forecast")}

@app.get("/v1/forecast-receipts")
def forecast_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-forecast-receipt-index/1.0","items":list_forecast_receipts(db,identity.user_key,limit)}

@app.get("/v1/forecast-receipts/{receipt_id}")
def forecast_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_forecast_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace forecast receipt not found.")
        return {"schema":"sc-workspace-forecast-receipt/1.0","item":forecast_receipt_metadata(row)}

@app.get("/v1/forecast-evaluation-receipts")
def forecast_evaluation_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-forecast-evaluation-receipt-index/1.0","items":list_forecast_evaluation_receipts(db,identity.user_key,limit)}

@app.get("/v1/forecast-evaluation-receipts/{receipt_id}")
def forecast_evaluation_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_forecast_evaluation_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace forecast evaluation receipt not found.")
        return {"schema":"sc-workspace-forecast-evaluation-receipt/1.0","item":forecast_evaluation_receipt_metadata(row)}

@app.get("/v1/interchange/runtime/status")
def interchange_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-runtime-status/1.0","item":interchange_runtime_health()}

@app.get("/v1/interchange/operations")
def interchange_operations_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-interchange-operation-index/1.0","version":settings.service_version,"items":interchange_operation_catalog(),"formats":["arrow-ipc-stream","parquet"],"boundedOperationsOnly":True,"arbitraryCodeExecution":False}

@app.get("/v1/interchange/receipts")
def interchange_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-interchange-receipt-index/1.0","items":list_interchange_receipts(db,identity.user_key,limit)}

@app.get("/v1/interchange/receipts/{receipt_id}")
def interchange_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_interchange_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace interchange receipt not found.")
        return {"schema":"sc-workspace-interchange-receipt/1.0","item":interchange_receipt_metadata(row)}

@app.get("/v1/reproduction/cross-runtime/profiles")
def cross_runtime_verification_profiles_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-cross-runtime-verification-profile-index/1.0","version":settings.service_version,"items":cross_runtime_verification_profiles(),"automaticExecution":False,"arbitraryCodeExecution":False}

@app.get("/v1/reproduction/cross-runtime/verifications")
def cross_runtime_verifications_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-cross-runtime-verification-receipt-index/1.0","items":list_cross_runtime_verification_receipts(db,identity.user_key,limit)}

@app.post("/v1/reproduction/cross-runtime/verifications")
def cross_runtime_verification_create_route(payload: CrossRuntimeVerificationCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=create_cross_runtime_verification(db,identity.user_key,payload)
        return {"ok":True,"item":cross_runtime_verification_receipt_metadata(row)}

@app.get("/v1/reproduction/cross-runtime/verifications/{receipt_id}")
def cross_runtime_verification_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_cross_runtime_verification_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace cross-runtime verification receipt not found.")
        return {"schema":"sc-workspace-cross-runtime-verification-receipt/1.0","item":cross_runtime_verification_receipt_metadata(row)}


@app.get("/v1/compute/operations")
def compute_operations_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {
        "schema": "sc-workspace-scientific-compute-operation-index/1.0",
        "version": settings.service_version,
        "items": compute_catalog(),
        "arbitraryCodeExecution": False,
        "boundedOperationsOnly": True,
    }


@app.get("/v1/compute/receipts")
def compute_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-compute-execution-receipt-index/1.0", "items": list_compute_receipts(db, identity.user_key, limit)}


@app.get("/v1/compute/receipts/{receipt_id}")
def compute_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_compute_receipt(db, identity.user_key, receipt_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace compute execution receipt not found.")
        return {"schema": "sc-workspace-compute-execution-receipt/1.0", "item": compute_receipt_metadata(row)}


@app.get("/v1/datasets")
def datasets_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-dataset-index/1.0", "items": list_datasets(db, identity.user_key, projectId), "revisioned": True}


@app.post("/v1/datasets")
def dataset_store_route(payload: DatasetStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_dataset(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": dataset_metadata(row)}


@app.get("/v1/datasets/{dataset_id}")
def dataset_get_route(dataset_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_dataset(db, identity.user_key, dataset_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace dataset not found.")
        return {"schema": "sc-workspace-dataset-response/1.0", "item": dataset_metadata(row)}


@app.get("/v1/datasets/{dataset_id}/revisions")
def dataset_revisions_route(dataset_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-dataset-revision-index/1.0", "datasetId": dataset_id, "items": list_dataset_revisions(db, identity.user_key, dataset_id)}


@app.get("/v1/datasets/{dataset_id}/revisions/{revision}")
def dataset_revision_get_route(dataset_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_dataset_revision(db, identity.user_key, dataset_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace dataset revision not found.")
        return {"schema": "sc-workspace-dataset-revision/1.0", "item": dataset_metadata(row)}


@app.get("/v1/models")
def models_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-model-index/1.0", "items": list_models(db, identity.user_key, projectId), "revisioned": True}


@app.post("/v1/models")
def model_store_route(payload: ModelStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_model(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": model_metadata(row)}


@app.get("/v1/models/{model_id}")
def model_get_route(model_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_model(db, identity.user_key, model_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace model not found.")
        return {"schema": "sc-workspace-model-response/1.0", "item": model_metadata(row)}


@app.get("/v1/models/{model_id}/revisions")
def model_revisions_route(model_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-model-revision-index/1.0", "modelId": model_id, "items": list_model_revisions(db, identity.user_key, model_id)}


@app.get("/v1/models/{model_id}/revisions/{revision}")
def model_revision_get_route(model_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_model_revision(db, identity.user_key, model_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace model revision not found.")
        return {"schema": "sc-workspace-model-revision/1.0", "item": model_metadata(row)}


@app.get("/v1/parameter-sets")
def parameter_sets_index(modelId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-parameter-set-index/1.0", "items": list_parameter_sets(db, identity.user_key, modelId), "revisioned": True}


@app.post("/v1/parameter-sets")
def parameter_set_store_route(payload: ParameterSetStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_parameter_set(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": parameter_set_metadata(row)}


@app.get("/v1/parameter-sets/{parameter_set_id}")
def parameter_set_get_route(parameter_set_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_parameter_set(db, identity.user_key, parameter_set_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace parameter set not found.")
        return {"schema": "sc-workspace-parameter-set-response/1.0", "item": parameter_set_metadata(row)}


@app.get("/v1/parameter-sets/{parameter_set_id}/revisions")
def parameter_set_revisions_route(parameter_set_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-parameter-set-revision-index/1.0", "parameterSetId": parameter_set_id, "items": list_parameter_set_revisions(db, identity.user_key, parameter_set_id)}


@app.get("/v1/parameter-sets/{parameter_set_id}/revisions/{revision}")
def parameter_set_revision_get_route(parameter_set_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_parameter_set_revision(db, identity.user_key, parameter_set_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace parameter-set revision not found.")
        return {"schema": "sc-workspace-parameter-set-revision/1.0", "item": parameter_set_metadata(row)}


@app.get("/v1/execution-environments")
def execution_environments_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-environment-index/1.0", "items": list_environments(db, identity.user_key, projectId), "revisioned": True}


@app.post("/v1/execution-environments")
def execution_environment_store_route(payload: ExecutionEnvironmentStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_environment(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": environment_metadata(row)}


@app.get("/v1/execution-environments/{environment_id}")
def execution_environment_get_route(environment_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_environment(db, identity.user_key, environment_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution environment not found.")
        return {"schema": "sc-workspace-execution-environment-response/1.0", "item": environment_metadata(row)}


@app.get("/v1/execution-environments/{environment_id}/revisions")
def execution_environment_revisions_route(environment_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-environment-revision-index/1.0", "environmentId": environment_id, "items": list_environment_revisions(db, identity.user_key, environment_id)}


@app.get("/v1/execution-environments/{environment_id}/revisions/{revision}")
def execution_environment_revision_get_route(environment_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_environment_revision(db, identity.user_key, environment_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution-environment revision not found.")
        return {"schema": "sc-workspace-execution-environment-revision/1.0", "item": environment_metadata(row)}



@app.get("/v1/runtime-adapters")
def runtime_adapters_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-runtime-adapter-index/1.0","items":list_adapters(db,identity.user_key,projectId),"revisioned":True}


@app.post("/v1/runtime-adapters")
def runtime_adapter_store_route(payload: RuntimeAdapterStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row,replayed=store_adapter(db,identity.user_key,payload)
        return {"ok":True,"replayed":replayed,"item":adapter_metadata(row)}


@app.get("/v1/runtime-adapters/{adapter_id}")
def runtime_adapter_get_route(adapter_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_adapter(db,identity.user_key,adapter_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime adapter not found.")
        return {"schema":"sc-workspace-runtime-adapter-response/1.0","item":adapter_metadata(row)}


@app.get("/v1/runtime-adapters/{adapter_id}/revisions")
def runtime_adapter_revisions_route(adapter_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-runtime-adapter-revision-index/1.0","adapterId":adapter_id,"items":list_adapter_revisions(db,identity.user_key,adapter_id)}


@app.get("/v1/runtime-adapters/{adapter_id}/revisions/{revision}")
def runtime_adapter_revision_get_route(adapter_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_adapter_revision(db,identity.user_key,adapter_id,revision)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime-adapter revision not found.")
        return {"schema":"sc-workspace-runtime-adapter-revision/1.0","item":adapter_metadata(row)}


@app.post("/v1/runtime-adapters/{adapter_id}/compatibility")
def runtime_adapter_compatibility_route(adapter_id: str, payload: RuntimeCompatibilityCheckRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_adapter(db,identity.user_key,adapter_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime adapter not found.")
        return check_environment_compatibility(db,identity.user_key,row,payload.environmentRef)


@app.get("/v1/execution-policies")
def execution_policies_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-policy-index/1.0", "items": list_policies(db, identity.user_key, projectId)}


@app.post("/v1/execution-policies")
def execution_policy_store_route(payload: ExecutionPolicyStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_policy(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": policy_metadata(row)}


@app.get("/v1/execution-policies/{policy_id}")
def execution_policy_get_route(policy_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_policy(db, identity.user_key, policy_id)
        if row is None: raise HTTPException(status_code=404, detail="Workspace execution policy not found.")
        return {"schema": "sc-workspace-execution-policy-response/1.0", "item": policy_metadata(row)}


@app.get("/v1/execution-policies/{policy_id}/revisions")
def execution_policy_revisions_route(policy_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-policy-revisions/1.0", "items": list_policy_revisions(db, identity.user_key, policy_id)}


@app.get("/v1/execution-policy-decisions")
def execution_policy_decisions_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-policy-decision-index/1.0", "items": list_policy_decisions(db, identity.user_key)}


@app.get("/v1/execution-policy-decisions/{decision_id}")
def execution_policy_decision_get_route(decision_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_policy_decision(db, identity.user_key, decision_id)
        if row is None: raise HTTPException(status_code=404, detail="Workspace execution-policy decision not found.")
        return {"schema": "sc-workspace-execution-policy-decision-response/1.0", "item": policy_decision_metadata(row)}


@app.get("/v1/reproduction-plans")
def reproduction_plans_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-reproduction-plan-index/1.0","items":list_reproduction_plans(db,identity.user_key)}


@app.post("/v1/reproduction-plans")
def reproduction_plan_create_route(payload: ReproductionPlanCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"item":plan_metadata(create_reproduction_plan(db,identity.user_key,payload))}


@app.get("/v1/reproduction-plans/{plan_id}")
def reproduction_plan_get_route(plan_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_reproduction_plan(db,identity.user_key,plan_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace reproduction plan not found.")
        return {"schema":"sc-workspace-reproduction-plan-response/1.0","item":plan_metadata(row)}


@app.get("/v1/reproduction-verifications")
def reproduction_verifications_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-reproduction-verification-index/1.0","items":list_verifications(db,identity.user_key)}


@app.post("/v1/reproduction-verifications")
def reproduction_verification_create_route(payload: ReproductionVerificationCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"item":verification_metadata(create_verification(db,identity.user_key,payload))}


@app.get("/v1/reproduction-verifications/{verification_id}")
def reproduction_verification_get_route(verification_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_verification(db,identity.user_key,verification_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace reproduction verification not found.")
        return {"schema":"sc-workspace-reproduction-verification-response/1.0","item":verification_metadata(row)}


@app.get("/v1/reproduction-execution-plans")
def reproduction_execution_plans_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-reproduction-execution-plan-index/1.0","items":list_execution_plans(db,identity.user_key),"automaticDispatch":False}


@app.post("/v1/reproduction-execution-plans")
def reproduction_execution_plan_create_route(payload: ReproductionExecutionPlanCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"item":execution_plan_metadata(create_execution_plan(db,identity.user_key,payload))}


@app.get("/v1/reproduction-execution-plans/{execution_plan_id}")
def reproduction_execution_plan_get_route(execution_plan_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_execution_plan(db,identity.user_key,execution_plan_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace reproduction execution plan not found.")
        return {"schema":"sc-workspace-reproduction-execution-plan-response/1.0","item":execution_plan_metadata(row)}


@app.post("/v1/reproduction-execution-plans/{execution_plan_id}/handoff")
def reproduction_execution_plan_handoff_route(execution_plan_id: str, payload: ControlledRuntimeHandoffRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        receipt,replayed,job=dispatch_execution_plan(db,identity.user_key,execution_plan_id,payload)
        return {"ok":True,"replayed":replayed,"item":handoff_receipt_metadata(receipt),"job":job}


@app.get("/v1/runtime-handoff-receipts")
def runtime_handoff_receipts_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-runtime-handoff-receipt-index/1.0","items":list_handoff_receipts(db,identity.user_key)}


@app.get("/v1/runtime-handoff-receipts/{receipt_id}")
def runtime_handoff_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_handoff_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime handoff receipt not found.")
        return {"schema":"sc-workspace-runtime-handoff-receipt-response/1.0","item":handoff_receipt_metadata(row)}


@app.get("/v1/runtime-execution-attestations")
def runtime_execution_attestations_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-runtime-execution-attestation-index/1.0", "items": list_runtime_attestations(db, identity.user_key), "browserSubmissionAllowed": False}


@app.get("/v1/runtime-execution-attestations/{attestation_id}")
def runtime_execution_attestation_get(attestation_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_runtime_attestation(db, identity.user_key, attestation_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace runtime-execution attestation not found.")
        return {"schema": "sc-workspace-runtime-execution-attestation-response/1.0", "item": attestation_metadata(row)}


@app.post("/v1/runtime-handoff-receipts/{receipt_id}/attest")
def runtime_handoff_attest(receipt_id: str, payload: RuntimeExecutionAttestationRequest, identity: ServiceIdentity = Depends(require_runtime_attestation_identity)):
    with session_scope() as db:
        row, replayed = create_runtime_attestation(db, identity.user_key, receipt_id, payload)
        return {"ok": True, "replayed": replayed, "item": attestation_metadata(row)}


@app.get("/v1/runtime-trust-policies")
def runtime_trust_policies_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-runtime-trust-policy-index/1.0","items":list_trust_policies(db,identity.user_key,projectId)}


@app.post("/v1/runtime-trust-policies")
def runtime_trust_policy_store_route(payload: RuntimeTrustPolicyStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row,replayed=store_trust_policy(db,identity.user_key,payload)
        return {"ok":True,"replayed":replayed,"item":trust_policy_metadata(row)}


@app.get("/v1/runtime-trust-policies/{policy_id}")
def runtime_trust_policy_get_route(policy_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_trust_policy(db,identity.user_key,policy_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime-trust policy not found.")
        return {"schema":"sc-workspace-runtime-trust-policy-response/1.0","item":trust_policy_metadata(row)}


@app.get("/v1/runtime-trust-policies/{policy_id}/revisions")
def runtime_trust_policy_revisions_route(policy_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-runtime-trust-policy-revisions/1.0","items":list_trust_policy_revisions(db,identity.user_key,policy_id)}


@app.get("/v1/compliance-waivers")
def compliance_waivers_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-compliance-waiver-index/1.0","items":list_waivers(db,identity.user_key),"executionPolicyRelaxationAllowed":False}


@app.post("/v1/compliance-waivers")
def compliance_waiver_create_route(payload: ComplianceWaiverCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"item":waiver_metadata(create_waiver(db,identity.user_key,payload))}


@app.get("/v1/compliance-waivers/{waiver_id}")
def compliance_waiver_get_route(waiver_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_waiver(db,identity.user_key,waiver_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace compliance waiver not found.")
        return {"schema":"sc-workspace-compliance-waiver-response/1.0","item":waiver_metadata(row)}


@app.get("/v1/attestation-verifications")
def attestation_verifications_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-attestation-verification-index/1.0","items":list_compliance_verifications(db,identity.user_key),"automaticExecutionAuthorization":False}


@app.post("/v1/attestation-verifications")
def attestation_verification_create_route(payload: AttestationVerificationCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=create_compliance_verification(db,identity.user_key,payload)
        return {"ok":True,"item":compliance_verification_metadata(row)}


@app.get("/v1/attestation-verifications/{verification_id}")
def attestation_verification_get_route(verification_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_compliance_verification(db,identity.user_key,verification_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace attestation verification not found.")
        return {"schema":"sc-workspace-attestation-verification-response/1.0","item":compliance_verification_metadata(row)}


@app.get("/v1/runs")
def execution_runs_index(
    status: str | None = Query(default=None, max_length=32),
    projectId: str | None = Query(default=None, max_length=160),
    limit: int = Query(default=100, ge=1, le=250),
    identity: ServiceIdentity = Depends(require_service_identity),
):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-run-index/1.0", "items": list_execution_runs(db, identity.user_key, status, projectId, limit)}


@app.post("/v1/runs")
def execution_run_create_route(payload: ExecutionRunCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = create_execution_run(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": run_metadata(row)}


@app.get("/v1/runs/{run_id}")
def execution_run_get_route(run_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_execution_run(db, identity.user_key, run_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution run not found.")
        return {"schema": "sc-workspace-execution-run-response/1.0", "item": run_metadata(row)}


@app.post("/v1/runs/{run_id}/state")
def execution_run_update_route(run_id: str, payload: ExecutionRunUpdateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = update_execution_run(db, identity.user_key, run_id, payload)
        return {"ok": True, "item": run_metadata(row)}


@app.get("/v1/runs/{run_id}/events")
def execution_run_events_route(run_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_execution_run(db, identity.user_key, run_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution run not found.")
        return {"schema": "sc-workspace-execution-run-event-index/1.0", "runId": run_id, "items": list_run_events(db, identity.user_key, run_id)}


@app.get("/v1/runs/{run_id}/outputs")
def execution_run_outputs_route(run_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-run-output-index/1.0", "runId": run_id, "items": list_run_outputs(db, identity.user_key, run_id)}


@app.post("/v1/runs/{run_id}/outputs")
def execution_run_output_store_route(run_id: str, payload: ExecutionRunOutputRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_run_output(db, identity.user_key, run_id, payload)
        return {"ok": True, "replayed": replayed, "item": output_metadata(row)}

@app.get("/v1/polyglot/runtimes/probability/status")
def probability_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-runtime-status/1.0","item":polyglot_runtime_health("probability")}

@app.get("/v1/probabilistic-inference-receipts")
def probabilistic_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-probabilistic-inference-receipt-index/1.0","items":list_probabilistic_inference_receipts(db,identity.user_key,limit)}

@app.get("/v1/probabilistic-inference-receipts/{receipt_id}")
def probabilistic_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_probabilistic_inference_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace probabilistic inference receipt not found.")
        return {"schema":"sc-workspace-probabilistic-inference-receipt/1.0","item":probabilistic_inference_receipt_metadata(row)}

@app.get("/v1/polyglot/runtimes/uncertainty/status")
def uncertainty_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-runtime-status/1.0","item":polyglot_runtime_health("uncertainty")}

@app.get("/v1/uncertainty-analysis-receipts")
def uncertainty_analysis_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-uncertainty-analysis-receipt-index/1.0","items":list_uncertainty_analysis_receipts(db,identity.user_key,limit)}

@app.get("/v1/uncertainty-analysis-receipts/{receipt_id}")
def uncertainty_analysis_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_uncertainty_analysis_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace uncertainty analysis receipt not found.")
        return {"schema":"sc-workspace-uncertainty-analysis-receipt/1.0","item":uncertainty_analysis_receipt_metadata(row)}

@app.get("/v1/polyglot/runtimes/optimization/status")
def optimization_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-runtime-status/1.0","item":polyglot_runtime_health("optimization")}

@app.get("/v1/optimization-receipts")
def optimization_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-optimization-receipt-index/1.0","items":list_optimization_receipts(db,identity.user_key,limit)}

@app.get("/v1/optimization-receipts/{receipt_id}")
def optimization_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_optimization_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace optimization receipt not found.")
        return {"schema":"sc-workspace-optimization-receipt/1.0","item":optimization_receipt_metadata(row)}


@app.get("/v1/polyglot/runtimes/decision/status")
def decision_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-runtime-status/1.0","item":polyglot_runtime_health("decision")}

@app.get("/v1/decision-optimization-receipts")
def decision_optimization_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-decision-optimization-receipt-index/1.0","items":list_decision_optimization_receipts(db,identity.user_key,limit)}

@app.get("/v1/decision-optimization-receipts/{receipt_id}")
def decision_optimization_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_decision_optimization_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace decision optimization receipt not found.")
        return {"schema":"sc-workspace-decision-optimization-receipt/1.0","item":decision_optimization_receipt_metadata(row)}


@app.get("/v1/polyglot/runtimes/reliability/status")
def reliability_runtime_status_route(identity: ServiceIdentity = Depends(require_service_identity)):
    return {"schema":"sc-workspace-runtime-status/1.0","item":polyglot_runtime_health("reliability")}

@app.get("/v1/reliability-analysis-receipts")
def reliability_analysis_receipts_route(limit: int = Query(default=100, ge=1, le=250), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db: return {"schema":"sc-workspace-reliability-analysis-receipt-index/1.0","items":list_reliability_analysis_receipts(db,identity.user_key,limit)}

@app.get("/v1/reliability-analysis-receipts/{receipt_id}")
def reliability_analysis_receipt_get_route(receipt_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_reliability_analysis_receipt(db,identity.user_key,receipt_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace reliability analysis receipt not found.")
        return {"schema":"sc-workspace-reliability-analysis-receipt/1.0","item":reliability_analysis_receipt_metadata(row)}
