"""SC-NB-01 verified cell-output -> cell-input binding.

A notebook cell may consume the result of an upstream cell (``payload.upstreamInput``) instead of
values typed by the caller. The worker resolves every reference server-side, from the same
server-created execution plan, and refuses unless the upstream cell:

* is a declared dependency of this cell and belongs to the same plan, notebook revision and owner;
* ran as an executed-verified ExecutionRun (succeeded, runtime receipt, output == receipt);
* has verified input lineage itself (so the chain bottoms out in pinned dataset bytes);
* still matches its immutable notebook cell (server cell hash) and was not withdrawn;
* produced a result ArtifactRevision whose stored bytes re-hash to the receipt's SHA-256.

The runtime payload is then derived from those bytes by a declared deterministic transform. Values
the caller sends next to ``upstreamInput`` (candidates, scores, rows, matrices) are refused. The
binding records the full chain: upstream runs, cell hashes, models, environments and datasets.
"""
from __future__ import annotations

import json
import math
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .input_integrity import VERIFIED, _refuse
from .models import ArtifactRevision, ExecutionRunOutput, NotebookRevision, ResearchExportWithdrawal
from .object_store import read_artifact_content
from .registry import get_execution_run, get_model_revision
from .utils import sha256_hex

BINDING_SCHEMA = "sc-workspace-upstream-cell-binding/1.0"
KIND = "upstream-cell"
ROLES = {"primary", "cross-check"}
TRANSFORMS = {"linear-scenario-scores"}
# Caller-supplied intermediates that an upstream-bound cell must derive instead.
FORBIDDEN_INLINE = {"candidates", "scores", "scenarios", "rows", "Q", "c", "values", "datasetInput"}
MAX_UPSTREAM = 8


def parse_spec(cid: str, spec: Any, depends: list[str]) -> list[dict[str, str]]:
    """Validates ``upstreamInput`` at plan time; returns its cell references. Raises 400 on malformed specs."""
    from fastapi import HTTPException

    def bad(code: str, **kw):
        return HTTPException(status_code=400, detail={"code": code, "cellId": cid, **kw})

    if not isinstance(spec, dict) or not isinstance(spec.get("cells"), list) or not spec["cells"]:
        raise bad("upstream-input-malformed")
    refs = []
    for ref in spec["cells"][:MAX_UPSTREAM + 1]:
        if not isinstance(ref, dict) or not str(ref.get("cellId") or "").strip() or ref.get("role", "primary") not in ROLES:
            raise bad("upstream-input-malformed")
        refs.append({"cellId": str(ref["cellId"]).strip(), "role": ref.get("role", "primary")})
    if len(refs) > MAX_UPSTREAM or len({r["cellId"] for r in refs}) != len(refs):
        raise bad("upstream-input-malformed", detail="at most 8 distinct upstream cells")
    if [r["role"] for r in refs].count("primary") != 1:
        raise bad("upstream-input-needs-one-primary")
    undeclared = sorted({r["cellId"] for r in refs} - set(depends))
    if undeclared:
        raise bad("upstream-input-not-declared-dependency", cellIds=undeclared)
    transform = spec.get("transform")
    if not isinstance(transform, dict) or transform.get("kind") not in TRANSFORMS:
        raise bad("upstream-transform-unsupported", supported=sorted(TRANSFORMS))
    return refs


# ---------------------------------------------------------------------------
# Deterministic transforms


