"""SC-NB-01 portable notebook exports from an immutable Workspace notebook revision.

* ``.ipynb`` (nbformat 4.5): always produced; cells Jupyter cannot represent (attachments,
  Decision Studio, figure, protocol cells, ...) become labelled markdown placeholders and are listed
  in ``metadata.sc_workspace.nonRepresentable``. Code cells carry the outputs of their latest
  verified run for this revision, with run, receipt and input-lineage references.
* Quarto ``.qmd``: only when every code cell is R, Julia or Python; otherwise refused with the reasons.
* Reproducibility package: an ``sc-workspace-notebook-portable-package/1.0`` document (existing
  schema) whose ``related.reproducibility`` section pins cells, runs, receipts, dataset bytes and
  study packages. Signed with the Workspace export key when that key is configured.

Exports are deterministic for a given revision and run state, so their hashes can be compared.
Workspace remains the notebook authority; exports are copies for portability, not new identities.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select

from .security import ServiceIdentity, require_service_identity
from .config import get_settings
from .db import session_scope
from .models import ExecutionRun, ExecutionRunOutput, NotebookExecutionPlan, NotebookRevision
from .notebook_orchestration import cell_sha256
from .object_store import get_artifact, read_artifact_content
from .utils import sha256_hex

IPYNB_META_SCHEMA = "sc-workspace-notebook-ipynb-provenance/1.0"
PACKAGE_SCHEMA = "sc-workspace-notebook-portable-package/1.0"
REPRODUCIBILITY_SCHEMA = "sc-workspace-notebook-reproducibility/1.0"
CODE_LANGUAGES = {"python", "r", "julia", "rust"}
QUARTO_LANGUAGES = {"python", "r", "julia"}
KERNELS = {
    "python": {"name": "python3", "display_name": "Python 3", "language": "python"},
    "r": {"name": "ir", "display_name": "R", "language": "R"},
    "julia": {"name": "julia-1.11", "display_name": "Julia 1.11", "language": "julia"},
    "rust": {"name": "rust", "display_name": "Rust", "language": "rust"},
}
MARKDOWN_BLOCKS = {"note": "", "excerpt": "> ", "question": "**Research question:** ", "claim": "**Claim:** ",
                   "checklist": "", "source": "**Source:** ", "reference": "**Reference:** "}
MAX_EMBEDDED_RESULT_BYTES = 256 * 1024

router = APIRouter(prefix="/v1/notebooks", tags=["notebook-export"])


def _items(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Ordered content: v3 sections/blocks first, then executable cells."""
    out = []
    for section in doc.get("sections") or []:
        if not isinstance(section, dict):
            continue
        out.append({"origin": "section", "id": str(section.get("id") or ""), "kind": "heading",
                    "source": f"## {section.get('title') or ''}".rstrip()})
        for block in section.get("blocks") or []:
            if isinstance(block, dict):
                out.append({"origin": "block", "id": str(block.get("id") or ""), "kind": str(block.get("type") or ""),
                            "block": block})
    for cell in doc.get("cells") or []:
        if isinstance(cell, dict):
            kind = str(cell.get("type") or cell.get("kind") or ("code" if cell.get("execution") else "markdown"))
            out.append({"origin": "cell", "id": str(cell.get("id") or ""), "kind": kind, "cell": cell})
    return out


def _block_markdown(block: dict[str, Any]) -> str:
    kind = str(block.get("type") or "")
    if kind == "divider":
        return "---"
    title = str(block.get("title") or "").strip()
    content = str(block.get("content") or "").strip()
    parts = [f"### {title}"] if title else []
    if content:
        prefix = MARKDOWN_BLOCKS.get(kind, "")
        parts.append("\n".join(prefix + line if prefix == "> " else line for line in content.splitlines()) if prefix == "> "
                     else prefix + content)
    cite = " — ".join(x for x in (str(block.get("sourceTitle") or "").strip(), str(block.get("sourceUrl") or "").strip()) if x)
    if cite:
        parts.append(f"*Source:* {cite}")
    return "\n\n".join(parts)


def _language(cell: dict[str, Any]) -> str:
    return str(cell.get("language") or (cell.get("execution") or {}).get("language") or "").strip().lower()


def _cell_id(raw: str, used: set[str]) -> str:
    base = re.sub(r"[^A-Za-z0-9_-]", "-", raw)[:56] or "cell"
    cid, n = base, 1
    while cid in used:
        n += 1
        cid = f"{base}-{n}"[:64]
    used.add(cid)
    return cid


