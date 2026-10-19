"""Workspace 3.84.3: read-only, fail-closed ECDF Lab figure SVG adapter.

This adapter preserves the raw Lab response and identifies it as caller-supplied,
not authenticated or independently certified. No Lab network calls or writes.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from html import escape
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix='/v1/lab-publication/v3843', tags=['lab-publication-v3843'])

class Envelope(BaseModel):
    labResponse: dict[str, Any]
    sourceObjectId: str = Field(min_length=1, max_length=160)
    sourceFingerprint: str = Field(min_length=1, max_length=256)
    caption: str = Field(min_length=1, max_length=800)
    evidenceStatus: Literal['illustrative','modeled','observed']
    model_config = ConfigDict(extra='forbid')

def guard():
    if os.getenv('SC_WORKSPACE_LAB_PUBLICATION_V3843_ENABLED') != '1':
        raise HTTPException(503, 'Lab publication adapter disabled')

def _canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)

def render(payload: Envelope) -> dict:
    src = payload.labResponse
    if len(_canonical(src).encode()) > 350_000:
        raise HTTPException(413,'Lab figure response exceeds size bound')
    # A source fingerprint supplied by a caller is a reference, not attestation.
    if src.get('ok') is not True or not isinstance(src.get('fingerprint'), str) or not src['fingerprint']:
        raise HTTPException(422,'Missing Lab figure response marker or fingerprint')
    if src.get('graphic_type') != 'distribution' or not isinstance(src.get('spec'),dict):
        raise HTTPException(422,'Unsupported Lab graphic type')
    spec=src['spec']
    if spec.get('kind') != 'ecdf':
        raise HTTPException(422,'Only the Lab ECDF figure primitive is certified in v3.84.3')
    if any(spec.get(k) for k in ('bars','bins','boxes','violins')):
        raise HTTPException(422,'Unsupported mixed figure primitives')
    series=spec.get('series')
    if not isinstance(series,list) or not 1<=len(series)<=8:
        raise HTTPException(422,'Invalid series collection')
    rows=[]
    for s in series:
        if not isinstance(s,dict) or not isinstance(s.get('points'),list) or not 2<=len(s['points'])<=5000:
            raise HTTPException(422,'Invalid ECDF series')
        pts=[]
        for pt in s['points']:
            if not isinstance(pt,dict) or type(pt.get('x')) not in (float,int) or type(pt.get('y')) not in (float,int):
                raise HTTPException(422,'Invalid scientific coordinate')
            x,y=float(pt['x']),float(pt['y'])
            if not math.isfinite(x) or not math.isfinite(y) or y<0 or y>1:
                raise HTTPException(422,'ECDF values must be finite and probabilities in [0,1]')
            pts.append((x,y))
        if any(pts[i][0]<pts[i-1][0] or pts[i][1]<pts[i-1][1] for i in range(1,len(pts))):
            raise HTTPException(422,'ECDF coordinates must be nondecreasing')
        rows.append((str(s.get('label','ECDF'))[:120],pts))
    axes=spec.get('axes',{})
    if not isinstance(axes,dict) or not isinstance(axes.get('x'),dict) or not isinstance(axes.get('y'),dict):
        raise HTTPException(422,'Missing axes')
    title=str(spec.get('title','')).strip()
    if not title or len(title)>180:
        raise HTTPException(422,'Invalid title')
    xlab=str(axes['x'].get('label',''))[:100]
    ylab=str(axes['y'].get('label',''))[:100]
    xmin=min(x for _,pts in rows for x,_ in pts)
    xmax=max(x for _,pts in rows for x,_ in pts)
    delta=xmax-xmin or 1.0
    colors=['#111111','#aa182b','#007a3d','#334d6e']
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 560" role="img">',
           '<rect width="860" height="560" fill="white"/>',
           '<path d="M85 85 V445 H790" fill="none" stroke="#222" stroke-width="2"/>',
           f'<text x="85" y="45" font-family="sans-serif" font-size="21">{escape(title)}</text>',
           f'<text x="420" y="491" font-family="sans-serif" font-size="14">{escape(xlab)}</text>',
           f'<text x="90" y="72" font-family="sans-serif" font-size="14">{escape(ylab)}</text>']
    for idx,(label,pts) in enumerate(rows):
        coords=' '.join(f'{85+705*(x-xmin)/delta:.3f},{445-350*y:.3f}' for x,y in pts)
        color=colors[idx%len(colors)]
        parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        parts.append(f'<text x="95" y="{515+idx*12}" font-family="sans-serif" font-size="11" fill="{color}">{escape(label)}</text>')
    digest=hashlib.sha256(_canonical(src).encode()).hexdigest()
    parts.append(f'<metadata>Workspace digest {digest}; Lab fingerprint {escape(src["fingerprint"])}; caller source {escape(payload.sourceObjectId)}; evidence {escape(payload.evidenceStatus)}</metadata>')
    parts.append('</svg>')
    return {'schema':'sc-workspace-lab-publication/1.0', 'mimeType':'image/svg+xml',
            'svg':''.join(parts),'caption':payload.caption,'evidenceStatus':payload.evidenceStatus,
            'sourceObjectId':payload.sourceObjectId,'sourceFingerprint':payload.sourceFingerprint,
            'labFigureFingerprint':src['fingerprint'],'workspaceResponseDigest':digest,
            'labOriginAuthenticated':False,'labFingerprintVerified':False,
            'scientificVerificationPerformed':False,'manuscriptModified':False,'writesPerformed':False}

@router.get('/status')
def status():
    return {'schema':'sc-workspace-lab-publication-status/1.0', 'enabled':os.getenv('SC_WORKSPACE_LAB_PUBLICATION_V3843_ENABLED')=='1', 'supported':['distribution/ecdf'], 'writesPerformed':False}

@router.post('/render/ecdf/svg')
def render_ecdf_svg(payload:Envelope, _=Depends(guard)):
    try:
        return render(payload)
    except (OverflowError, ValueError, TypeError) as exc:
        raise HTTPException(422,'Invalid Lab figure response') from exc