def _num(v: Any) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def linear_scenario_scores(values: dict[str, float], uncertainty: dict[str, float], t: dict[str, Any]) -> dict[str, Any]:
    """Scenario scores from a fitted line: score(rate, s) = intercept + s * rate, with s in
    {slope - k*SE, slope, slope + k*SE}. Design parameters (rates, k, probabilities) are declared in the cell."""
    names = t.get("names") or {}
    i_name, s_name = str(names.get("intercept", "intercept")), str(names.get("slope", "slope"))
    intercept, slope = _num(values.get(i_name)), _num(values.get(s_name))
    if intercept is None or slope is None:
        raise _refuse("upstream-values-missing", required=[i_name, s_name])
    se = _num(uncertainty.get(s_name))
    k = _num(t.get("uncertaintyMultiplier", 2))
    if se is None or se < 0 or k is None or k < 0:
        raise _refuse("upstream-uncertainty-missing", required=s_name)
    rates = t.get("rates")
    if not isinstance(rates, list) or not 1 <= len(rates) <= 64 or any(_num(r) is None for r in rates):
        raise _refuse("transform-rates-invalid")
    probs = t.get("scenarioProbabilities", [0.25, 0.5, 0.25])
    if not isinstance(probs, list) or len(probs) != 3 or any(_num(p) is None or p < 0 for p in probs) or abs(sum(probs) - 1) > 1e-9:
        raise _refuse("transform-probabilities-invalid")
    direction = t.get("direction", "maximize")
    if direction not in ("maximize", "minimize"):
        raise _refuse("transform-direction-invalid")
    prefix, unit = str(t.get("candidatePrefix", "rate")), str(t.get("candidateUnit", ""))
    slopes = {"slope-low": slope - k * se, "slope-central": slope, "slope-high": slope + k * se}

    def cid(r: float) -> str:
        label = str(int(r)) if float(r).is_integer() else repr(float(r))
        return "-".join(x for x in (prefix, label, unit) if x)

    return {"direction": direction,
            "scenarios": [{"id": n, "probability": p} for n, p in zip(slopes, probs)],
            "candidates": [{"id": cid(r), "scores": [round(intercept + s * r, 9) for s in slopes.values()]} for r in rates]}


# ---------------------------------------------------------------------------
# Resolution


def _upstream_run(db: Session, user_key: str, plan, step: dict[str, Any], ref: dict[str, str]) -> tuple[dict, Any]:
    up_step = next((s for s in (plan.steps_json or []) if s.get("cellId") == ref["cellId"]), None)
    if up_step is None:
        raise _refuse("upstream-cell-not-in-plan", cellId=ref["cellId"], planId=plan.plan_id)
    if ref["cellId"] not in (step.get("dependsOnStepIds") or []):
        raise _refuse("upstream-cell-not-declared-dependency", cellId=ref["cellId"])
    run = get_execution_run(db, user_key, str(up_step.get("runId") or ""))  # owner-scoped lookup
    if run is None:
        raise _refuse("upstream-run-not-found", cellId=ref["cellId"])
    return up_step, run


def _verified_result(db: Session, user_key: str, cell_id: str, run) -> tuple[dict[str, Any], dict[str, Any], ArtifactRevision]:
    from .notebook_orchestration import verified_cell_run
    from .research_exports import _verification

    if db.get(ResearchExportWithdrawal, {"user_key": user_key, "run_id": run.run_id}):
        raise _refuse("upstream-run-withdrawn", cellId=cell_id, runId=run.run_id)
    outputs = list(db.scalars(select(ExecutionRunOutput).where(
        ExecutionRunOutput.user_key == user_key, ExecutionRunOutput.run_id == run.run_id)).all())
    ver = _verification(db, user_key, run, outputs)
    if ver["status"] != "executed-verified":
        raise _refuse("upstream-run-not-verified", cellId=cell_id, runId=run.run_id, status=ver["status"])
    if ver["inputLineage"] != VERIFIED:
        raise _refuse("upstream-lineage-unverified", cellId=cell_id, runId=run.run_id, inputLineage=ver["inputLineage"])
    cell = verified_cell_run(db, user_key, run)
    if not cell or not cell.get("verified"):
        raise _refuse("upstream-cell-unverifiable", cellId=cell_id, runId=run.run_id)
    receipt = ver["runtimeReceipts"][0]
    snapshot = db.scalars(select(ArtifactRevision).where(
        ArtifactRevision.user_key == user_key, ArtifactRevision.artifact_id == receipt["resultArtifactId"],
        ArtifactRevision.sha256 == receipt["resultSha256"]).order_by(ArtifactRevision.revision.desc())).first()
    if snapshot is None:
        raise _refuse("upstream-result-snapshot-missing", cellId=cell_id, sha256=receipt["resultSha256"])
    try:
        read_artifact_content(snapshot)  # re-hash the stored bytes
    except Exception as exc:
        raise _refuse("upstream-result-integrity-failed", cellId=cell_id, artifactId=snapshot.artifact_id) from exc
    return ver, cell, snapshot


