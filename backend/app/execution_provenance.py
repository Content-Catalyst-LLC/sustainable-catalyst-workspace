from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .environments import environment_metadata, get_environment, get_environment_revision
from .models import (
    ComputeExecutionReceipt,
    CrossRuntimeVerificationReceipt,
    DecisionOptimizationReceipt,
    ForecastEvaluationReceipt,
    ForecastReceipt,
    InterchangeReceipt,
    ModelEvaluationReceipt,
    NumericalSimulationReceipt,
    OptimizationReceipt,
    PolyglotExecutionReceipt,
    PredictiveModelReceipt,
    ProbabilisticInferenceReceipt,
    ReliabilityAnalysisReceipt,
    ResearchSessionObjectBinding,
    ScientificExecutionProvenanceSnapshot,
    StatisticalModelReceipt,
    UncertaintyAnalysisReceipt,
)
from .registry import (
    dataset_metadata,
    get_dataset,
    get_dataset_revision,
    get_execution_run,
    get_model,
    get_model_revision,
    get_parameter_set,
    get_parameter_set_revision,
    list_execution_runs,
    list_run_events,
    list_run_outputs,
    model_metadata,
    parameter_set_metadata,
    run_metadata,
)
from .runtime_adapters import adapter_metadata, get_adapter, get_adapter_revision
from .utils import iso, sha256_hex

EXECUTION_PROVENANCE_SCHEMA = "sc-workspace-scientific-execution-provenance-workspace/1.0"
EXECUTION_PROVENANCE_RUN_SCHEMA = "sc-workspace-scientific-execution-provenance-run/1.0"
EXECUTION_PROVENANCE_SNAPSHOT_SCHEMA = "sc-workspace-scientific-execution-provenance-snapshot/1.0"
EXECUTION_PROVENANCE_SNAPSHOT_REQUEST_SCHEMA = "sc-workspace-scientific-execution-provenance-snapshot-request/1.0"


class ScientificExecutionProvenanceSnapshotRequest(BaseModel):
    schema_: Literal["sc-workspace-scientific-execution-provenance-snapshot-request/1.0"] = Field(alias="schema")
    runId: str | None = Field(default=None, max_length=96)
    includeEvents: bool = True
    includeReceipts: bool = True
    model_config = ConfigDict(populate_by_name=True)


_RECEIPT_MODELS: tuple[tuple[str, type], ...] = (
    ("compute", ComputeExecutionReceipt),
    ("polyglot", PolyglotExecutionReceipt),
    ("statistical-model", StatisticalModelReceipt),
    ("numerical-simulation", NumericalSimulationReceipt),
    ("predictive-model", PredictiveModelReceipt),
    ("model-evaluation", ModelEvaluationReceipt),
    ("forecast", ForecastReceipt),
    ("forecast-evaluation", ForecastEvaluationReceipt),
    ("probabilistic-inference", ProbabilisticInferenceReceipt),
    ("uncertainty-analysis", UncertaintyAnalysisReceipt),
    ("optimization", OptimizationReceipt),
    ("decision-optimization", DecisionOptimizationReceipt),
    ("reliability-analysis", ReliabilityAnalysisReceipt),
    ("interchange", InterchangeReceipt),
)


def profile() -> dict[str, Any]:
    return {
        "schema": EXECUTION_PROVENANCE_SCHEMA,
        "workspaceVersion": "3.4.0",
        "release": "Scientific Execution & Provenance Workspace",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "referenceFirst": True,
        "executionAuthority": "workspace-postgresql-and-bounded-runtime-receipts",
        "specialistObjectAuthorityPreserved": True,
        "provenanceGraph": True,
        "datasetRevisionPinning": True,
        "modelRevisionPinning": True,
        "parameterSetRevisionPinning": True,
        "environmentFingerprintPinning": True,
        "runtimeAdapterFingerprintPinning": True,
        "outputArtifactDigestProjection": True,
        "scientificReceiptProjection": True,
        "researchSessionBindingAwareness": True,
        "immutableProvenanceSnapshots": True,
        "automaticScientificInterpretation": False,
        "automaticEvidenceRanking": False,
        "automaticDecisionAuthority": False,
    }


