"""SC-RIGHTS-02: reliable delivery of owner-signed source-rights notices from Workspace to Research.

Workspace stays the rights authority and Research stays the publication authority; this module only moves
the signed notices and keeps the two in step. Nothing here signs a new rights decision.

1. Outbox. ``enqueue`` runs in the transaction that writes the notice, so a notice exists with its delivery
   row or not at all.
2. Delivery. The Workspace worker claims due rows with ``FOR UPDATE SKIP LOCKED`` and a lease, posts the
   stored signed notice, and records the outcome. Per owner and source only the lowest undelivered sequence
   is eligible (the notice chain is causal); across sources restrictions go first. A restriction may pass
   a blocked earlier notice: Research applies it and records the gap, and the blocked notice stays visible.
3. Retries. Transport errors, 5xx, 429 and 503 retry with capped exponential backoff and jitter, up to
   ``research_rights_max_attempts``, then block (alert). 401/403/422 block at once. A 409 "newer" marks the
   notice superseded; "does not follow" asks for reconciliation. A lost acknowledgement is harmless: the
   retry returns Research's replay of the notice it already applied.
4. Reconciliation. The worker reads Research's applied state, re-queues notices Research lost (restore from
   backup), and sends one signed attestation per owner of the latest notice per source. Research uses the
   attestation for its rights-freshness hold.
"""
from __future__ import annotations

import html
import json
import random
import secrets
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Body, Header, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import and_, exists, func, select
from sqlalchemy.orm import Session, aliased

from .config import get_settings
from .db import session_scope
from .models import (DatasetRevision, ResearchRightsDeliveryEvent, ResearchRightsOutbox, ResearchRightsSyncState,
                     ResearchSourceRightsNotice, WorkerHeartbeat)