def _values(db: Session, user_key: str, cell_id: str, run, snapshot: ArtifactRevision) -> dict[str, Any]:
    from .research_exports import extract_result_values

    ref = run.model_ref or {}
    model = get_model_revision(db, user_key, ref.get("modelId") or "", ref.get("revision") or 0) if ref.get("modelId") else None
    mapping = ((model.metadata_json or {}) if model is not None else {}).get("researchResultValues") or {}
    if not mapping:
        raise _refuse("upstream-model-declares-no-result-values", cellId=cell_id,
                      detail="the upstream cell's modelRef must declare researchResultValues")
    out = extract_result_values(mapping, json.loads(read_artifact_content(snapshot)))
    if out.get("error") or not out.get("values"):
        raise _refuse("upstream-values-unextractable", cellId=cell_id, error=out.get("error"))
    return out


def _chain_entry(cell_id: str, role: str, run, ver: dict, cell: dict, snapshot: ArtifactRevision, values: dict) -> dict[str, Any]:
    receipt = ver["runtimeReceipts"][0]
    return {
        "cellId": cell_id, "role": role, "runId": run.run_id, "jobId": run.job_id,
        "cellSha256": cell.get("cellSha256"), "language": cell.get("language"), "operation": run.operation,
        "modelRef": run.model_ref or {}, "parameterSetRef": run.parameter_set_ref or {},
        "environmentFingerprint": run.environment_fingerprint, "inputFingerprint": run.input_fingerprint,
        "reproducibilityFingerprint": run.reproducibility_fingerprint,
        "runtime": receipt["runtime"], "runtimeReceiptId": receipt["receiptId"],
        "resultArtifactId": snapshot.artifact_id, "resultArtifactRevision": snapshot.revision,
        "resultSha256": snapshot.sha256, "valuesSha256": sha256_hex(values),
        "inputLineage": ver["inputLineage"], "inputBindings": ver["inputBindings"],
    }


