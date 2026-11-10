"""SC-SIM-01 G9: predictive, probabilistic and forensic result bindings checked against runtime receipts.

A binding whose resultRef names a Workspace ExecutionRun (``workspace-run:<runId>``) is verified server-side:
the run must be executed-verified and resultFingerprint must equal the sha256 of one of its runtime receipt
results. Any other reference is recorded as ``client-asserted`` and is exploratory, never verified evidence.
The verdict is written by the server under a reserved metadata key that clients cannot set.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy import select

from .models import ExecutionRunOutput
from .registry import get_execution_run

RUN_PREFIX = "workspace-run:"
RESERVED_KEY = "receiptVerification"
SCHEMA = "sc-workspace-result-receipt-verification/1.0"


def _refuse(code: str, status: int = 409, **extra: Any) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, **extra})


def verify_result_ref(db, user_key: str, project_id: str, result_ref: str, fingerprint: str) -> dict[str, Any]:
    if not result_ref.startswith(RUN_PREFIX):
        return {"schema": SCHEMA, "status": "client-asserted", "evidence": "exploratory",
                "reason": "resultRef does not name a Workspace ExecutionRun"}
    from .research_exports import verification_for_run  # late: research_exports imports most of the app
    run_id = result_ref[len(RUN_PREFIX):].strip()
    run = get_execution_run(db, user_key, run_id)
    # The same answer for absent, foreign and other-project runs.
    if run is None or (project_id and run.project_id != project_id):
        raise _refuse("result-run-not-found", 404, runId=run_id)
    outputs = list(db.scalars(select(ExecutionRunOutput).where(
        ExecutionRunOutput.user_key == user_key, ExecutionRunOutput.run_id == run_id)).all())
    v = verification_for_run(db, user_key, run, outputs)
    if v["status"] != "executed-verified":
        raise _refuse("result-run-not-executed-verified", runId=run_id, status=v["status"])
    receipt = next((r for r in v["runtimeReceipts"] if r["resultSha256"] == fingerprint.strip().lower()), None)
    if receipt is None:
        raise _refuse("result-fingerprint-does-not-match-receipt", runId=run_id)
    return {"schema": SCHEMA, "status": "receipt-verified", "evidence": "executed-verified", "runId": run_id,
            "receiptId": receipt["receiptId"], "resultSha256": receipt["resultSha256"],
            "resultArtifactId": receipt["resultArtifactId"], "operation": receipt["operation"],
            "runtime": receipt["runtime"], "inputLineage": v["inputLineage"]}


def with_verification(metadata: dict[str, Any] | None, verification: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in (metadata or {}).items() if k != RESERVED_KEY}
    out[RESERVED_KEY] = verification
    return out


def client_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Client metadata without the reserved key, as hashed into the binding fingerprint."""
    return {k: v for k, v in (metadata or {}).items() if k != RESERVED_KEY}


def verification_of(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Bindings stored before SC-SIM-01 G9 carry no server verdict."""
    found = (metadata or {}).get(RESERVED_KEY)
    return found if isinstance(found, dict) else {"schema": SCHEMA, "status": "unverified-legacy", "evidence": "exploratory"}