ATTESTATION_SCHEMA = "sc-workspace-source-rights-attestation/1.0"
STATUS_SCHEMA = "sc-workspace-rights-delivery-status/1.0"
TERMINAL = ("applied", "superseded")
PENDING = ("queued", "retrying", "delivering")
router = APIRouter(prefix="/v1/research-exports/rights-delivery", tags=["SC-RIGHTS-02 rights delivery"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(when: datetime | None) -> datetime | None:
    return when if when is None or when.tzinfo else when.replace(tzinfo=timezone.utc)


def _token(path: str) -> str:
    try:
        return Path(path).read_text().strip() if path else ""
    except OSError:
        return ""


def enabled() -> bool:
    s = get_settings()
    return bool(s.research_export_enabled and s.research_rights_delivery_url and _token(s.research_rights_delivery_token_file))


def _event(db: Session, kind: str, outcome: str = "", *, notice_id: str = "", user_key: str = "",
           http_status: int | None = None, detail: dict | None = None) -> None:
    db.add(ResearchRightsDeliveryEvent(notice_id=notice_id, user_key=user_key, kind=kind, outcome=outcome,
                                       http_status=http_status, detail=detail or {}, at=_now()))


def enqueue(db: Session, *, notice_id: str, user_key: str, source_sha256: str, sequence: int, licence_status: str,
            created_at: datetime | None = None) -> None:
    """Add the delivery row for a notice. Call inside the transaction that inserts the notice."""
    now = created_at or _now()
    db.add(ResearchRightsOutbox(notice_id=notice_id, user_key=user_key, source_sha256=source_sha256, sequence=sequence,
                                licence_status=licence_status, priority=0 if licence_status == "restricted" else 1,
                                state="queued", attempts=0, next_attempt_at=now, created_at=now, updated_at=now))
    _event(db, "enqueued", "queued", notice_id=notice_id, user_key=user_key,
           detail={"sequence": sequence, "licenceStatus": licence_status})


# ---------------------------------------------------------------------------
# HTTP to Research (replaceable in tests)


class TransportError(Exception):
    pass


def http_call(method: str, path: str, body: dict | None = None) -> tuple[int, Any]:
    s = get_settings()
    url = s.research_rights_delivery_url.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {_token(s.research_rights_delivery_token_file)}"})
    try:
        with urllib.request.urlopen(req, timeout=s.research_rights_http_timeout_seconds) as resp:
            raw = resp.read(1 << 20)
            return resp.status, json.loads(raw or b"{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read(1 << 16)
        try:
            return exc.code, json.loads(raw or b"{}")
        except ValueError:
            return exc.code, {"detail": raw.decode("utf-8", "replace")[:500]}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise TransportError(f"{exc.__class__.__name__}: {exc}"[:500]) from exc


# ---------------------------------------------------------------------------
# Delivery


def backoff_seconds(attempts: int) -> float:
    """Capped exponential backoff with jitter: half fixed, half random (never zero, never above the cap)."""
    s = get_settings()
    ceiling = min(s.research_rights_backoff_cap_seconds, s.research_rights_backoff_base_seconds * (2 ** max(attempts - 1, 0)))
    return ceiling / 2 + random.uniform(0, ceiling / 2)


def claim(db: Session, worker_id: str, limit: int | None = None) -> list[dict]:
    """Lease the due head notice of each source (restrictions first). Returns snapshots to deliver."""
    s = get_settings()
    now = _now()
    earlier = aliased(ResearchRightsOutbox)
    blocking = exists().where(
        earlier.user_key == ResearchRightsOutbox.user_key, earlier.source_sha256 == ResearchRightsOutbox.source_sha256,
        earlier.sequence < ResearchRightsOutbox.sequence, earlier.state.not_in(TERMINAL),
        # A restriction may pass an earlier notice that is blocked; Research records the gap.
        ~and_(ResearchRightsOutbox.priority == 0, earlier.state == "blocked"))
    due = ((ResearchRightsOutbox.state.in_(("queued", "retrying")) & (ResearchRightsOutbox.next_attempt_at <= now))
           | ((ResearchRightsOutbox.state == "delivering") & (ResearchRightsOutbox.lease_expires_at < now)))
    q = (select(ResearchRightsOutbox).where(due, ~blocking)
         .order_by(ResearchRightsOutbox.priority, ResearchRightsOutbox.created_at, ResearchRightsOutbox.sequence)
         .limit(limit or s.research_rights_batch))
    if db.get_bind().dialect.name == "postgresql":
        q = q.with_for_update(skip_locked=True)
    out = []
    for row in db.scalars(q).all():
        reclaimed = row.state == "delivering"
        row.state, row.lease_owner = "delivering", worker_id
        row.lease_expires_at = now + timedelta(seconds=s.research_rights_lease_seconds)
        row.attempts += 1
        row.first_attempt_at = row.first_attempt_at or now
        row.updated_at = now
        _event(db, "attempt", "reclaimed-after-lease" if reclaimed else "started", notice_id=row.notice_id,
               user_key=row.user_key, detail={"attempt": row.attempts, "workerId": worker_id})
        notice = db.get(ResearchSourceRightsNotice, row.notice_id)
        out.append({"noticeId": row.notice_id, "attempt": row.attempts, "notice": notice.notice_json})
    db.commit()
    return out


def classify(status: int | None, body: Any) -> tuple[str, str]:
    """(state, code) for one Research answer; status None is a transport failure."""
    detail = str((body or {}).get("detail") if isinstance(body, dict) else body or "")
    if status == 200:
        return "applied", "replayed" if isinstance(body, dict) and body.get("replayed") else "applied"
    if status is None:
        return "retrying", "transport"
    if status == 409:
        if "newer" in detail:
            return "superseded", "newer-applied"
        if "does not follow" in detail:
            return "retrying", "does-not-follow"
        return "retrying", "conflict"
    if status in (401, 403):
        return "blocked", "unauthorised" if status == 401 else "refused-signature-or-owner"
    if status in (404, 422):
        return "blocked", "refused" if status == 422 else "route-missing"
    return "retrying", f"http-{status}"


def record(db: Session, notice_id: str, worker_id: str, status: int | None, body: Any, error: str = "") -> str | None:
    """Store the outcome if this worker still holds the lease (a reclaimed row belongs to its new holder)."""
    s = get_settings()
    row = db.get(ResearchRightsOutbox, notice_id, with_for_update=db.get_bind().dialect.name == "postgresql")
    if row is None or row.state != "delivering" or row.lease_owner != worker_id:
        db.rollback()
        return None
    state, code = classify(status, body)
    now = _now()
    if state == "retrying" and row.attempts >= s.research_rights_max_attempts:
        state, code = "blocked", f"max-attempts:{code}"
    row.state, row.last_http_status, row.last_error_code = state, status, code[:64]
    row.last_error = (error or (json.dumps(body)[:2000] if state != "applied" else ""))[:4000]
    row.lease_owner, row.lease_expires_at, row.updated_at = "", None, now
    if state == "applied":
        row.applied_at = now
        row.research_receipt = {k: body.get(k) for k in ("noticeId", "sequence", "replayed", "chainGap",
                                                         "revokedObjectIds", "figureBytesRemoved", "articles", "auditEvents")}
    elif state == "retrying":
        row.next_attempt_at = now + timedelta(seconds=0.5 if code == "does-not-follow" else backoff_seconds(row.attempts))
    _event(db, "outcome", f"{state}:{code}", notice_id=row.notice_id, user_key=row.user_key, http_status=status,
           detail={"attempt": row.attempts, "error": row.last_error[:500]} if state != "applied" else row.research_receipt)
    db.commit()
    return state


def deliver_due(worker_id: str) -> list[str]:
    global _last_reconcile
    with session_scope() as db:
        batch = claim(db, worker_id)
    states = []
    for item in batch:
        status, body, error = None, None, ""
        try:
            status, body = http_call("POST", "/convergence/workspace/source-rights-notices", {"notice": item["notice"]})
        except TransportError as exc:
            error = str(exc)
        with session_scope() as db:
            states.append(record(db, item["noticeId"], worker_id, status, body, error))
        if states[-1] == "retrying" and "does not follow" in str((body or {}).get("detail") if isinstance(body, dict) else ""):
            _last_reconcile = 0.0  # Research is missing an earlier notice: reconcile on this tick
    return [s for s in states if s]


# ---------------------------------------------------------------------------
# Reconciliation and attestation


def _user(owner_scope: str) -> str | None:
    return owner_scope.split(":", 1)[1] if owner_scope.startswith("workspace-user:") else None


def _latest_notices(db: Session) -> dict[tuple[str, str], ResearchSourceRightsNotice]:
    latest = {}
    for n in db.scalars(select(ResearchSourceRightsNotice).order_by(ResearchSourceRightsNotice.sequence)):
        latest[(n.user_key, n.source_sha256)] = n
    return latest


def reconcile() -> dict:
    """Compare with Research, re-queue what it lost, and attest the latest notices per owner."""
    from .research_exports import AUDIENCE, ISSUER, sign_document

    try:
        status, state = http_call("GET", "/convergence/workspace/source-rights-state")
    except TransportError as exc:
        status, state = None, str(exc)
    if status != 200:
        with session_scope() as db:
            _event(db, "reconcile", f"state-unavailable:{status}", http_status=status, detail={"body": str(state)[:500]})
            db.commit()
        return {"ok": False, "status": status}
    research = {(_user(o["ownerScope"]), s["sourceSha256"]): s for o in state.get("owners") or [] if _user(o["ownerScope"])
                for s in o.get("sources") or []}
    summary = {"requeued": [], "attested": [], "results": {}}
    with session_scope() as db:
        # Notices without a delivery row (issued before the outbox existed, migration 058 not run) are queued.
        orphans = db.scalars(select(ResearchSourceRightsNotice).where(~exists().where(
            ResearchRightsOutbox.notice_id == ResearchSourceRightsNotice.notice_id))).all()
        for n in orphans:
            enqueue(db, notice_id=n.notice_id, user_key=n.user_key, source_sha256=n.source_sha256, sequence=n.sequence,
                    licence_status=n.licence_status, created_at=_aware(n.issued_at))
            summary["requeued"].append(n.notice_id)
        db.flush()
        latest = _latest_notices(db)
        for (user, sha), n in latest.items():
            applied = (research.get((user, sha)) or {}).get("appliedSequence", 0)
            for row in db.scalars(select(ResearchRightsOutbox).where(
                    ResearchRightsOutbox.user_key == user, ResearchRightsOutbox.source_sha256 == sha,
                    ResearchRightsOutbox.state == "applied", ResearchRightsOutbox.sequence > applied)):
                # Research no longer has a notice it acknowledged (for example after a restore): send it again.
                row.state, row.attempts, row.next_attempt_at, row.updated_at = "queued", 0, _now(), _now()
                row.last_error_code = "research-missing"
                summary["requeued"].append(row.notice_id)
                _event(db, "requeue", "research-missing", notice_id=row.notice_id, user_key=user,
                       detail={"researchSequence": applied, "sequence": row.sequence})
            for row in db.scalars(select(ResearchRightsOutbox).where(
                    ResearchRightsOutbox.user_key == user, ResearchRightsOutbox.source_sha256 == sha,
                    ResearchRightsOutbox.state == "retrying")):
                row.next_attempt_at = _now()  # deliver the repaired chain now rather than after backoff
        owners = {u for u, _ in latest} | {u for u, _ in research}
        for user in sorted(owners):
            shas = sorted({sha for u, sha in latest if u == user} | {sha for u, sha in research if u == user})
            known = set(db.scalars(select(DatasetRevision.artifact_sha256).where(
                DatasetRevision.user_key == user, DatasetRevision.artifact_sha256.in_(shas))))
            sources = []
            for sha in shas:
                n = latest.get((user, sha))
                sources.append({"sourceSha256": sha, "sequence": n.sequence if n else 0,
                                "noticeSha256": n.notice_sha256 if n else None,
                                "licenceStatus": n.licence_status if n else None, "known": sha in known or n is not None})
            body = {"schema": ATTESTATION_SCHEMA, "issuer": ISSUER, "audience": AUDIENCE,
                    "attestationId": f"sra_{uuid4().hex}", "ownerScope": f"workspace-user:{user}",
                    "issuedAt": _now().isoformat(), "sources": sources}
            att = sign_document(ATTESTATION_SCHEMA, body)
            try:
                code, out = http_call("POST", "/convergence/workspace/source-rights-attestations", {"attestation": att})
            except TransportError as exc:
                code, out = None, {"detail": str(exc)}
            _event(db, "attest", "accepted" if code == 200 else f"refused:{code}", user_key=user, http_status=code,
                   detail={"attestationId": body["attestationId"], "sources": len(sources),
                           "results": (out or {}).get("results") if code == 200 else None,
                           "error": None if code == 200 else str((out or {}).get("detail"))[:500]})
            if code != 200:
                continue
            summary["attested"].append(body["attestationId"])
            for r in out.get("results") or []:
                st = db.get(ResearchRightsSyncState, {"user_key": user, "source_sha256": r["sourceSha256"]})
                if st is None:
                    st = ResearchRightsSyncState(user_key=user, source_sha256=r["sourceSha256"])
                    db.add(st)
                st.research_status, st.research_sequence = r["status"], r["researchSequence"]
                st.workspace_sequence = r["attestedSequence"]
                st.live_figures = (research.get((user, r["sourceSha256"])) or {}).get("liveFigures", 0)
                st.attestation_id, st.attested_at, st.checked_at = body["attestationId"], _now(), _now()
                summary["results"][r["sourceSha256"]] = r["status"]
        _event(db, "reconcile", "ok", detail={"requeued": summary["requeued"], "owners": len(owners)})
        db.commit()
    return {"ok": True, **summary}


# ---------------------------------------------------------------------------
# Worker hook

_last_reconcile = 0.0
_last_alerts: set[str] = set()


def tick(worker_id: str) -> None:
    """Called from the Workspace worker loop. Never raises: delivery problems must not stop job processing."""
    global _last_reconcile, _last_alerts
    if not enabled():
        return
    try:
        deliver_due(worker_id)
        if time.monotonic() - _last_reconcile >= get_settings().research_rights_attest_interval_seconds:
            _last_reconcile = time.monotonic()
            reconcile()
        with session_scope() as db:
            alerts = status(db)["alerts"]
        keys = {f"{a['severity']}:{a['code']}:{a.get('subject', '')}" for a in alerts}
        for a in alerts:
            if f"{a['severity']}:{a['code']}:{a.get('subject', '')}" not in _last_alerts:
                print(f"SC-RIGHTS ALERT {a['severity']} {a['code']} {a.get('subject', '')} {a['message']}", flush=True)
        for gone in _last_alerts - keys:
            print(f"SC-RIGHTS RESOLVED {gone}", flush=True)
        _last_alerts = keys
    except Exception as exc:  # noqa: BLE001 - reported, retried next tick
        print(f"SC-RIGHTS delivery tick error: {exc.__class__.__name__}: {exc}"[:1000], flush=True)


# ---------------------------------------------------------------------------
# Status, alerts and the private dashboard


def _age(now: datetime, when: datetime | None) -> float | None:
    return None if when is None else round((now - _aware(when)).total_seconds(), 1)


def _pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    return round(values[min(len(values) - 1, int(round(p * (len(values) - 1))))], 3)


def status(db: Session) -> dict:
    s = get_settings()
    now = _now()
    rows = db.scalars(select(ResearchRightsOutbox).order_by(ResearchRightsOutbox.created_at.desc())).all()
    counts = {k: 0 for k in ("queued", "delivering", "retrying", "applied", "superseded", "blocked")}
    for r in rows:
        counts[r.state] = counts.get(r.state, 0) + 1
    lag = [(_aware(r.applied_at) - _aware(r.created_at)).total_seconds() for r in rows
           if r.applied_at and _aware(r.applied_at) > now - timedelta(days=1)]
    open_rows = [r for r in rows if r.state not in TERMINAL]
    items = [{"noticeId": r.notice_id, "owner": r.user_key, "source": r.source_sha256, "sequence": r.sequence,
              "licenceStatus": r.licence_status, "state": r.state, "attempts": r.attempts,
              "ageSeconds": _age(now, r.created_at), "nextAttemptInSeconds": (
                  round((_aware(r.next_attempt_at) - now).total_seconds(), 1) if r.state in ("queued", "retrying") else None),
              "lastHttpStatus": r.last_http_status, "lastError": r.last_error_code,
              "chainGap": (r.research_receipt or {}).get("chainGap"), "replayed": (r.research_receipt or {}).get("replayed")}
             for r in rows[:200]]
    sync = db.scalars(select(ResearchRightsSyncState).order_by(ResearchRightsSyncState.checked_at.desc())).all()
    last_ok = db.scalar(select(func.max(ResearchRightsDeliveryEvent.at)).where(
        ResearchRightsDeliveryEvent.kind == "attest", ResearchRightsDeliveryEvent.outcome == "accepted"))
    hb = db.scalar(select(func.max(WorkerHeartbeat.last_seen_at)))
    alerts = []
    for r in open_rows:
        age = _age(now, r.created_at) or 0
        if r.licence_status == "restricted" and age >= s.research_rights_alert_restriction_seconds:
            alerts.append({"severity": "critical", "code": "restriction-unapplied", "subject": r.notice_id,
                           "message": f"restriction for source {r.source_sha256[:12]} not applied by Research after {int(age)}s ({r.state})"})
        if r.state == "blocked":
            alerts.append({"severity": "critical" if r.licence_status == "restricted" else "warning", "code": "delivery-blocked",
                           "subject": r.notice_id, "message": f"delivery blocked: {r.last_error_code}"})
        elif r.state == "retrying" and r.attempts >= max(2, s.research_rights_max_attempts // 2):
            alerts.append({"severity": "warning", "code": "delivery-retrying", "subject": r.notice_id,
                           "message": f"{r.attempts} attempts: {r.last_error_code}"})
    if rows and not enabled():
        alerts.append({"severity": "critical", "code": "delivery-disabled", "subject": "",
                       "message": "notices exist but Research delivery is not configured"})
    if enabled() and (last_ok is None or _age(now, last_ok) > 3 * s.research_rights_attest_interval_seconds):
        alerts.append({"severity": "critical", "code": "attestation-stale", "subject": "",
                       "message": "no attestation accepted by Research recently; Research will hold figures when its window passes"})
    for st in sync:
        if st.research_status in ("divergent", "unknown-to-workspace"):
            alerts.append({"severity": "critical", "code": f"source-{st.research_status}", "subject": st.source_sha256,
                           "message": f"owner {st.user_key}: Research reports {st.research_status}"})
        elif st.research_status == "research-behind" and not any(
                r.user_key == st.user_key and r.source_sha256 == st.source_sha256 for r in open_rows):
            # Behind with nothing in flight: Workspace believes it delivered what Research lacks.
            alerts.append({"severity": "warning", "code": "research-behind", "subject": st.source_sha256,
                           "message": f"Research applied {st.research_sequence}, Workspace issued {st.workspace_sequence}"})
    if enabled() and (hb is None or _age(now, hb) > 6 * s.worker_heartbeat_seconds):
        alerts.append({"severity": "critical", "code": "worker-stale", "subject": "", "message": "no Workspace worker heartbeat"})
    return {
        "schema": STATUS_SCHEMA, "generatedAt": now.isoformat(), "deliveryEnabled": enabled(), "counts": counts,
        "lagSeconds": {"applied24h": len(lag), "p50": _pct(lag, 0.5), "p95": _pct(lag, 0.95), "max": _pct(lag, 1.0)},
        "oldestOpenSeconds": max((_age(now, r.created_at) or 0 for r in open_rows), default=None),
        "unresolvedRestrictions": sum(1 for r in open_rows if r.licence_status == "restricted"),
        "lastAttestationAcceptedSecondsAgo": _age(now, last_ok), "workerHeartbeatSecondsAgo": _age(now, hb),
        "alerts": alerts, "items": items,
        "sync": [{"owner": st.user_key, "source": st.source_sha256, "status": st.research_status,
                  "researchSequence": st.research_sequence, "workspaceSequence": st.workspace_sequence,
                  "liveFigures": st.live_figures, "attestedSecondsAgo": _age(now, st.attested_at)} for st in sync[:200]],
    }


def require_operator(authorization: str | None = Header(default=None)) -> None:
    token = _token(get_settings().research_rights_ops_token_file)
    if not token:
        raise HTTPException(status_code=503, detail="The rights delivery dashboard is not configured.")
    if not authorization or not secrets.compare_digest(authorization.strip(), f"Bearer {token}"):
        raise HTTPException(status_code=401, detail="Operator authentication failed.")


NO_STORE = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"}


@router.get("/status")
def status_route(authorization: str | None = Header(default=None)):
    require_operator(authorization)
    with session_scope() as db:
        from fastapi.responses import JSONResponse
        return JSONResponse(status(db), headers=NO_STORE)


@router.post("/requeue")
def requeue_route(body: dict = Body(...), authorization: str | None = Header(default=None)):
    """Operator: send a blocked notice again after fixing its cause (credential, key, Research route)."""
    require_operator(authorization)
    notice_id = str(body.get("noticeId") or "")
    reason = str(body.get("reason") or "")[:500]
    if not reason:
        raise HTTPException(status_code=422, detail="A reason is required.")
    with session_scope() as db:
        row = db.get(ResearchRightsOutbox, notice_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Notice not found in the delivery outbox.")
        if row.state != "blocked":
            raise HTTPException(status_code=409, detail=f"Only blocked notices are re-queued (state {row.state}).")
        row.state, row.attempts, row.next_attempt_at, row.updated_at = "queued", 0, _now(), _now()
        _event(db, "requeue", "operator", notice_id=row.notice_id, user_key=row.user_key, detail={"reason": reason})
        db.commit()
        return {"noticeId": notice_id, "state": "queued"}


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_route(authorization: str | None = Header(default=None)):
    require_operator(authorization)
    with session_scope() as db:
        st = status(db)
    return HTMLResponse(render_dashboard(st), headers={
        **NO_STORE, "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'",
        "Referrer-Policy": "no-referrer"})


def render_dashboard(st: dict) -> str:
    e = lambda v: html.escape("" if v is None else str(v))  # noqa: E731
    sev = {"critical": "crit", "warning": "warn"}
    counts = "".join(f'<div class="tile s-{e(k)}"><b>{e(v)}</b><span>{e(k)}</span></div>' for k, v in st["counts"].items())
    lag = st["lagSeconds"]
    alerts = "".join(f'<li class="{sev.get(a["severity"], "")}"><b>{e(a["severity"])}</b> {e(a["code"])} '
                     f'<code>{e(a.get("subject", "")[:16])}</code> {e(a["message"])}</li>' for a in st["alerts"]) \
        or '<li class="ok">No alerts.</li>'
    rows = "".join(
        f'<tr class="st-{e(i["state"])}"><td><code>{e(i["noticeId"][:14])}</code></td><td>{e(i["owner"])}</td>'
        f'<td><code>{e(i["source"][:12])}</code></td><td>{e(i["sequence"])}</td><td>{e(i["licenceStatus"])}</td>'
        f'<td>{e(i["state"])}</td><td>{e(i["attempts"])}</td><td>{e(i["ageSeconds"])}</td><td>{e(i["nextAttemptInSeconds"])}</td>'
        f'<td>{e(i["lastHttpStatus"])} {e(i["lastError"])}</td><td>{"gap" if i["chainGap"] else ""}{" replay" if i["replayed"] else ""}</td></tr>'
        for i in st["items"]) or '<tr><td colspan="11">No notices.</td></tr>'
    sync = "".join(
        f'<tr class="sy-{e(x["status"])}"><td>{e(x["owner"])}</td><td><code>{e(x["source"][:12])}</code></td><td>{e(x["status"])}</td>'
        f'<td>{e(x["researchSequence"])} / {e(x["workspaceSequence"])}</td><td>{e(x["liveFigures"])}</td><td>{e(x["attestedSecondsAgo"])}</td></tr>'
        for x in st["sync"]) or '<tr><td colspan="6">No reconciliation yet.</td></tr>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="15"><title>Rights delivery</title><style>
body{{font:14px/1.45 system-ui,sans-serif;margin:16px;color:#1b2a36;background:#fbfaf7}}h1{{font-size:20px;margin:0 0 4px}}
.meta{{color:#5f6b75;margin:0 0 12px}}.tiles{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}}
.tile{{border:1px solid #c8c8c8;border-radius:6px;padding:8px 12px;min-width:92px;background:#fff}}.tile b{{display:block;font-size:22px}}
.s-blocked b,.crit{{color:#a1251b}}.s-retrying b,.warn{{color:#8a5a00}}.s-applied b{{color:#1f5e2e}}
ul{{padding-left:18px}}li.ok{{color:#1f5e2e}}table{{border-collapse:collapse;width:100%;margin:8px 0 20px;background:#fff}}
th,td{{border-bottom:1px solid #e3e1db;padding:4px 6px;text-align:left;vertical-align:top}}th{{background:#f1efe9}}
.wrap{{overflow-x:auto}}.st-blocked td{{background:#fbeceb}}.st-retrying td{{background:#fdf5e6}}
.sy-research-behind td,.sy-divergent td,.sy-unknown-to-workspace td{{background:#fbeceb}}</style></head><body>
<h1>Source-rights delivery to Research</h1><p class="meta">Private operator view. Generated {e(st["generatedAt"])}.
Delivery {"enabled" if st["deliveryEnabled"] else "DISABLED"}. Worker heartbeat {e(st["workerHeartbeatSecondsAgo"])}s ago.
Last accepted attestation {e(st["lastAttestationAcceptedSecondsAgo"])}s ago.</p>
<div class="tiles">{counts}<div class="tile"><b>{e(st["unresolvedRestrictions"])}</b><span>unresolved restrictions</span></div>
<div class="tile"><b>{e(lag["p50"])}</b><span>lag p50 s</span></div><div class="tile"><b>{e(lag["p95"])}</b><span>lag p95 s</span></div>
<div class="tile"><b>{e(st["oldestOpenSeconds"])}</b><span>oldest open s</span></div></div>
<h2>Alerts</h2><ul>{alerts}</ul>
<h2>Notices</h2><div class="wrap"><table><thead><tr><th>Notice</th><th>Owner</th><th>Source</th><th>Seq</th><th>Status</th><th>Delivery</th>
<th>Attempts</th><th>Age s</th><th>Next s</th><th>Last answer</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Research reconciliation</h2><div class="wrap"><table><thead><tr><th>Owner</th><th>Source</th><th>Research</th><th>Applied / issued</th>
<th>Live figures</th><th>Attested s ago</th></tr></thead><tbody>{sync}</tbody></table></div></body></html>"""