def flatten_datasets(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every pinned dataset revision under a list of bindings (dataset or upstream-cell), de-duplicated."""
    out: dict[tuple, dict[str, Any]] = {}
    for b in bindings or []:
        if b.get("kind") == KIND:
            for d in b.get("datasets") or []:
                out[(d["datasetId"], d["datasetRevision"], d["artifactSha256"])] = d
        elif b.get("datasetId"):
            d = {k: b.get(k) for k in ("datasetId", "datasetRevision", "artifactId", "artifactRevision", "artifactSha256")}
            out[(d["datasetId"], d["datasetRevision"], d["artifactSha256"])] = d
    return [out[k] for k in sorted(out, key=lambda k: (str(k[0]), k[1] or 0, str(k[2])))]


def resolve_upstream_input(db: Session, user_key: str, payload: dict[str, Any], run_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Returns (runtime payload, binding). Raises 409 on any binding, integrity or ownership failure."""
    from .notebook_orchestration import get_plan

    spec = payload.get("upstreamInput")
    inline = sorted(FORBIDDEN_INLINE & set(payload))
    if inline:
        raise _refuse("upstream-input-and-inline-values", keys=inline,
                      detail="an upstream-bound cell derives these values; it does not accept them from the caller")
    if not isinstance(spec, dict):
        raise _refuse("upstream-input-malformed")
    run = get_execution_run(db, user_key, run_id) if run_id else None
    claim = (run.environment_json or {}).get("notebookCell") if run is not None else None
    if not isinstance(claim, dict):
        raise _refuse("upstream-input-requires-notebook-plan", detail="only server-planned notebook cells can bind upstream outputs")
    plan = get_plan(db, user_key, str(claim.get("planId") or ""))
    step = next((s for s in (plan.steps_json or []) if s.get("runId") == run.run_id), None) if plan else None
    if step is None or step.get("cellId") != claim.get("cellId"):
        raise _refuse("upstream-input-run-not-in-plan", runId=run_id)
    revision = db.get(NotebookRevision, {"user_key": user_key, "notebook_id": plan.notebook_id, "revision": plan.notebook_revision})
    if revision is None:
        raise _refuse("upstream-notebook-revision-missing")
    try:
        refs = parse_spec(step["cellId"], spec, step.get("dependsOnStepIds") or [])
    except Exception as exc:  # plan-time validation should already have caught this
        raise _refuse("upstream-input-malformed") from exc
    pinned = step.get("upstreamCellSha256") or {}
    chain, extracted = [], {}
    for ref in refs:
        up_step, up_run = _upstream_run(db, user_key, plan, step, ref)
        ver, cell, snapshot = _verified_result(db, user_key, ref["cellId"], up_run)
        if cell.get("planId") != plan.plan_id or cell.get("notebookRevision") != plan.notebook_revision:
            raise _refuse("upstream-cell-from-other-plan", cellId=ref["cellId"])
        if pinned.get(ref["cellId"]) not in (None, cell.get("cellSha256")) or up_step.get("cellSha256") != cell.get("cellSha256"):
            raise _refuse("upstream-cell-modified", cellId=ref["cellId"])
        values = _values(db, user_key, ref["cellId"], up_run, snapshot)
        extracted[ref["cellId"]] = values
        chain.append(_chain_entry(ref["cellId"], ref["role"], up_run, ver, cell, snapshot, values))
    transform = spec["transform"]
    primary = next(c for c in chain if c["role"] == "primary")
    p_vals = extracted[primary["cellId"]]
    tolerance = _num(transform.get("crossCheckTolerance", 1e-6))
    cross = []
    for c in chain:
        if c["role"] != "cross-check":
            continue
        other = extracted[c["cellId"]]["values"]
        shared = sorted(set(other) & set(p_vals["values"]))
        if not shared:
            raise _refuse("upstream-cross-check-no-shared-values", cellId=c["cellId"])
        diffs = {k: abs(other[k] - p_vals["values"][k]) for k in shared}
        worst = max(diffs.values())
        if tolerance is None or worst > tolerance * max(1.0, *(abs(p_vals["values"][k]) for k in shared)):
            raise _refuse("upstream-cross-check-failed", cellId=c["cellId"], maxAbsDifference=worst, tolerance=tolerance)
        cross.append({"cellId": c["cellId"], "values": shared, "maxAbsDifference": worst, "tolerance": tolerance})
    derived = linear_scenario_scores(p_vals["values"], (p_vals.get("uncertainty") or {}).get("values") or {}, transform)
    runtime_payload = {k: v for k, v in payload.items() if k != "upstreamInput"}
    runtime_payload.update(derived)
    binding = {
        "schema": BINDING_SCHEMA, "kind": KIND, "lineage": VERIFIED,
        "planId": plan.plan_id, "notebookId": plan.notebook_id, "notebookRevision": plan.notebook_revision,
        "notebookPackageSha256": revision.fingerprint, "cellId": step["cellId"], "cellSha256": step.get("cellSha256"),
        "upstream": chain, "crossChecks": cross, "transform": transform,
        "upstreamValues": {c: v["values"] for c, v in sorted(extracted.items())},
        "derivedPayloadSha256": sha256_hex(derived),
        "datasets": flatten_datasets([b for c in chain for b in c["inputBindings"]]),
    }
    binding["chainSha256"] = sha256_hex({k: binding[k] for k in ("upstream", "transform", "derivedPayloadSha256", "datasets")})
    return runtime_payload, binding
