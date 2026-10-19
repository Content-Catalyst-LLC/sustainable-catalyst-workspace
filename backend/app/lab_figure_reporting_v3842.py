"""Workspace v3.84.2: deterministic, read-only Lab figure and 4D reporting preview.

Lab owns scientific computations, dataset selection and semantic claims. These
endpoints accept only explicit Lab-generated export envelopes, never simulate,
write manuscripts, or query private projects. They are disabled by default.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from html import escape
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter(prefix='/v1/lab-figure-reporting/v3842', tags=['lab-figure-reporting-v3842'])
MAX_POINTS = 5000
MAX_FRAMES = 48
MAX_SERIES = 12

class Datum(BaseModel):
    x: float
    y: float

class Series(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    points: list[Datum] = Field(min_length=1, max_length=MAX_POINTS)

class Frame(BaseModel):
    time: str = Field(min_length=1, max_length=80)
    points: list[Datum] = Field(min_length=1, max_length=MAX_POINTS)

class Provenance(BaseModel):
    labObjectId: str = Field(min_length=1,max_length=160)
    labObjectHash: str = Field(pattern=r'^[a-f0-9]{64}$')
    labRelease: str = Field(min_length=1,max_length=80)
    method: str = Field(min_length=1,max_length=160)
    seed: int | None = None
    assessment: Literal['illustrative','simulated','observed','verified']
    sourceDescription: str = Field(min_length=1,max_length=400)
    model_config = ConfigDict(extra='forbid')

class Figure(BaseModel):
    schemaName: Literal['sc-lab-report-figure/1.0']
    title: str = Field(min_length=1,max_length=180)
    xLabel: str = Field(min_length=1,max_length=80)
    yLabel: str = Field(min_length=1,max_length=80)
    caption: str = Field(min_length=1,max_length=800)
    series: list[Series] = Field(min_length=1,max_length=MAX_SERIES)
    provenance: Provenance
    model_config = ConfigDict(extra='forbid')

class Scene(BaseModel):
    schemaName: Literal['sc-lab-report-scene/1.0']
    title: str = Field(min_length=1,max_length=180)
    xLabel: str = Field(min_length=1,max_length=80)
    yLabel: str = Field(min_length=1,max_length=80)
    zLabel: str = Field(min_length=1,max_length=80)
    tLabel: str = Field(min_length=1,max_length=80)
    caption: str = Field(min_length=1,max_length=800)
    frames: list[Frame] = Field(min_length=1,max_length=MAX_FRAMES)
    provenance: Provenance
    model_config = ConfigDict(extra='forbid')

def _guard():
    if os.getenv('SC_WORKSPACE_LAB_FIGURE_REPORTING_ENABLED','') != '1':
        raise HTTPException(503, 'Lab figure reporting not enabled')


def _finite(points):
    if not all(math.isfinite(p.x) and math.isfinite(p.y) for p in points):
        raise HTTPException(422,'Non-finite scientific coordinates')


def _digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def _result(kind, obj):
    # A projection suitable for the browser. Never says the input has been
    # independently validated; provenance is declarative until Lab verified.
    src=obj.model_dump(exclude_none=True)
    for row in (obj.series if kind=='figure' else obj.frames):
        _finite(row.points)
    return {'schema':'sc-workspace-lab-report-preview/1.0', 'kind':kind,
            'payload':src, 'workspaceDigest':_digest(src),
            'labAuthorityPreserved':True, 'scientificVerificationPerformed':False,
            'writesPerformed':False, 'manuscriptModified':False,
            'staticExportAvailable':True}


def _svg(result, frame_index=0):
    obj=result['payload']; kind=result['kind']
    groups=obj['series'] if kind=='figure' else [obj['frames'][frame_index]]
    allp=[p for g in groups for p in g['points']]
    x0=min(p['x'] for p in allp);x1=max(p['x'] for p in allp)
    y0=min(p['y'] for p in allp);y1=max(p['y'] for p in allp)
    dx=x1-x0 or 1.;dy=y1-y0 or 1.
    def sx(p):return 90+690*(p['x']-x0)/dx
    def sy(p):return 430-330*(p['y']-y0)/dy
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 540" role="img">',
         '<rect width="860" height="540" fill="white"/>',
         '<g stroke="#222" stroke-width="1.8"><path d="M90 80 V430 H790" fill="none"/></g>',
         f'<text x="90" y="46" font-family="sans-serif" font-size="20">{escape(obj["title"])}</text>',
         f'<text x="400" y="480" font-family="sans-serif" font-size="14">{escape(obj["xLabel"])}</text>',
         f'<text x="95" y="70" font-family="sans-serif" font-size="14">{escape(obj["yLabel"])}</text>']
    palette=['#111111','#aa182b','#007a3d','#334d6e','#7951a8']
    for i,g in enumerate(groups):
        pts=' '.join(f'{sx(p):.2f},{sy(p):.2f}' for p in g['points'])
        color=palette[i % len(palette)]
        if len(g['points'])>1:
            out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for p in g['points']:
            out.append(f'<circle cx="{sx(p):.2f}" cy="{sy(p):.2f}" r="3" fill="{color}"/>')
        label=g.get('label',g.get('time',''))
        out.append(f'<text x="95" y="{500+i*14}" font-family="sans-serif" font-size="11">{escape(label)}</text>')
    prov=obj['provenance']
    out.append(f'<metadata>Lab object {escape(prov["labObjectId"])}; hash {escape(prov["labObjectHash"])}; {escape(prov["assessment"])}</metadata>')
    out.append('</svg>')
    return ''.join(out)

@router.get('/status')
def status():
    return {'schema':'sc-workspace-lab-figure-reporting-status/1.0','enabled':os.getenv('SC_WORKSPACE_LAB_FIGURE_REPORTING_ENABLED','')=='1',
            'labIsScientificAuthority':True,'automaticLabCompute':False,'persistentWrites':False}

@router.post('/figure/preview')
def figure_preview(payload:Figure, _=Depends(_guard)):
    return _result('figure',payload)

@router.post('/scene/preview')
def scene_preview(payload:Scene, _=Depends(_guard)):
    return _result('scene',payload)

class ExportRequest(BaseModel):
    kind: Literal['figure','scene']
    figure: Figure | None = None
    scene: Scene | None = None
    frameIndex: int = Field(default=0,ge=0,lt=MAX_FRAMES)

@router.post('/export/svg')
def svg_export(payload:ExportRequest, _=Depends(_guard)):
    if payload.kind=='figure' and payload.figure is not None and payload.scene is None:
        r=_result('figure',payload.figure)
    elif payload.kind=='scene' and payload.scene is not None and payload.figure is None:
        r=_result('scene',payload.scene)
        if payload.frameIndex>=len(payload.scene.frames):
            raise HTTPException(422,'Frame index out of range')
    else:
        raise HTTPException(422,'Exactly one matching object required')
    return {'schema':'sc-workspace-lab-figure-svg-export/1.0', 'svg':_svg(r,payload.frameIndex),
            'mimeType':'image/svg+xml','workspaceDigest':r['workspaceDigest'],
            'provenance':r['payload']['provenance'],
            'scientificVerificationPerformed':False,'writesPerformed':False}
