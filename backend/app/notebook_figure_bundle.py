"""SC-FIG-02B: a Vega-Lite figure package from one verified Workspace notebook cell run.

The result of the latest ``executed-verified`` run of a cell in an immutable notebook revision is
projected into rows and returned as an ``sc.figure-bundle.v1`` bundle plus one Vega-Lite view
(``usermeta.sc`` profile ``sc-vega-lite-v1``), which Lab Graph Studio verifies and renders. Nothing
is stored: Workspace stays the notebook and run authority, Lab the renderer, Research the registry.

Scientific rules:

* Only ``modelled`` (computed from specified inputs) or ``hypothetical`` figures. A notebook
  computation is never presented as observed or literature-derived evidence.
* The dataset hash in the view is the canonical hash of the projected rows. It appears as the output
  of a second calculation reference that names the run, the projection and any uncertainty bound
  computation, so every number can be traced to the receipt-verified result bytes.
* Input datasets become source references. Their licence and quality stay ``pending``: holding a
  dataset is not a right to publish it.
* Every encoded field needs a label and a unit; declared uncertainty is drawn.

The package is deterministic for a given revision, run and request, so its hashes can be compared.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

from .config import get_settings
from .db import session_scope
from .notebook_export import _cell_runs, _latest_verified, load_revision
from .notebook_orchestration import cell_sha256
from .object_store import get_artifact, read_artifact_content
from .security import ServiceIdentity, require_service_identity

BUNDLE_SCHEMA = "sc.figure-bundle.v1"
PACKAGE_SCHEMA = "sc-workspace-figure-package/1.0"
PROFILE = "sc-vega-lite-v1"
VL5 = "application/vnd.vegalite.v5+json"
VL5_SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json"
RENDERER_VERSION = "vega-lite 6.5.0; vega 6.4.0"
MEASUREMENT = {"modelled": "computed-from-specified-inputs", "hypothetical": "hypothetical-only"}
MAX_ROWS = 20000
MAX_RESULT_BYTES = 4 * 1024 * 1024
FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
FIGURE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,95}$")
EVIDENCE_FIELD = "evidenceClass"
LOWER, UPPER = "lower", "upper"
KIND_TEXT = {"sd": "± one standard deviation", "se": "± one standard error", "ci90": "90% confidence interval",
             "ci95": "95% confidence interval", "pi95": "95% prediction interval", "range": "range"}

router = APIRouter(prefix="/v1/notebooks", tags=["notebook-figure-bundle"])


class FieldSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str = Field(pattern=FIELD.pattern)
    label: str = Field(min_length=1, max_length=120)
    unit: str = Field(min_length=1, max_length=40, description='"1" for dimensionless, "category" for labels')
    type: Literal["quantitative", "nominal", "ordinal", "temporal"] = "quantitative"


class UncertaintySpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["none", "sd", "se", "ci90", "ci95", "pi95", "range"] = "none"
    lowerField: str | None = Field(default=None, pattern=FIELD.pattern)
    upperField: str | None = Field(default=None, pattern=FIELD.pattern)
    spreadField: str | None = Field(default=None, pattern=FIELD.pattern)
    multiplier: float | None = Field(default=None, gt=0, le=10)
    statement: str = Field(default="", max_length=400)


class FigureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    figureId: str = Field(pattern=FIGURE_ID.pattern)
    title: str = Field(min_length=8, max_length=200)
    rowsPath: str = Field(default="", max_length=120, pattern=r"^[A-Za-z0-9_.]*$")
    mark: Literal["point", "line", "bar"] = "point"
    x: FieldSpec
    y: FieldSpec
    color: FieldSpec | None = None
    uncertainty: UncertaintySpec = UncertaintySpec()
    evidenceClass: Literal["modelled", "hypothetical"]
    caption: str = Field(min_length=15, max_length=600)
    altText: str = Field(min_length=15, max_length=600)
    interpretation: str = Field(min_length=8, max_length=1200)
    limitations: list[str] = Field(min_length=1, max_length=12)
    doNotInfer: list[str] = Field(default_factory=lambda: ["measured evidence", "publication approval"], max_length=12)


def canonical(value: Any) -> str:
    """The canonical JSON Lab hashes (sorted keys, no spaces, UTF-8)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _refuse(code: str, message: str, **extra: Any) -> HTTPException:
    return HTTPException(status_code=422, detail={"code": code, "message": message, **extra})