def _resolve_ref(ref: dict[str, Any] | None, id_key: str) -> tuple[str, int | None]:
    if not ref:
        return "", None
    object_id = str(ref.get(id_key) or "")
    revision = ref.get("revision")
    return object_id, int(revision) if revision not in (None, "") else None


def _receipt_payload(kind: str, row: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "receiptKind": kind,
        "receiptId": str(getattr(row, "receipt_id", "")),
        "executionRunId": str(getattr(row, "execution_run_id", "")),
        "jobId": str(getattr(row, "job_id", "")),
        "operation": str(getattr(row, "operation", "")),
        "createdAt": iso(getattr(row, "created_at", None)),
    }
    for source, target in (
        ("request_fingerprint", "requestFingerprint"),
        ("result_artifact_id", "resultArtifactId"),
        ("result_sha256", "resultSha256"),
        ("model_artifact_id", "modelArtifactId"),
        ("model_sha256", "modelSha256"),
        ("schema_fingerprint", "schemaFingerprint"),
        ("dataset_fingerprint", "datasetFingerprint"),
        ("status", "status"),
        ("language", "language"),
        ("runtime", "runtime"),
    ):
        value = getattr(row, source, None)
        if value not in (None, ""):
            payload[target] = value
    return payload


def _receipts(db: Session, user_key: str, run_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for kind, model in _RECEIPT_MODELS:
        rows = db.scalars(
            select(model).where(model.user_key == user_key, model.execution_run_id == run_id)
            .order_by(model.created_at.asc())
        ).all()
        items.extend(_receipt_payload(kind, row) for row in rows)
    cross_rows = db.scalars(
        select(CrossRuntimeVerificationReceipt).where(
            CrossRuntimeVerificationReceipt.user_key == user_key,
            (CrossRuntimeVerificationReceipt.original_run_id == run_id) |
            (CrossRuntimeVerificationReceipt.reproduction_run_id == run_id),
        ).order_by(CrossRuntimeVerificationReceipt.created_at.asc())
    ).all()
    for row in cross_rows:
        item = _receipt_payload("cross-runtime-verification", row)
        item["originalRunId"] = row.original_run_id
        item["reproductionRunId"] = row.reproduction_run_id
        item["classification"] = row.classification
        items.append(item)
    return items


def _resolved_inputs(db: Session, user_key: str, run: dict[str, Any]) -> dict[str, Any]:
    datasets: list[dict[str, Any]] = []
    for ref in run.get("datasetRefs") or []:
        dataset_id, revision = _resolve_ref(ref, "datasetId")
        row = get_dataset_revision(db, user_key, dataset_id, revision) if dataset_id and revision else get_dataset(db, user_key, dataset_id) if dataset_id else None
        datasets.append({"ref": ref, "resolved": dataset_metadata(row) if row is not None else None})

    model_id, model_revision = _resolve_ref(run.get("modelRef"), "modelId")
    model_row = get_model_revision(db, user_key, model_id, model_revision) if model_id and model_revision else get_model(db, user_key, model_id) if model_id else None

    parameter_id, parameter_revision = _resolve_ref(run.get("parameterSetRef"), "parameterSetId")
    parameter_row = get_parameter_set_revision(db, user_key, parameter_id, parameter_revision) if parameter_id and parameter_revision else get_parameter_set(db, user_key, parameter_id) if parameter_id else None

    environment_id, environment_revision = _resolve_ref(run.get("environmentRef"), "environmentId")
    environment_row = get_environment_revision(db, user_key, environment_id, environment_revision) if environment_id and environment_revision else get_environment(db, user_key, environment_id) if environment_id else None

    adapter_id, adapter_revision = _resolve_ref(run.get("runtimeAdapterRef"), "adapterId")
    adapter_row = get_adapter_revision(db, user_key, adapter_id, adapter_revision) if adapter_id and adapter_revision else get_adapter(db, user_key, adapter_id) if adapter_id else None

    return {
        "datasets": datasets,
        "model": {"ref": run.get("modelRef") or {}, "resolved": model_metadata(model_row) if model_row is not None else None},
        "parameterSet": {"ref": run.get("parameterSetRef") or {}, "resolved": parameter_set_metadata(parameter_row) if parameter_row is not None else None},
        "environment": {"ref": run.get("environmentRef") or {}, "resolved": environment_metadata(environment_row) if environment_row is not None else None},
        "runtimeAdapter": {"ref": run.get("runtimeAdapterRef") or {}, "resolved": adapter_metadata(adapter_row) if adapter_row is not None else None},
    }


def _binding(db: Session, user_key: str, project_id: str, run_id: str) -> dict[str, Any] | None:
    ref = f"workspace:execution-run:{run_id}"
    row = db.scalar(select(ResearchSessionObjectBinding).where(
        ResearchSessionObjectBinding.user_key == user_key,
        ResearchSessionObjectBinding.project_id == project_id,
        ResearchSessionObjectBinding.binding_type == "execution",
        ResearchSessionObjectBinding.workspace_ref == ref,
    ).limit(1))
    if row is None:
        return None
    return {
        "bindingId": row.binding_id,
        "coreSessionId": row.core_session_id,
        "coreBindingId": row.core_binding_id,
        "status": row.status,
        "workspaceRevision": row.workspace_revision,
        "workspaceFingerprint": row.workspace_fingerprint,
        "role": row.role,
        "updatedAt": iso(row.updated_at),
    }


def _graph(run: dict[str, Any], inputs: dict[str, Any], outputs: list[dict[str, Any]], receipts: list[dict[str, Any]], binding: dict[str, Any] | None) -> dict[str, Any]:
    run_id = str(run["runId"])
    nodes: list[dict[str, Any]] = [{"id": f"run:{run_id}", "kind": "execution-run", "ref": run_id, "fingerprint": run.get("reproducibilityFingerprint") or run.get("inputFingerprint") or ""}]
    edges: list[dict[str, str]] = []
    for item in inputs["datasets"]:
        ref = item["ref"]
        object_id = str(ref.get("datasetId") or "")
        if object_id:
            node_id = f"dataset:{object_id}:{ref.get('revision') or 'head'}"
            nodes.append({"id": node_id, "kind": "dataset", "ref": object_id, "revision": ref.get("revision")})
            edges.append({"from": node_id, "to": f"run:{run_id}", "relation": "consumed-by"})
    for key, kind, id_key, relation in (
        ("model", "model", "modelId", "used-by"),
        ("parameterSet", "parameter-set", "parameterSetId", "parameterized"),
        ("environment", "execution-environment", "environmentId", "executed-in"),
        ("runtimeAdapter", "runtime-adapter", "adapterId", "executed-via"),
    ):
        ref = inputs[key]["ref"]
        object_id = str(ref.get(id_key) or "")
        if object_id:
            node_id = f"{kind}:{object_id}:{ref.get('revision') or 'head'}"
            nodes.append({"id": node_id, "kind": kind, "ref": object_id, "revision": ref.get("revision")})
            edges.append({"from": node_id, "to": f"run:{run_id}", "relation": relation})
    for output in outputs:
        output_id = str(output.get("outputId") or "")
        node_id = f"output:{run_id}:{output_id}"
        nodes.append({"id": node_id, "kind": "execution-output", "ref": output_id, "artifactId": output.get("artifactId"), "sha256": output.get("sha256")})
        edges.append({"from": f"run:{run_id}", "to": node_id, "relation": "produced"})
    for receipt in receipts:
        receipt_id = str(receipt.get("receiptId") or "")
        node_id = f"receipt:{receipt.get('receiptKind')}:{receipt_id}"
        nodes.append({"id": node_id, "kind": "scientific-receipt", "ref": receipt_id, "receiptKind": receipt.get("receiptKind")})
        edges.append({"from": f"run:{run_id}", "to": node_id, "relation": "evidenced-by"})
    if binding:
        node_id = f"core-session:{binding['coreSessionId']}"
        nodes.append({"id": node_id, "kind": "platform-core-session", "ref": binding["coreSessionId"]})
        edges.append({"from": f"run:{run_id}", "to": node_id, "relation": "bound-to"})
    return {"nodes": nodes, "edges": edges, "nodeCount": len(nodes), "edgeCount": len(edges)}


def run_provenance(db: Session, user_key: str, project_id: str, run_id: str, include_events: bool = True, include_receipts: bool = True) -> dict[str, Any]:
    row = get_execution_run(db, user_key, run_id)
    if row is None:
        raise KeyError(run_id)
    run = run_metadata(row)
    if str(run.get("projectId") or "") != project_id:
        raise PermissionError(run_id)
    inputs = _resolved_inputs(db, user_key, run)
    outputs = list_run_outputs(db, user_key, run_id)
    events = list_run_events(db, user_key, run_id) if include_events else []
    receipts = _receipts(db, user_key, run_id) if include_receipts else []
    binding = _binding(db, user_key, project_id, run_id)
    graph = _graph(run, inputs, outputs, receipts, binding)
    item = {
        "schema": EXECUTION_PROVENANCE_RUN_SCHEMA,
        "projectId": project_id,
        "run": run,
        "inputs": inputs,
        "outputs": outputs,
        "events": events,
        "scientificReceipts": receipts,
        "researchSessionBinding": binding,
        "provenanceGraph": graph,
        "authority": {
            "execution": "workspace-postgresql",
            "runtimeReceipts": "workspace-bounded-runtime-receipts",
            "crossProductSession": "platform-core-v3" if binding else "unbound",
        },
    }
    item["provenanceFingerprint"] = sha256_hex(item)
    return item


def project_provenance(db: Session, user_key: str, project_id: str, limit: int = 250) -> dict[str, Any]:
    runs = list_execution_runs(db, user_key, None, project_id, limit)
    items = [run_provenance(db, user_key, project_id, str(run["runId"]), False, True) for run in runs]
    status_counts: dict[str, int] = {}
    receipt_count = 0
    bound_count = 0
    for item in items:
        status = str(item["run"].get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        receipt_count += len(item["scientificReceipts"])
        if item.get("researchSessionBinding"):
            bound_count += 1
    payload = {
        "schema": "sc-workspace-scientific-execution-provenance-project/1.0",
        "projectId": project_id,
        "executionCount": len(items),
        "receiptCount": receipt_count,
        "coreBoundExecutionCount": bound_count,
        "statusCounts": status_counts,
        "executions": items,
    }
    payload["provenanceFingerprint"] = sha256_hex(payload)
    return payload


def create_snapshot(db: Session, user_key: str, project_id: str, request: ScientificExecutionProvenanceSnapshotRequest) -> dict[str, Any]:
    if request.runId:
        provenance = run_provenance(db, user_key, project_id, request.runId, request.includeEvents, request.includeReceipts)
        run_id = request.runId
        execution_count = 1
    else:
        provenance = project_provenance(db, user_key, project_id)
        run_id = ""
        execution_count = int(provenance.get("executionCount") or 0)
    fingerprint = str(provenance.get("provenanceFingerprint") or sha256_hex(provenance))
    row = ScientificExecutionProvenanceSnapshot(
        user_key=user_key,
        snapshot_id="execution-provenance-" + uuid4().hex[:24],
        project_id=project_id,
        run_id=run_id,
        provenance_fingerprint=fingerprint,
        execution_count=execution_count,
        provenance_json=provenance,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return snapshot_metadata(row)


def snapshot_metadata(row: ScientificExecutionProvenanceSnapshot) -> dict[str, Any]:
    return {
        "schema": EXECUTION_PROVENANCE_SNAPSHOT_SCHEMA,
        "snapshotId": row.snapshot_id,
        "projectId": row.project_id,
        "runId": row.run_id,
        "provenanceFingerprint": row.provenance_fingerprint,
        "executionCount": row.execution_count,
        "createdAt": iso(row.created_at),
    }


def list_snapshots(db: Session, user_key: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(ScientificExecutionProvenanceSnapshot)
        .where(ScientificExecutionProvenanceSnapshot.user_key == user_key, ScientificExecutionProvenanceSnapshot.project_id == project_id)
        .order_by(ScientificExecutionProvenanceSnapshot.created_at.desc())
        .limit(limit)
    ).all()
    return [snapshot_metadata(row) for row in rows]
