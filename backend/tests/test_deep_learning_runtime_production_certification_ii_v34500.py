from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import sys

P = pathlib.Path(__file__).resolve().parents[1] / "neural-runtime" / "service.py"
spec = importlib.util.spec_from_file_location("sc_neural_v34500", P)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT = P.parents[1]
REPO = ROOT.parent


def test_certification_identity_registry_and_fingerprint():
    h = s.health()
    assert h["version"] == "3.45.0"
    assert len(h["operations"]) == 141
    assert h["deepLearningRuntimeProductionCertificationII"] is True
    assert h["deepLearningRuntimeProductionCertificationIISchema"] == "sc-workspace-neural-production-certification-ii/1.0"
    assert h["deepLearningRuntimeCertifiedBaseline"] == "3.45.0"
    assert h["deepLearningRuntimeRollbackBaseline"] == "3.44.0"
    assert h["deepLearningRuntimeCertifiedOperationCount"] == 141
    expected = hashlib.sha256("\n".join(sorted(h["operations"])).encode("utf-8")).hexdigest()
    assert h["deepLearningRuntimeOperationRegistrySha256"] == expected


def test_all_certified_deep_learning_domains_remain_enabled():
    h = s.health()
    required = {
        "graphNeuralNetworkRuntimeFoundation": True,
        "computerVisionRemoteSensingRuntime": True,
        "temporalDeepLearningSequenceRuntime": True,
        "multimodalNeuralRuntime": True,
        "neuralSymbolicResearchIntelligenceRuntime": True,
        "reproducibleDeepLearningResearchPackagesRuntime": True,
        "distributedNeuralExecutionWorkerFabricRuntime": True,
        "advancedAcceleratorSchedulingResourceGovernanceRuntime": True,
        "modelServingBatchInferenceResearchDeploymentRuntime": True,
        "crossRuntimeMLNeuralWorkflowOrchestrationRuntime": True,
    }
    for key, value in required.items():
        assert h[key] is value, key
    assert len(h["deepLearningRuntimeCertificationDomains"]) == 10


def test_production_guardrails_remain_fail_closed():
    h = s.health()
    assert h["arbitraryCodeExecution"] is False
    assert h["clientSuppliedCodeAllowed"] is False
    assert h["clientSuppliedPackagesAllowed"] is False
    assert h["clientSuppliedRuntimeUrlsAllowed"] is False
    assert h["clientSuppliedSerializedModelsAllowed"] is False
    assert h["modelServingPublicNetworkExposureEnabled"] is False
    assert h["researchDeploymentInfrastructureMutationEnabled"] is False
    assert h["crossRuntimeAutomaticExecutionEnabled"] is False
    assert h["deepLearningRuntimeInfrastructureMutationEnabled"] is False
    for key in ("shellCommand", "python", "runtimeUrl", "apiKey", "serializedPayload", "workerUrl"):
        assert key in s.BLOCKED_PAYLOAD_KEYS


def test_workspace_registry_parity_and_current_artifact_store_contract():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n = RUNTIME_BY_LANGUAGE["neural"]
    assert len(n.operations) == 141
    assert set(n.operations) == set(s.OPERATIONS)
    poly = (ROOT / "app" / "polyglot.py").read_text()
    assert '"schema":"sc-workspace-artifact-store/1.0"' in poly or '"schema": "sc-workspace-artifact-store/1.0"' in poly
    assert "sc-workspace-artifact-store-request/1.0" not in poly


def test_backend_health_contract_exposes_certification_ii_without_registry_growth():
    main = (ROOT / "app" / "main.py").read_text()
    assert '"neuralRuntimeBoundedOperations": 141' in main
    assert '"deepLearningRuntimeProductionCertificationII": True' in main
    assert '"deepLearningRuntimeCertifiedBaseline": "3.45.0"' in main
    assert '"deepLearningRuntimeRollbackBaseline": "3.44.0"' in main
    assert '"deepLearningRuntimeFrontendContinuityCertified": True' in main


def test_wordpress_identity_frontend_continuity_and_rollback_metadata():
    wp = REPO / "wordpress" / "sustainable-catalyst-workspace"
    if not wp.exists():
        # Backend-only packages intentionally exclude WordPress assets; backend health must still
        # advertise that full-release frontend continuity is part of the certification contract.
        main = (ROOT / "app" / "main.py").read_text()
        assert '"deepLearningRuntimeFrontendContinuityCertified": True' in main
        return
    plugin = (wp / "sustainable-catalyst-workspace.php").read_text()
    assert "Version: 3.45.0" in plugin
    assert "SC_WORKSPACE_VERSION', '3.45.0'" in plugin
    css = wp / "assets" / "css" / "workspace-v3.45.0.css"
    js = wp / "assets" / "js" / "workspace-v3.45.0.js"
    assert css.stat().st_size >= 100000
    assert js.stat().st_size >= 5000
    cls = (wp / "includes" / "class-sc-workspace.php").read_text()
    assert "workspace-v3.45.0.css" in cls and "workspace-v3.45.0.js" in cls
    dep = (wp / "includes" / "class-sc-workspace-deployment.php").read_text()
    assert "const PREVIOUS_RELEASE = '3.44.0';" in dep
    assert "const ROLLBACK_RELEASE = '3.44.0';" in dep
    assert "const CANONICAL_PLUGIN_ROOT = 'sustainable-catalyst-workspace';" in dep
    assert "const MIN_CURRENT_STYLE_BYTES = 100000;" in dep
    assert "const MIN_CURRENT_SCRIPT_BYTES = 5000;" in dep


def test_certification_is_non_migrating_release():
    assert not (ROOT / "migrations" / "0042_workspace_v34500.sql").exists()
    doc = REPO / "DEEP_LEARNING_RUNTIME_PRODUCTION_CERTIFICATION_II_V34500.md"
    if doc.exists():
        assert "No database migration" in doc.read_text()