def _lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def load_revision(db, user_key: str, notebook_id: str, revision: int) -> NotebookRevision:
    row = db.get(NotebookRevision, {"user_key": user_key, "notebook_id": notebook_id, "revision": revision})
    if row is None:
        # Same answer for absent and foreign notebooks.
        raise HTTPException(status_code=404, detail="Workspace notebook revision not found.")
    return row


def _cell_runs(db, user_key: str, rev: NotebookRevision) -> dict[str, list[dict[str, Any]]]:
    """Runs of this exact revision's cells, newest plan first, from server-created plans only."""
    plans = db.scalars(select(NotebookExecutionPlan).where(
        NotebookExecutionPlan.user_key == user_key, NotebookExecutionPlan.notebook_id == rev.notebook_id,
        NotebookExecutionPlan.notebook_revision == rev.revision).order_by(NotebookExecutionPlan.created_at.desc(),
                                                                         NotebookExecutionPlan.plan_id)).all()
    out: dict[str, list[dict[str, Any]]] = {}
    for plan in plans:
        for step in plan.steps_json or []:
            if step.get("runId"):
                out.setdefault(step["cellId"], []).append({"planId": plan.plan_id, **step})
    return out


def _run_evidence(db, user_key: str, run_id: str) -> dict[str, Any]:
    from .research_exports import _verification  # same verification rules as Research exports
    run = db.get(ExecutionRun, {"user_key": user_key, "run_id": run_id})
    if run is None:
        return {"runId": run_id, "status": "missing"}
    outputs = list(db.scalars(select(ExecutionRunOutput).where(
        ExecutionRunOutput.user_key == user_key, ExecutionRunOutput.run_id == run_id)).all())
    v = _verification(db, user_key, run, outputs)
    return {"runId": run_id, "runStatus": run.status, "inputFingerprint": run.input_fingerprint,
            "reproducibilityFingerprint": run.reproducibility_fingerprint,
            "environmentFingerprint": run.environment_fingerprint, "datasetRefs": run.dataset_refs or [],
            "verification": v, "_run": run}


def _result_output(db, user_key: str, ev: dict[str, Any]) -> dict[str, Any] | None:
    v = ev.get("verification") or {}
    if v.get("status") != "executed-verified" or not v.get("runtimeReceipts"):
        return None
    receipt = v["runtimeReceipts"][0]
    art = get_artifact(db, user_key, receipt["resultArtifactId"])
    if art is None or art.sha256 != receipt["resultSha256"] or art.bytes > MAX_EMBEDDED_RESULT_BYTES:
        return None
    result = json.loads(read_artifact_content(art))
    return {"output_type": "execute_result", "execution_count": None,
            "data": {"application/json": result, "text/plain": [f"Workspace run {ev['runId']} result (sha256 {art.sha256})"]},
            "metadata": {"sc_workspace": {"runId": ev["runId"], "resultSha256": art.sha256,
                                          "receiptId": receipt["receiptId"], "inputLineage": v.get("inputLineage")}}}


def _latest_verified(db, user_key: str, runs: list[dict[str, Any]], sha: str) -> dict[str, Any] | None:
    for step in runs:
        if step.get("cellSha256") != sha:
            continue
        ev = _run_evidence(db, user_key, step["runId"])
        if (ev.get("verification") or {}).get("status") == "executed-verified":
            return ev
    return None


