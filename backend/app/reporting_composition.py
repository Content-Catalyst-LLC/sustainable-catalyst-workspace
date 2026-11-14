"""Bound equation/table publication panels. No eval, CAS, or network calls."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import textwrap
from typing import Literal
from xml.etree import ElementTree as ET
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Strict(BaseModel):
    model_config=ConfigDict(extra='forbid')

class Binding(Strict):
    artifact_id: str = Field(min_length=1,max_length=160)
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    source_revision: int = Field(ge=1)
    execution_ref: str = Field(min_length=1,max_length=300)
    field: Literal['latex','exactText','decimalText']

class Equation(Strict):
    latex: str = Field(min_length=1,max_length=2000)
    alt_text: str = Field(min_length=1,max_length=400)
    mode: Literal['inline','display'] = 'display'
    binding: Binding | None = None
    citations: list[str] = Field(default_factory=list,max_length=10)

class Column(Strict):
    label: str = Field(min_length=1,max_length=30)
    unit: str = Field(min_length=1,max_length=24)
    definition: str = Field(min_length=1,max_length=160)
    significant_figures: int | None = Field(default=None,ge=1,le=30)

class Cell(Strict):
    value: str | None = Field(default=None,max_length=60)
    binding: Binding | None = None
    uncertainty: str = Field(default='not quantified',max_length=60)
    citations: list[str] = Field(default_factory=list,max_length=10)
    @model_validator(mode='after')
    def one_value(self):
        if (self.value is None)==(self.binding is None):
            raise ValueError('Exactly one explicit text value or immutable binding is required')
        return self

class Table(Strict):
    title: str = Field(min_length=1,max_length=120)
    columns: list[Column] = Field(min_length=1,max_length=4)
    rows: list[list[Cell]] = Field(min_length=1,max_length=12)
    @model_validator(mode='after')
    def rectangular(self):
        if any(len(row)!=len(self.columns) for row in self.rows):
            raise ValueError('Table rows must match the declared columns')
        return self

class Composition(Strict):
    equations: list[Equation] = Field(default_factory=list,max_length=4)
    table: Table | None = None
    method_notes: str = Field(default='',max_length=1200)
    source_citations: list[str] = Field(default_factory=list,max_length=12)


def render_math(latex,mode):
    worker=Path(__file__).resolve().parent.parent/'reporting_math'/'render.cjs'
    try:
        result=subprocess.run([os.getenv('SC_REPORTING_NODE_BIN','node'),'--max-old-space-size=128',str(worker)],
            input=json.dumps({'latex':latex,'mode':mode}),text=True,capture_output=True,timeout=8,
            cwd=worker.parent,env={k:v for k,v in os.environ.items() if k in ('PATH','SYSTEMROOT','TMPDIR')})
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise HTTPException(503,'Optional math SVG runtime unavailable or timed out.') from exc
    if result.returncode:
        if 'Cannot find module' in result.stderr:
            raise HTTPException(503,'Install the pinned optional reporting_math dependencies.')
        raise HTTPException(422,'LaTeX rejected by the bounded base/AMS typesetter.')
    if len(result.stdout)>1_000_000:
        raise HTTPException(413,'Equation SVG output exceeds the typesetting limit.')
    root=ET.fromstring(result.stdout)
    for node in root.iter():
        if node.tag.rsplit('}',1)[-1] not in ('svg','g','path','rect','text','title','desc','defs','use'):
            raise HTTPException(422,'Unsafe equation SVG element.')
        for key,value in node.attrib.items():
            if key.startswith('on') or (key.rsplit('}',1)[-1]=='href' and not value.startswith('#')):
                raise HTTPException(422,'Unsafe equation SVG reference.')
    return root


def resolve_binding(binding,loader):
    obj=loader(binding.model_dump())
    if obj.get('schema')!='sc-workbench-math-object/1.0':
        raise HTTPException(422,'Binding requires an existing Workbench math-object export.')
    expected=hashlib.sha256(json.dumps({k:v for k,v in obj.items() if k!='mathObjectHash'},
        sort_keys=True,separators=(',',':'),ensure_ascii=False,default=str).encode()).hexdigest()
    if obj.get('mathObjectHash')!=expected:
        raise HTTPException(409,'Workbench math-object integrity mismatch.')
    value=obj.get(binding.field)
    if not isinstance(value,str) or len(value)>2000:
        raise HTTPException(422,'Bound result field missing or exceeds limit.')
    return value,{'reference':binding.model_dump(),'exactText':obj.get('exactText'),
        'decimalText':obj.get('decimalText'),'latex':obj.get('latex'),
        'freeSymbols':obj.get('freeSymbols'), 'precision':obj.get('precision'),
        'mathObjectHash':obj['mathObjectHash'],'origin_authenticated':False,
        'execution_ref_attested':False,'measured_result':False}


def compose(svg,composition,loader):
    if not composition or not (composition.equations or composition.table or composition.method_notes):
        return svg,[]
    if svg is None:
        raise HTTPException(422,'Native Lab scene needs a runtime overlay adapter; no synthetic scene rendering.')
    ns='{http://www.w3.org/2000/svg}'
    root=ET.fromstring(svg);inspections=[]
    def text(x,y,value,size=14,weight=None):
        attr={'x':str(x),'y':str(y),'font-family':'sans-serif','font-size':str(size)}
        if weight:attr['font-weight']=weight
        node=ET.SubElement(root,ns+'text',attr);node.text=str(value)
    def wrapped(x,y,value,width=95,size=14):
        for line in textwrap.wrap(str(value),width=width) or ['']:
            text(x,y,line,size);y+=20
        return y
    y=float(root.attrib['viewBox'].split()[3])+30
    text(24,y,'Analytical notation and results | not field-verified measurements',16,'bold');y+=30
    for eq in composition.equations:
        value=eq.latex
        if eq.binding:
            bound,inspection=resolve_binding(eq.binding,loader);inspections.append(inspection)
            if bound!=value:
                raise HTTPException(409,'Equation definition differs from immutable bound result.')
        node=render_math(value,eq.mode)
        view=[float(v) for v in node.attrib['viewBox'].split()]
        scale=min(0.032,760/max(view[2],1),120/max(view[3],1))
        height=max(32,view[3]*scale)
        # Flatten the SVG viewport into an explicit group transform. This keeps
        # MathJax paths aligned identically in browsers and the PDF converter.
        group=ET.SubElement(root,ns+'g',{'role':'img','aria-label':eq.alt_text,
            'transform':f'translate({40+(760-view[2]*scale)/2} {y}) scale({scale}) translate({-view[0]} {-view[1]})'})
        ET.SubElement(group,ns+'title').text=eq.alt_text
        for child in node:group.append(child)
        y+=height+25
        y=wrapped(24,y,eq.alt_text)
        if eq.citations:y=wrapped(24,y,'References: '+'; '.join(eq.citations))
    table=composition.table
    if table:
        text(24,y,table.title,16,'bold');y+=28
        width=812/len(table.columns)
        for i,col in enumerate(table.columns):
            text(24+i*width,y,col.label,14,'bold')
            text(24+i*width,y+20,'Unit: '+col.unit,12)
        y+=48
        for row in table.rows:
            start=y;max_y=y
            for i,cell in enumerate(row):
                value=cell.value
                if cell.binding:
                    value,inspection=resolve_binding(cell.binding,loader);inspections.append(inspection)
                cell_y=wrapped(24+i*width,y,value,width=max(12,int(width/8)),size=14)
                cell_y=wrapped(24+i*width,cell_y,'Uncertainty: '+cell.uncertainty,width=max(12,int(width/7)),size=11)
                if cell.citations:cell_y=wrapped(24+i*width,cell_y,'Refs: '+'; '.join(cell.citations),width=max(12,int(width/7)),size=11)
                max_y=max(max_y,cell_y)
            ET.SubElement(root,ns+'path',{'d':f'M24 {max_y+2} H836','stroke':'#cedbd5'})
            y=max_y+20
        for col in table.columns:
            y=wrapped(24,y,f'{col.label}: {col.definition}; significant figures: {col.significant_figures or "source precision preserved"}.')
    if composition.method_notes:
        y+=15;text(24,y,'Method and inference boundaries',16,'bold');y+=24
        y=wrapped(24,y,composition.method_notes)
    if composition.source_citations:
        y+=12;text(24,y,'Source references',16,'bold');y+=24
        for citation in composition.source_citations:y=wrapped(24,y,citation)
    # The same white vector composition feeds browser PNG and print-to-PDF.
    background=ET.Element(ns+'rect',{'x':'0','y':'0','width':'860','height':str(y+25),'fill':'white'})
    root.insert(0,background);root.set('viewBox',f'0 0 860 {y+25}');root.set('height',str(y+25))
    root.set('role','img');root.set('aria-label','Scientific figure, equations, results table, methodology and source references')
    return ET.tostring(root,encoding='unicode'),inspections
