"""SC-PUB-M1 — Research approval desk (owner- and approver-facing Workspace page).

A same-origin page over the authenticated `/v1/research-approvals` API: the approver queue, the
requests a person raised, and the requests on their own projects. Approving shows the exact
revision (subject reference and content hash), requires the person to confirm it, and — when the
API answers `step-up-required` — sends them through a fresh SC Identity sign-in and asks them to
confirm the same revision again on return. Decisions are made only by the API; this module serves
static files with a strict Content-Security-Policy (no inline script, same-origin connections).
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

router = APIRouter(prefix="/v1/desk", tags=["SC-PUB-M1 approval desk"])

STATIC = Path(__file__).resolve().parent / "static" / "approval_desk"
ASSETS = {"approval-desk.js": "text/javascript; charset=utf-8", "approval-desk.css": "text/css; charset=utf-8"}
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; "
       "form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
HEADERS = {"Content-Security-Policy": CSP, "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
           "X-Content-Type-Options": "nosniff", "Cross-Origin-Opener-Policy": "same-origin"}


def _file(name: str, media_type: str) -> Response:
    return Response((STATIC / name).read_bytes(), media_type=media_type, headers=HEADERS)


@router.get("/approvals")
def approval_desk_page():
    return _file("index.html", "text/html; charset=utf-8")


@router.get("/assets/{name}")
def approval_desk_asset(name: str):
    if name not in ASSETS:
        raise HTTPException(status_code=404, detail="Not Found")
    return _file(name, ASSETS[name])