def build_ipynb(db, user_key: str, rev: NotebookRevision) -> dict[str, Any]:
    doc = (rev.package or {}).get("notebook") or {}
    runs = _cell_runs(db, user_key, rev)
    used: set[str] = set()
    cells, non_rep, languages = [], [], []
    for item in _items(doc):
        jid = _cell_id(item["id"] or item["kind"], used)
        if item["origin"] == "section":
            cells.append({"cell_type": "markdown", "id": jid, "metadata": {}, "source": _lines(item["source"])})
            continue
        if item["origin"] == "block":
            block = item["block"]
            meta = {"sc_workspace": {"blockId": item["id"], "blockType": item["kind"]}}
            if item["kind"] in MARKDOWN_BLOCKS or item["kind"] == "divider":
                cells.append({"cell_type": "markdown", "id": jid, "metadata": meta, "source": _lines(_block_markdown(block))})
            else:
                non_rep.append({"id": item["id"], "kind": item["kind"], "reason": "binary or structured block has no Jupyter equivalent"})
                meta["sc_workspace"]["nonRepresentable"] = True
                cells.append({"cell_type": "markdown", "id": jid, "metadata": meta,
                              "source": _lines(f"*Not representable in Jupyter: Workspace {item['kind']} block `{item['id']}`.*")})
            continue
        cell = item["cell"]
        lang = _language(cell)
        sha = cell_sha256(cell)
        meta = {"sc_workspace": {"cellId": item["id"], "cellSha256": sha, "language": lang or None,
                                 "execution": cell.get("execution")}}
        if item["kind"] == "markdown":
            cells.append({"cell_type": "markdown", "id": jid, "metadata": meta, "source": _lines(str(cell.get("source") or ""))})
        elif item["kind"] == "code" and lang in CODE_LANGUAGES:
            if lang not in languages:
                languages.append(lang)
            ev = _latest_verified(db, user_key, runs.get(item["id"], []), sha)
            out = _result_output(db, user_key, ev) if ev else None
            if ev:
                meta["sc_workspace"]["run"] = {"runId": ev["runId"], "inputLineage": ev["verification"]["inputLineage"],
                                               "inputBindings": ev["verification"]["inputBindings"]}
            cells.append({"cell_type": "code", "id": jid, "metadata": meta, "execution_count": None,
                          "outputs": [out] if out else [], "source": _lines(str(cell.get("source") or ""))})
        else:
            reason = (f"no authorized runtime adapter for language '{lang}'" if item["kind"] == "code"
                      else f"Workspace {item['kind']} cell has no Jupyter equivalent")
            non_rep.append({"id": item["id"], "kind": item["kind"], "reason": reason})
            meta["sc_workspace"]["nonRepresentable"] = True
            cells.append({"cell_type": "markdown", "id": jid, "metadata": meta,
                          "source": _lines(f"*Not representable in Jupyter: {reason} (cell `{item['id']}`).*")})
    primary = languages[0] if languages else "python"
    issues = list(non_rep)
    if len(languages) > 1:
        issues.append({"id": None, "kind": "kernel", "reason": f"cells use {', '.join(languages)}; one Jupyter kernel cannot run them all"})
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": KERNELS[primary], "language_info": {"name": KERNELS[primary]["language"]},
            "sc_workspace": {"schema": IPYNB_META_SCHEMA, "authority": "workspace", "notebookId": rev.notebook_id,
                             "notebookRevision": rev.revision, "notebookPackageSha256": rev.fingerprint,
                             "title": rev.title, "languages": languages, "fullyRepresentable": not issues,
                             "nonRepresentable": issues,
                             "outputs": "latest executed-verified run of each unchanged cell in this revision; others have none"},
        },
        "cells": cells,
    }


def build_quarto(rev: NotebookRevision) -> str:
    doc = (rev.package or {}).get("notebook") or {}
    blockers, body, labels = [], [], set()
    for item in _items(doc):
        if item["origin"] == "section":
            body.append(item["source"])
        elif item["origin"] == "block":
            if item["kind"] in MARKDOWN_BLOCKS or item["kind"] == "divider":
                body.append(_block_markdown(item["block"]))
            else:
                body.append(f"> Not representable in Quarto: Workspace {item['kind']} block `{item['id']}`.")
        elif item["kind"] == "markdown":
            body.append(str(item["cell"].get("source") or ""))
        elif item["kind"] == "code" and _language(item["cell"]) in QUARTO_LANGUAGES:
            label = _cell_id(item["id"], labels)
            body.append(f"```{{{_language(item['cell'])}}}\n#| label: {label}\n#| sc-cell-sha256: {cell_sha256(item['cell'])}\n"
                        f"{str(item['cell'].get('source') or '').rstrip()}\n```")
        else:
            blockers.append({"id": item["id"], "kind": item["kind"], "language": _language(item["cell"]) or None})
    if blockers:
        raise HTTPException(status_code=409, detail={"code": "quarto-not-representable", "cells": blockers,
                                                     "supportedLanguages": sorted(QUARTO_LANGUAGES)})
    front = {"title": rev.title, "sc-workspace": {"authority": "workspace", "notebook-id": rev.notebook_id,
                                                  "notebook-revision": rev.revision, "notebook-package-sha256": rev.fingerprint}}
    # JSON is valid YAML, which keeps quoting exact without a YAML dependency.
    return "---\n" + "\n".join(f"{k}: {json.dumps(v, sort_keys=True)}" for k, v in front.items()) + "\n---\n\n" + "\n\n".join(body).rstrip() + "\n"


