"""SC-SCI-01 — Research notebook workspace (owner-facing Workspace page).

A same-origin page over the existing authenticated notebook, dataset, model, execution-plan, export and
figure-package APIs: create and reopen a notebook, attach a byte-pinned dataset, add R and Julia cells,
run them on the governed runtimes, pass verified results between dependent cells, see which results are
stale after an upstream edit, and export Jupyter, Quarto and reproducibility packages. The page holds no
credential (SC Identity session cookie, same origin) and decides nothing: every state shown comes from the
API, and runtimes execute declared, bounded operations only (cell text documents the method).

``GET /v1/notebooks/{id}/cell-status`` is the one read this page adds. For each code cell of the notebook
head it reports the latest server-planned run, its receipt verification (the same rules as Research
exports), the values its model revision declares, and whether that result still describes the head
(``cell_currency``). It never re-runs or re-verifies anything beyond those existing checks.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select

from .approval_desk import HEADERS
from .db import session_scope
from .execution_provenance import run_provenance
from .models import NotebookExecutionPlan
from .notebook_export import _run_evidence
from .notebook_orchestration import cell_sha256, verified_cell_run
from .object_store import get_artifact, read_artifact_content
from .repository import get_notebook
from .research_exports import extract_result_values
from .security import ServiceIdentity, require_service_identity

STATUS_SCHEMA = "sc-workspace-notebook-cell-status/1.0"
MAX_RESULT_BYTES = 4 * 1024 * 1024
ACTIVE = {"pending", "queued", "running", "ready", "dispatched"}

page_router = APIRouter(prefix="/v1/desk", tags=["SC-SCI-01 notebook workspace"])
status_router = APIRouter(prefix="/v1/notebooks", tags=["SC-SCI-01 notebook workspace"])

STATIC = Path(__file__).resolve().parent / "static" / "notebook_desk"
ASSETS = {"notebook-desk.js": "text/javascript; charset=utf-8", "notebook-desk.css": "text/css; charset=utf-8",
          "notebook-recipes.js": "text/javascript; charset=utf-8"}


def _file(name: str, media_type: str) -> Response:
    return Response((STATIC / name).read_bytes(), media_type=media_type, headers=HEADERS)


@page_router.get("/notebooks")
def notebook_desk_page():
    return _file("index.html", "text/html; charset=utf-8")


@page_router.get("/notebook-assets/{name}")
def notebook_desk_asset(name: str):
    if name not in ASSETS:
        raise HTTPException(status_code=404, detail="Not Found")
    return _file(name, ASSETS[name])


def _values(db, user_key: str, run, verification: dict[str, Any]) -> dict[str, Any] | None:
    """The model revision's declared values from the receipt-verified result bytes; None when not verified."""
    if verification.get("status") != "executed-verified" or not verification.get("runtimeReceipts"):
        return None
    receipt = verification["runtimeReceipts"][0]
    art = get_artifact(db, user_key, receipt["resultArtifactId"])
    if art is None or art.sha256 != receipt["resultSha256"] or art.bytes > MAX_RESULT_BYTES:
        return {"values": {}, "error": "result unavailable"}
    provenance = run_provenance(db, user_key, run.project_id, run.run_id, True, True)
    model = ((provenance.get("inputs") or {}).get("model") or {}).get("resolved") or {}
    mapping = (model.get("metadata") or {}).get("researchResultValues") or {}
    if not mapping:
        return {"values": {}, "error": "the model revision declares no result values"}
    out = extract_result_values(mapping, json.loads(read_artifact_content(art)))
    out["sourceArtifactSha256"] = art.sha256
    return out


def _state(step: dict[str, Any] | None, plan_status: str, verification: dict[str, Any] | None,
           claim: dict[str, Any] | None) -> str:
    """One label per cell: not-run, running, failed, unverified, stale or verified."""
    if step is None:
        return "not-run"
    if not step.get("runId") or (verification or {}).get("status") == "incomplete":
        if plan_status in ACTIVE:
            return "running"
        return "failed" if step.get("runId") else "not-run"  # never dispatched: an upstream step stopped the plan
    status = (verification or {}).get("status")
    if status in ("failed", "blocked", "cancelled"):
        return "failed"
    if status != "executed-verified" or not (claim or {}).get("verified"):
        return "unverified"
    return "verified" if (claim.get("currency") or {}).get("current") else "stale"


@status_router.get("/{notebook_id}/cell-status")
def cell_status_route(notebook_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    user_key = identity.user_key
    with session_scope() as db:
        head = get_notebook(db, user_key, notebook_id)
        if head is None:
            raise HTTPException(status_code=404, detail="Notebook account copy not found.")
        cells = [c for c in ((head.package or {}).get("notebook") or {}).get("cells") or [] if isinstance(c, dict)]
        plans = db.scalars(select(NotebookExecutionPlan).where(
            NotebookExecutionPlan.user_key == user_key, NotebookExecutionPlan.notebook_id == notebook_id)
            .order_by(NotebookExecutionPlan.created_at.desc(), NotebookExecutionPlan.plan_id)).all()
        latest: dict[str, tuple[NotebookExecutionPlan, dict[str, Any]]] = {}
        for plan in plans:  # newest plan first: the first step seen for a cell is its latest
            for step in plan.steps_json or []:
                cid = str(step.get("cellId") or "")
                if cid and cid not in latest:
                    latest[cid] = (plan, step)
        items = []
        for cell in cells:
            if cell.get("type") == "markdown":
                continue
            cid = str(cell.get("id") or "")
            execution = cell.get("execution") or {}
            item: dict[str, Any] = {
                "cellId": cid, "cellSha256": cell_sha256(cell), "language": cell.get("language"),
                "operation": execution.get("operation"), "dependsOnCellIds": execution.get("dependsOnCellIds") or [],
                "plan": None, "run": None, "currency": None}
            plan, step = latest.get(cid, (None, None))
            verification = claim = None
            if plan is not None:
                item["plan"] = {"planId": plan.plan_id, "status": plan.status, "notebookRevision": plan.notebook_revision,
                                "stepState": step.get("state"), "createdAt": plan.created_at.isoformat()}
                if step.get("runId"):
                    ev = _run_evidence(db, user_key, step["runId"])
                    run = ev.pop("_run", None)
                    verification = ev.get("verification") or {}
                    if run is not None:
                        claim = verified_cell_run(db, user_key, run)
                        item["currency"] = (claim or {}).get("currency")
                        item["run"] = {
                            "runId": run.run_id, "runStatus": run.status, "errorMessage": run.error_message,
                            "cellSha256": step.get("cellSha256"), "cellVerified": bool((claim or {}).get("verified")),
                            "verification": verification, "resultValues": _values(db, user_key, run, verification),
                            "reproducibilityFingerprint": run.reproducibility_fingerprint,
                            "environmentFingerprint": run.environment_fingerprint, "datasetRefs": run.dataset_refs or [],
                            "upstreamCellSha256": step.get("upstreamCellSha256") or {},
                            "finishedAt": run.finished_at.isoformat() if run.finished_at else None}
            item["state"] = _state(step, plan.status if plan else "", verification, claim)
            items.append(item)
        return {"schema": STATUS_SCHEMA, "notebookId": notebook_id, "headRevision": head.revision, "cells": items}