POLYGLOT_RESULT = "sc-workspace-polyglot-result/1.0"


def runtime_result(result: Any) -> Any:
    """What the cell's code returned: the runtime result inside a polyglot result envelope."""
    if isinstance(result, dict) and result.get("schema") == POLYGLOT_RESULT:
        remote = ((result.get("result") or {}).get("remote") or {})
        if "result" not in remote:
            raise _refuse("figure-rows-not-found", "The run result envelope carries no runtime result.")
        return remote["result"]
    return result


def _rows(result: Any, path: str) -> list[dict[str, Any]]:
    node = runtime_result(result)
    for part in [p for p in path.split(".") if p]:
        if not isinstance(node, dict) or part not in node:
            raise _refuse("figure-rows-not-found", f"The run result has no '{path}'.")
        node = node[part]
    if not isinstance(node, list) or not node or len(node) > MAX_ROWS or not all(isinstance(r, dict) for r in node):
        raise _refuse("figure-rows-invalid", f"'{path or 'result'}' must be a list of 1 to {MAX_ROWS} records.")
    return node


def _number(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise _refuse("figure-field-not-numeric", f"Field '{field}' must be numeric or null in every row.")
    return value


def _round(value: float) -> float:
    return float(f"{value:.12g}")


def project_rows(rows: list[dict[str, Any]], req: FigureRequest) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    """Rows for the view (declared fields, computed bounds, evidence class) and the projection description."""
    u = req.uncertainty
    channels = [req.x, req.y] + ([req.color] if req.color else [])
    names = [c.field for c in channels]
    if len(set(names)) != len(names) or EVIDENCE_FIELD in names or {LOWER, UPPER} & set(names):
        raise _refuse("figure-fields-invalid", "Encoded fields must be distinct and must not be named "
                      f"'{EVIDENCE_FIELD}', '{LOWER}' or '{UPPER}'.")
    if req.y.type != "quantitative":
        raise _refuse("figure-fields-invalid", "The y field must be quantitative.")
    bounds = u.kind != "none"
    if bounds and not ((u.lowerField and u.upperField and not u.spreadField and u.multiplier is None)
                       or (u.spreadField and u.multiplier and not u.lowerField and not u.upperField)):
        raise _refuse("figure-uncertainty-invalid", "Give either lowerField and upperField, or spreadField and multiplier.")
    if not bounds and (u.lowerField or u.upperField or u.spreadField or u.multiplier):
        raise _refuse("figure-uncertainty-invalid", "Uncertainty kind 'none' takes no fields.")
    out = []
    for row in rows:
        r: dict[str, Any] = {}
        for c in channels:
            if c.field not in row:
                raise _refuse("figure-field-missing", f"Field '{c.field}' is missing from a result row.")
            v = row[c.field]
            if c.type == "quantitative":
                v = _number(v, c.field)
            elif isinstance(v, bool) or (v is not None and not isinstance(v, (str, int, float))):
                raise _refuse("figure-field-invalid", f"Field '{c.field}' must hold text or numbers.")
            r[c.field] = v
        if bounds:
            y = r[req.y.field]
            if u.spreadField:
                s = _number(row.get(u.spreadField), u.spreadField)
                lo, hi = (None, None) if y is None or s is None else (_round(y - u.multiplier * s), _round(y + u.multiplier * s))
            else:
                lo, hi = _number(row.get(u.lowerField), u.lowerField), _number(row.get(u.upperField), u.upperField)
            if lo is not None and hi is not None and lo > hi:
                raise _refuse("figure-uncertainty-invalid", "A lower bound exceeds its upper bound.")
            r[LOWER], r[UPPER] = lo, hi
        r[EVIDENCE_FIELD] = req.evidenceClass
        out.append(r)
    if bounds and u.spreadField:
        k = repr(u.multiplier)
        rule = f"{LOWER} = {req.y.field} − {k} × {u.spreadField}, {UPPER} = {req.y.field} + {k} × {u.spreadField}"
    elif bounds:
        rule = f"{LOWER} = {u.lowerField}, {UPPER} = {u.upperField}"
    else:
        rule = "no uncertainty bounds"
    statement = u.statement or (f"{KIND_TEXT[u.kind]} from the run result ({rule})." if bounds else
                                "The run result reports no uncertainty for these values.")
    meta = {"kind": u.kind, "statement": statement}
    if bounds:
        meta.update(lowerField=LOWER, upperField=UPPER)
    method = (f"Workspace figure projection: rows from the runtime result{'.' + req.rowsPath if req.rowsPath else ''}; "
              f"fields {', '.join(names)}; {rule}; {EVIDENCE_FIELD} = {req.evidenceClass}")
    return out, meta, method


def build_view(req: FigureRequest, rows: list[dict[str, Any]], unc: dict[str, Any], dataset_id: str, dataset_sha: str) -> dict[str, Any]:
    y_title = req.y.label if req.y.unit in ("1", "category") else f"{req.y.label} ({req.y.unit})"
    enc = {"x": {"field": req.x.field, "type": req.x.type}, "y": {"field": req.y.field, "type": "quantitative"}}
    if req.color:
        enc["color"] = {"field": req.color.field, "type": req.color.type}
    layers = []
    fields = {c.field: {"label": c.label, "unit": c.unit} for c in (req.x, req.y, req.color) if c}
    fields[EVIDENCE_FIELD] = {"label": "Evidence class", "unit": "category"}
    if unc["kind"] != "none":
        # Caps only on a continuous x: on a categorical band they would span the whole category.
        style = {"opacity": 0.3} if req.mark == "line" else {"ticks": req.x.type in ("quantitative", "temporal")}
        band = {"mark": {"type": "errorband" if req.mark == "line" else "errorbar", **style},
                "encoding": {"x": dict(enc["x"]), "y": {"field": LOWER, "type": "quantitative", "title": y_title}, "y2": {"field": UPPER},
                             **({"color": dict(enc["color"])} if req.color else {})}}
        layers.append(band)
        bound_label = KIND_TEXT[unc["kind"]]
        fields[LOWER] = {"label": f"Lower bound ({bound_label})", "unit": req.y.unit}
        fields[UPPER] = {"label": f"Upper bound ({bound_label})", "unit": req.y.unit}
    # SC-SCI-02: hovering a mark names every value with its unit (Vega's built-in tooltip; no interaction params).
    types = {req.x.field: req.x.type, req.y.field: "quantitative", LOWER: "quantitative", UPPER: "quantitative",
             **({req.color.field: req.color.type} if req.color else {})}
    tip = [{"field": f, "type": types.get(f, "nominal"), "title": d["label"] if d["unit"] in ("1", "category") else f"{d['label']} ({d['unit']})"}
           for f, d in fields.items()]
    layers.append({"mark": {"type": req.mark, **({"filled": True, "size": 60} if req.mark == "point" else {})}, "encoding": {**enc, "tooltip": tip}})
    return {
        "$schema": VL5_SCHEMA, "width": 560, "height": 320, "title": req.title,
        "data": {"values": rows},
        "layer": layers,
        "usermeta": {"sc": {"profile": PROFILE, "datasetId": dataset_id, "datasetSha256": dataset_sha,
                            "evidenceField": EVIDENCE_FIELD, "fields": fields, "uncertainty": unc}},
    }


def _sources(verification: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    sources, lineage = [], []
    verified = verification.get("inputLineage") == "artifact-bound-verified"
    for b in verification.get("inputBindings") or []:
        if b.get("datasetId"):
            sid = f"workspace-dataset:{b['datasetId']}@r{b.get('datasetRevision')}"
            src = {"sourceId": sid, "provider": "Sustainable Catalyst Workspace dataset",
                   "identityStatus": "source-hash-verified" if verified and b.get("artifactSha256") else "source-identified",
                   "qualityStatus": "pending", "licenceStatus": "pending",
                   "notes": "Licence and quality are not inferred from possession of the dataset."}
            if b.get("artifactSha256"):
                src["sha256"] = b["artifactSha256"]
            if sid not in [s["sourceId"] for s in sources]:
                sources.append(src)
        elif b.get("cellId"):
            lineage.append(f"workspace-notebook-cell:{b.get('notebookId')}@r{b.get('notebookRevision')}#{b.get('cellId')}")
    return sources, lineage


def build_package(rev: Any, cell_id: str, cell_sha: str, ev: dict[str, Any], result: Any, req: FigureRequest,
                  environment: str = "local-review") -> dict[str, Any]:
    v = ev["verification"]
    receipt = v["runtimeReceipts"][0]
    run = ev["_run"]
    sources, upstream = _sources(v)
    if not sources:
        raise _refuse("figure-no-source", "The run has no pinned input dataset to cite; a figure needs at least one source.")
    rows, unc, method = project_rows(_rows(result, req.rowsPath), req)
    dataset_sha = canonical_sha256(rows)
    run_ref = f"workspace-run:{ev['runId']}"
    dataset_id = f"{run_ref}/{req.rowsPath or 'result'}"
    view = build_view(req, rows, unc, dataset_id, dataset_sha)
    view_text = json.dumps(view, indent=1, ensure_ascii=False, allow_nan=False) + "\n"
    view_sha = canonical_sha256(view)
    finished = run.finished_at or run.created_at
    if finished.tzinfo is None:
        finished = finished.replace(tzinfo=timezone.utc)
    generated = finished.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    calcs = [
        {"system": "other", "runRef": run_ref,
         "method": f"Workspace notebook {rev.notebook_id} r{rev.revision} cell {cell_id} (sha256 {cell_sha}); "
                   f"{receipt.get('language')} {receipt.get('runtime')} {receipt.get('operation')}; receipt {receipt['receiptId']}",
         "outputSha256": receipt["resultSha256"], "assumptionRefs": []},
        {"system": "other", "runRef": f"workspace-figure-projection:{ev['runId']}", "method": method,
         "outputSha256": dataset_sha, "assumptionRefs": [run_ref]},
    ]
    provenance = {"authorityOwner": "workspace", "sourceSnapshotIds": [s["sourceId"] for s in sources],
                  "generationRunId": ev["runId"], "generatedAt": generated,
                  # A verified run is not a replay: reproducibility stays untested until one is recorded.
                  "reproducibility": "not-tested",
                  "lineageRefs": [f"workspace-receipt:{receipt['receiptId']}",
                                  f"workspace-notebook-cell:{rev.notebook_id}@r{rev.revision}#{cell_id}", *upstream]}
    if re.fullmatch(r"[0-9a-f]{64}", run.input_fingerprint or ""):
        provenance["inputManifestSha256"] = run.input_fingerprint
    bundle = {
        "schema": BUNDLE_SCHEMA, "figureId": req.figureId, "version": 1, "title": req.title,
        "project": {"projectRef": f"workspace-project:{rev.project_id or run.project_id}", "ownerScope": "authenticated",
                    "environment": environment},
        "publication": {"kind": "none", "target": "unassigned", "bindingStatus": "unbound"},
        "evidenceClass": req.evidenceClass, "figureType": "evidence-chart",
        "sourceRefs": sources, "calculationRefs": calcs,
        "scientificContext": {"interpretation": req.interpretation, "limitations": req.limitations,
                              "measurementStatus": MEASUREMENT[req.evidenceClass], "units": req.y.unit,
                              "uncertaintyNotation": unc["statement"], "claimIds": [], "doNotInfer": req.doNotInfer},
        "rendering": {"profileId": "sc-institutional-research-v1", "renderer": "vega-lite", "rendererVersion": RENDERER_VERSION,
                      "caption": req.caption, "altText": req.altText, "palette": "colorblind-safe",
                      "accessibilityReview": "pending", "visualizationSpecSha256": view_sha},
        "artifacts": [{"format": "json", "artifactRef": f"sc://workspace/figure/{req.figureId}/{view_sha}.json",
                       "sha256": view_sha, "mediaType": VL5, "width": 560, "height": 320, "status": "local-review", "revision": 1}],
        "provenance": provenance,
        "review": {"scientific": "pending", "visual": "pending", "rights": "pending", "sourceIntegrity": "pending",
                   "publication": "pending"},
    }
    bundle_text = json.dumps(bundle, indent=1, ensure_ascii=False, allow_nan=False) + "\n"
    bundle_sha = hashlib.sha256(bundle_text.encode("utf-8")).hexdigest()
    return {
        "schema": PACKAGE_SCHEMA, "bundleSha256": bundle_sha, "figureId": req.figureId,
        "notebook": {"notebookId": rev.notebook_id, "revision": rev.revision, "cellId": cell_id, "cellSha256": cell_sha},
        "run": {"runId": ev["runId"], "receiptId": receipt["receiptId"], "resultSha256": receipt["resultSha256"],
                "verification": v["status"], "inputLineage": v.get("inputLineage")},
        "files": [
            {"name": f"{req.figureId}.bundle.json", "role": "bundle", "mediaType": "application/json",
             "sha256": bundle_sha, "text": bundle_text},
            {"name": f"{req.figureId}.vega-lite.json", "role": "view", "mediaType": VL5,
             "sha256": hashlib.sha256(view_text.encode("utf-8")).hexdigest(), "canonicalSha256": view_sha, "text": view_text},
        ],
        "stored": False, "published": False,
    }


@router.post("/{notebook_id}/revisions/{revision}/cells/{cell_id}/figure-bundle")
def figure_bundle_route(notebook_id: str, revision: int, cell_id: str, req: FigureRequest,
                        identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        rev = load_revision(db, identity.user_key, notebook_id, revision)
        cells = [c for c in ((rev.package or {}).get("notebook") or {}).get("cells") or [] if c.get("id") == cell_id]
        if not cells or cells[0].get("type") != "code":
            raise HTTPException(status_code=404, detail="Workspace notebook cell not found.")
        sha = cell_sha256(cells[0])
        ev = _latest_verified(db, identity.user_key, _cell_runs(db, identity.user_key, rev).get(cell_id, []), sha)
        if ev is None:
            raise _refuse("figure-run-not-verified", "This cell has no executed-verified run for this revision.")
        receipt = ev["verification"]["runtimeReceipts"][0]
        art = get_artifact(db, identity.user_key, receipt["resultArtifactId"])
        if art is None or art.sha256 != receipt["resultSha256"] or art.bytes > MAX_RESULT_BYTES:
            raise _refuse("figure-result-unavailable", "The verified run result is unavailable or too large.")
        raw = read_artifact_content(art)
        if hashlib.sha256(raw).hexdigest() != receipt["resultSha256"]:
            raise _refuse("figure-result-unavailable", "The run result bytes no longer match the receipt.")
        env = get_settings().environment
        package = build_package(rev, cell_id, sha, ev, json.loads(raw), req,
                                environment=env if env in ("production", "staging") else "local-review")
    body = (json.dumps(package, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    return Response(content=body, media_type="application/json", headers={
        "X-SC-Figure-Bundle-Sha256": package["bundleSha256"], "Cache-Control": "no-store"})