def ipynb_bytes(nb: dict[str, Any]) -> bytes:
    return (json.dumps(nb, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def build_package(db, user_key: str, rev: NotebookRevision) -> dict[str, Any]:
    from .research_exports import _study_packages, sign_document
    doc = (rev.package or {}).get("notebook") or {}
    nb = build_ipynb(db, user_key, rev)
    try:
        quarto = {"sha256": hashlib.sha256(build_quarto(rev).encode("utf-8")).hexdigest(), "representable": True}
    except HTTPException as exc:
        quarto = {"sha256": None, "representable": False, "reason": exc.detail}
    runs = _cell_runs(db, user_key, rev)
    cells, executions, datasets, packages = [], [], {}, {}
    for item in _items(doc):
        if item["origin"] != "cell":
            continue
        sha = cell_sha256(item["cell"])
        cells.append({"cellId": item["id"], "kind": item["kind"], "language": _language(item["cell"]) or None, "cellSha256": sha})
        for step in runs.get(item["id"], []):
            ev = _run_evidence(db, user_key, step["runId"])
            run = ev.pop("_run", None)
            v = ev.get("verification") or {}
            executions.append({"planId": step["planId"], "cellId": item["id"], "cellSha256": step.get("cellSha256"),
                               "cellUnchanged": step.get("cellSha256") == sha, "stepState": step.get("state"), **ev})
            for b in v.get("inputBindings") or []:
                datasets[(b["datasetId"], b["datasetRevision"])] = {k: b.get(k) for k in (
                    "datasetId", "datasetRevision", "artifactId", "artifactRevision", "artifactSha256", "rowsSha256")}
            if run is not None:
                for p in _study_packages(db, user_key, run):
                    packages[p["packageId"]] = p
    reproducibility = {
        "schema": REPRODUCIBILITY_SCHEMA,
        "notebookRef": {"authority": "workspace", "notebookId": rev.notebook_id, "notebookRevision": rev.revision,
                        "notebookPackageSha256": rev.fingerprint},
        "cells": cells, "executions": executions,
        "datasets": [datasets[k] for k in sorted(datasets)],
        "studyPackages": [packages[k] for k in sorted(packages)],
        "exports": {"ipynb": {"sha256": hashlib.sha256(ipynb_bytes(nb)).hexdigest(), "fullyRepresentable": nb["metadata"]["sc_workspace"]["fullyRepresentable"],
                              "nonRepresentable": nb["metadata"]["sc_workspace"]["nonRepresentable"]},
                    "quarto": quarto},
        "notIncluded": ["dataset bytes (pinned by artifactSha256; retrieve from the Workspace artifact store)",
                        "runtime images (identified by the runtime receipts)"],
        "replay": ("Re-run the cells through Workspace notebook execution plans with the same datasetInput revisions, "
                   "then compare in Research (convergence/workspace/reproductions). Matching execution fingerprints "
                   "alone are not evidence of reproducibility."),
    }
    body = {"schema": PACKAGE_SCHEMA, "workspaceVersion": get_settings().service_version,
            "sourceProject": {"projectId": rev.project_id}, "notebook": doc,
            "related": {"reproducibility": reproducibility},
            "governance": {"visibility": "private", "publicationApproved": False,
                           "note": "Export of a private Workspace notebook revision; publication requires separate Research approval."}}
    body["integrity"] = {"contentSha256": sha256_hex(body)}
    body["exportedAt"] = datetime.now(timezone.utc).isoformat()
    try:
        return sign_document(PACKAGE_SCHEMA, body)
    except HTTPException:
        return {**body, "signature": None}


@router.get("/{notebook_id}/revisions/{revision}/export")
def export_route(notebook_id: str, revision: int, format: str = Query(default="ipynb", pattern="^(ipynb|qmd|package)$"),
                 identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        rev = load_revision(db, identity.user_key, notebook_id, revision)
        stem = re.sub(r"[^A-Za-z0-9_-]", "-", f"{notebook_id}-r{revision}")
        if format == "ipynb":
            raw = ipynb_bytes(build_ipynb(db, identity.user_key, rev))
            media, name = "application/x-ipynb+json", f"{stem}.ipynb"
        elif format == "qmd":
            raw, media, name = build_quarto(rev).encode("utf-8"), "text/markdown; charset=utf-8", f"{stem}.qmd"
        else:
            raw = (json.dumps(build_package(db, identity.user_key, rev), indent=1, sort_keys=True) + "\n").encode("utf-8")
            media, name = "application/json", f"{stem}.reproducibility.json"
    return Response(content=raw, media_type=media, headers={
        "Content-Disposition": f'attachment; filename="{name}"', "X-SC-Export-Sha256": hashlib.sha256(raw).hexdigest()})
