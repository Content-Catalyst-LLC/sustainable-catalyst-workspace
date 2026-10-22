"""Read-only recovery inventory, bound to a real Workspace session and an expiring administrative grant.

Reading this inventory confers neither historical ownership nor scientific approval.
There are no staging, import, artifact-byte download, or mutation endpoints.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import stat

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .session_auth import session_payload_from_request

router = APIRouter(prefix="/v1/private-research/wexford-recovery", tags=["Private Wexford Recovery"])
SCHEMA = "sc.workspace.recovery-review-grant.v1"
SCOPE = "wexford-recovery:review"


def _read_regular(path: str, limit: int, *, protected: bool = False) -> bytes:
    if not path or not Path(path).is_absolute():
        raise ValueError("Absolute server-side path required")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit:
            raise ValueError("Invalid file")
        if protected and (info.st_mode & 0o077 or info.st_uid not in {0, os.geteuid()}):
            raise ValueError("Untrusted grant file")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            data = handle.read(limit + 1)
        if len(data) > limit:
            raise ValueError("File too large")
        return data
    finally:
        os.close(fd)


def _grant(request: Request) -> dict:
    payload = session_payload_from_request(request)
    subject = payload.get("sub") if isinstance(payload, dict) else None
    if not isinstance(subject, str) or not subject.strip() or len(subject) > 128:
        raise HTTPException(401, "A valid Workspace browser session is required.", headers={"Cache-Control": "no-store"})
    try:
        grant = json.loads(_read_regular(os.getenv("WXR_REVIEW_GRANT_FILE", ""), 8192, protected=True))
        required = {"schema", "scope", "status", "subject_sha256", "catalog_sha256", "approved_by", "approval_reference", "issued_at", "expires_at"}
        if not isinstance(grant, dict) or set(grant) != required:
            raise ValueError("Grant schema")
        if grant["schema"] != SCHEMA or grant["scope"] != SCOPE or grant["status"] != "approved":
            raise ValueError("Grant scope")
        digest = hashlib.sha256(subject.encode()).hexdigest()
        if not isinstance(grant["subject_sha256"], str) or not hmac.compare_digest(digest, grant["subject_sha256"]):
            raise ValueError("Grant subject")
        if not isinstance(grant["catalog_sha256"], str) or len(grant["catalog_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in grant["catalog_sha256"]):
            raise ValueError("Catalog digest")
        if not all(isinstance(grant[k], str) and len(grant[k].strip()) >= 3 for k in ("approved_by", "approval_reference")):
            raise ValueError("Approval record")
        issued = datetime.fromisoformat(grant["issued_at"].replace("Z", "+00:00"))
        expiry = datetime.fromisoformat(grant["expires_at"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if issued.tzinfo is None or expiry.tzinfo is None or not issued <= now < expiry or not 0 < (expiry - issued).total_seconds() <= 86400:
            raise ValueError("Grant validity")
        return grant
    except (OSError, ValueError, TypeError, AttributeError):
        raise HTTPException(403, "Private recovery review access is not authorized.", headers={"Cache-Control": "no-store"}) from None


def _inventory(grant: dict) -> dict:
    try:
        raw = _read_regular(os.getenv("WXR_REVIEW_CATALOG_FILE", ""), 50 * 1024 * 1024)
        if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), grant["catalog_sha256"]):
            raise ValueError("Catalog changed")
        catalog = json.loads(raw)
        if not isinstance(catalog, dict):
            raise ValueError("Catalog shape")
        output = {}
        fields = {
            "projects": ("project_id", "name", "owner_fingerprint", "curation_status"),
            "calculations": ("record_id", "project_id", "owner_fingerprint", "association", "curation_status", "review_status"),
            "artifacts": ("artifact_id", "collection", "relative_path", "kind_hint", "sha256", "size_bytes", "curation_status", "ownership_status", "scientific_status"),
        }
        for section, keys in fields.items():
            rows = catalog.get(section)
            if not isinstance(rows, list) or len(rows) > 100000 or not all(isinstance(row, dict) for row in rows):
                raise ValueError("Catalog records")
            output[section] = [{key: row.get(key) for key in keys} for row in rows]
        output.update({
            "summary": {"projects": len(output["projects"]), "calculations": len(output["calculations"]), "artifact_occurrences": len(output["artifacts"]), "unique_artifacts": len({row["sha256"] for row in output["artifacts"] if row["sha256"]})},
            "catalog_sha256": grant["catalog_sha256"], "expires_at": grant["expires_at"],
            "access": "PRIVATE_READ_ONLY", "historical_ownership": "UNRESOLVED",
            "scientific_validity": "NOT_ASSESSED", "staging": "NOT_PERFORMED",
            "workspace_registration": "NOT_PERFORMED", "publication": "DISABLED",
        })
        return output
    except (OSError, ValueError, TypeError, KeyError):
        raise HTTPException(503, "Verified recovery inventory is unavailable.", headers={"Cache-Control": "no-store"}) from None


HEADERS = {"Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow", "X-Content-Type-Options": "nosniff"}


@router.get("/catalog")
def catalog(request: Request):
    return JSONResponse(_inventory(_grant(request)), headers=HEADERS)


@router.get("/access-status")
def access_status(request: Request):
    grant = _grant(request)
    _inventory(grant)
    return JSONResponse({"session": "VERIFIED", "research_access": "PRIVATE_READ_ONLY", "expires_at": grant["expires_at"], "historical_ownership": "UNRESOLVED", "staging": "NOT_PERFORMED", "workspace_registration": "NOT_PERFORMED", "publication": "DISABLED"}, headers=HEADERS)


SCRIPT = r'''async function load(){const status=document.getElementById('status');try{const response=await fetch('./catalog',{credentials:'same-origin',cache:'no-store'});if(!response.ok)throw new Error(response.status===403?'Review access has expired or is not authorized.':'The verified recovery inventory is unavailable.');const d=await response.json();document.getElementById('counts').textContent=d.summary.projects+' projects · '+d.summary.calculations+' calculations · '+d.summary.unique_artifacts+' unique artifact files';document.getElementById('expiry').textContent='Review access expires '+new Date(d.expires_at).toLocaleString();for(const [section,keys] of [['projects',['name','project_id','curation_status','owner_fingerprint']],['calculations',['record_id','project_id','review_status']],['artifacts',['relative_path','collection','kind_hint','sha256']]]){const body=document.getElementById(section);for(const row of d[section]){const tr=document.createElement('tr');for(const key of keys){const td=document.createElement('td');const value=row[key];td.textContent=value==null?'—':typeof value==='object'?JSON.stringify(value):String(value);tr.appendChild(td)}body.appendChild(tr)}}document.getElementById('fingerprint').textContent='Catalog SHA-256: '+d.catalog_sha256;status.textContent='Verified recovery inventory loaded. Originals are preserved.';}catch(error){status.textContent=error.message;status.setAttribute('role','alert')}}load();'''

HTML = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Wexford recovery review | Sustainable Catalyst</title><style>body{margin:0;background:#0c1011;color:#e8eeed;font:16px/1.6 system-ui}main{max-width:1160px;margin:auto;padding:32px 24px 60px}.brand{font-size:12px;font-weight:700;letter-spacing:.16em;color:#8dccc0}h1{font-size:clamp(28px,4vw,44px);line-height:1.2;margin:12px 0}h2{margin-top:36px;font-size:23px}.lead{color:#b8c8c4;max-width:850px}.notice{border-left:3px solid #d6b36f;background:#211e17;padding:16px 20px;margin:24px 0}.counts{font-size:20px;font-weight:650;color:#b8e1d7}.meta{font-size:13px;color:#aabcb6;overflow-wrap:anywhere}details{border:1px solid #344540;border-radius:8px;margin:18px 0;background:#101817}summary{cursor:pointer;padding:16px;font-size:20px;font-weight:600}.table{overflow:auto;max-height:440px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;vertical-align:top;border-top:1px solid #344540;padding:12px;max-width:420px;overflow-wrap:anywhere}th{color:#b8d6cd;background:#17231f;position:sticky;top:0}footer{margin-top:30px;border-top:1px solid #344540;padding-top:20px}a{color:#b8e1d7}</style></head><body><main><div class="brand">SUSTAINABLE CATALYST / PRIVATE RESEARCH</div><h1>Wexford recovery review</h1><p class="lead">Inspect the recovered research inventory and its provenance. This private view preserves the original records and gives you a place to review what was recovered before any restoration.</p><div class="notice"><strong>Private, read-only review</strong><br>Historical ownership is unresolved. Scientific validity has not been assessed. Nothing has been imported, staged, reassigned, or published.</div><p class="counts" id="counts">Loading verified inventory…</p><p id="status" role="status" aria-live="polite"></p><p class="meta" id="expiry"></p><details open><summary>Recovered projects</summary><div class="table"><table><thead><tr><th>Project</th><th>Original project ID</th><th>Review status</th><th>Historical owner fingerprint</th></tr></thead><tbody id="projects"></tbody></table></div></details><details><summary>Calculation inventory</summary><div class="table"><table><thead><tr><th>Calculation ID</th><th>Original project ID</th><th>Review status</th></tr></thead><tbody id="calculations"></tbody></table></div></details><details><summary>Artifact inventory</summary><div class="table"><table><thead><tr><th>File</th><th>Collection</th><th>Type</th><th>SHA-256</th></tr></thead><tbody id="artifacts"></tbody></table></div></details><footer><p class="meta" id="fingerprint"></p><a href="/v1/private-research/recovery/ui">Open private research restoration</a> · <a href="/v1/private-research/ui">Back to Private Research Workspace</a></footer></main><script>''' + SCRIPT + '''</script></body></html>'''


@router.get("/ui", response_class=HTMLResponse)
def private_ui(request: Request):
    _inventory(_grant(request))
    script_hash = __import__("base64").b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
    return HTMLResponse(HTML, headers={**HEADERS, "Content-Security-Policy": f"default-src 'none'; script-src 'sha256-{script_hash}'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"})
