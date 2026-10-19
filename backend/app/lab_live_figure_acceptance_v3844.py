"""Workspace 3.84.4: opt-in loopback Lab ECDF acceptance and integrity check.

Scientific input is explicitly supplied by the authorized service client. Lab owns
normalization and ECDF computation; Workspace only verifies and renders. No data
is read from private project stores or written to manuscripts/databases.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .lab_publication_adapter_v3843 import Envelope, render

router = APIRouter(prefix='/v1/lab-publication/v3844', tags=['lab-live-figure-v3844'])
LAB_ENDPOINT = 'http://127.0.0.1:8092/v1/advanced-statistical-uncertainty-graphics/distributions/figure'
MAX_BODY = 350_000

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class RequestFigure(BaseModel):
    sourceObjectId: str = Field(min_length=1, max_length=160)
    sourceFingerprint: str = Field(min_length=1, max_length=256)
    title: str = Field(min_length=1, max_length=180)
    xLabel: str = Field(min_length=1, max_length=100)
    caption: str = Field(min_length=1, max_length=800)
    units: str = Field(min_length=1, max_length=80)
    evidenceStatus: Literal['illustrative','modeled','observed']
    samples: list[float] = Field(min_length=2, max_length=1500)
    model_config = ConfigDict(extra='forbid')

def guard():
    if os.getenv('SC_WORKSPACE_LAB_LIVE_V3844_ENABLED') != '1':
        raise HTTPException(503, 'Live Lab figure acceptance disabled')
    if os.getenv('SC_WORKSPACE_LAB_LIVE_EXECUTION_APPROVED') != '1':
        raise HTTPException(503, 'Explicit live Lab execution approval required')

def _stable(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False, default=str)

def _verify_lab(result: dict):
    if not isinstance(result, dict) or result.get('schema') != 'sc-lab-advanced-statistical-figure/0.115.0':
        raise HTTPException(502, 'Unsupported Lab figure schema')
    fingerprint = result.get('fingerprint')
    if not isinstance(fingerprint, str) or len(fingerprint) != 64 or any(c not in '0123456789abcdef' for c in fingerprint):
        raise HTTPException(502, 'Missing Lab SHA256 fingerprint')
    expected = hashlib.sha256(_stable({k:v for k,v in result.items() if k!='fingerprint'}).encode()).hexdigest()
    if fingerprint != expected:
        raise HTTPException(502, 'Lab response fingerprint mismatch')
    if result.get('graphic_type') != 'ecdf' or result.get('spec', {}).get('kind') != 'ecdf':
        raise HTTPException(502, 'Unexpected Lab figure primitive')
    if result.get('boundaries', {}).get('automatic_scientific_validity_certification') is not False:
        raise HTTPException(502, 'Lab scientific boundary missing')

def _lab_call(body: dict) -> dict:
    payload = _stable(body).encode('utf-8')
    opener = build_opener(ProxyHandler({}), NoRedirect)
    req = Request(LAB_ENDPOINT, data=payload, headers={'Content-Type':'application/json','Accept':'application/json'}, method='POST')
    try:
        with opener.open(req, timeout=12) as resp:
            if resp.status != 200:
                raise HTTPException(502, 'Lab scientific endpoint unavailable')
            raw = resp.read(MAX_BODY+1)
            if len(raw) > MAX_BODY:
                raise HTTPException(502, 'Lab response exceeds size limit')
            return json.loads(raw)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(502, 'Lab scientific endpoint unavailable or returned invalid JSON') from exc

def accept(payload: RequestFigure, *, loader=None) -> dict:
    if any(not math.isfinite(v) for v in payload.samples):
        raise HTTPException(422, 'Non-finite sample value')
    # Lab does not infer truth status from sample semantics. This metadata is supplied by client.
    semantics = {'illustrative':'custom', 'modeled':'ensemble', 'observed':'observed'}[payload.evidenceStatus]
    body = {'mode':'ecdf', 'samples':payload.samples, 'semantics':semantics,
            'title':payload.title, 'x_label':payload.xLabel, 'units':payload.units, 'bins':20}
    result = (loader or _lab_call)(body)
    _verify_lab(result)
    try:
        output = render(Envelope(labResponse=result, sourceObjectId=payload.sourceObjectId,
                  sourceFingerprint=payload.sourceFingerprint, caption=payload.caption,
                  evidenceStatus=payload.evidenceStatus))
    except HTTPException as exc:
        raise HTTPException(502, 'Lab figure response incompatible with Workspace renderer') from exc
    output.update({'schema':'sc-workspace-lab-live-figure-acceptance/1.0',
                   'labOriginAuthenticated':False,  # loopback transport is not cryptographic service identity
                   'labResponseIntegrityVerified':True,
                   'labRequestEndpoint':'advanced-statistical-uncertainty-graphics/distributions/figure',
                   'labFingerprintVerified':True, 'sampleCount':len(payload.samples),
                   'scientificVerificationPerformed':False,'writesPerformed':False,
                   'manuscriptModified':False})
    return output

@router.get('/status')
def status():
    return {'schema':'sc-workspace-lab-live-figure-status/1.0',
            'enabled':os.getenv('SC_WORKSPACE_LAB_LIVE_V3844_ENABLED')=='1',
            'executionApproved':os.getenv('SC_WORKSPACE_LAB_LIVE_EXECUTION_APPROVED')=='1',
            'endpointIsFixedLoopback':True,'automaticExecution':False,'persistentWrites':False}

@router.post('/ecdf/accept')
def accept_endpoint(payload:RequestFigure, _=Depends(guard)):
    return accept(payload)
