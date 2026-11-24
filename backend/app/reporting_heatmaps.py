"""Read-only Lab heatmap grammar adapter using the pinned Lab SVG renderer.

Only regular numeric grids (possibly masked/sparse) are supported. No
correlations, interpolation, reprojection, raster acquisition or 5D is computed.
"""
import json
import math
import os
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET
from fastapi import HTTPException

PALETTES={'sequential':['#440154','#443983','#31688e','#21918c','#35b779','#90d743','#fde725'],
          'diverging':['#2166ac','#67a9cf','#d1e5f0','#f7f7f7','#fddbc7','#ef8a62','#b2182b']}


def _axis(values):
    if not isinstance(values,list) or not 2<=len(values)<=200:
        raise HTTPException(422,'Heatmap axis must contain 2–200 declared numeric centers.')
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
        raise HTTPException(422,'Heatmap axes must be finite.')
    step=values[1]-values[0]
    if step<=0 or any(not math.isclose(values[i]-values[i-1],step,rel_tol=1e-7,abs_tol=1e-9) for i in range(1,len(values))):
        raise HTTPException(422,'This Lab adapter requires increasing, regularly spaced centers; no silent resampling.')
    return [values[0]-step/2,values[-1]+step/2]


def render_heatmap(obj,ref):
    if obj.get('schema')!='sc-lab-scientific-visualization/1.0' or obj.get('kind')!='heatmap':
        raise HTTPException(422,'Existing Lab numeric heatmap schema required.')
    xs,ys=obj.get('xValues'),obj.get('yValues')
    xd,yd=_axis(xs),_axis(ys)
    cells=obj.get('cells')
    if not isinstance(cells,list) or not 1<=len(cells)<=10000:
        raise HTTPException(422,'Heatmap requires 1–10000 explicit cells.')
    seen=set();clean=[]
    for cell in cells:
        if not isinstance(cell,dict):raise HTTPException(422,'Invalid heatmap cell.')
        xi,yi,z=cell.get('xIndex'),cell.get('yIndex'),cell.get('z')
        if type(xi) is not int or type(yi) is not int or not 0<=xi<len(xs) or not 0<=yi<len(ys):
            raise HTTPException(422,'Heatmap cell index outside declared axes.')
        if (xi,yi) in seen:raise HTTPException(422,'Duplicate heatmap cell.')
        if cell.get('x')!=xs[xi] or cell.get('y')!=ys[yi]:raise HTTPException(422,'Heatmap coordinate/index mismatch.')
        if type(z) not in (int,float) or not math.isfinite(z):raise HTTPException(422,'Heatmap cell must be finite; omit missing cells explicitly.')
        seen.add((xi,yi));clean.append({k:cell[k] for k in ('x','y','z','xIndex','yIndex')})
    unit=ref.get('heatmap_unit')
    if not unit:raise HTTPException(422,'Declare scientific heatmap units; no inferred unit.')
    palette=ref['display']['palette']
    lo,hi=min(c['z'] for c in clean),max(c['z'] for c in clean)
    declared=ref['display'].get('color_domain')
    if declared:
        if any(not math.isfinite(v) for v in declared) or declared[0]>=declared[1] or lo<declared[0] or hi>declared[1]:
            raise HTTPException(422,'Color domain must increase and include every data value; clipping is disabled.')
        lo,hi=declared
    transform=ref['display'].get('color_transform','linear')
    if transform=='log10' and lo<=0:raise HTTPException(422,'Log color scales require positive source values.')
    spec={'schema':obj['schema'],'kind':'heatmap','title':str(obj.get('title','Heatmap'))[:160],
        'description':str(obj.get('description',''))[:1000],
        'xLabel':str(obj.get('xLabel','X'))[:100],'yLabel':str(obj.get('yLabel','Y'))[:100],
        'xValues':xs,'yValues':ys,'cells':clean,'domain':{'x':xd,'y':yd,'z':[lo,hi]},
        'publication':{'showGrid':False,'showLegend':False},
        'interaction':{'tooltip':False,'focusablePoints':False,'zoom':False,'pan':False,'crosshair':False}}
    worker=Path(__file__).resolve().parent.parent/'reporting_math'/'heatmap.cjs'
    try:
        result=subprocess.run([os.getenv('SC_REPORTING_NODE_BIN','node'),'--max-old-space-size=256',str(worker)],
            input=json.dumps({'spec':spec,'palette':palette,'geospatial':bool(obj.get('spatialReference')),'transform':transform}),text=True,capture_output=True,timeout=15,
            cwd=worker.parent,env={k:v for k,v in os.environ.items() if k in ('PATH','SYSTEMROOT','TMPDIR')})
    except (OSError,subprocess.TimeoutExpired) as exc:raise HTTPException(503,'Optional Lab DOM renderer unavailable or timed out.') from exc
    if result.returncode:raise HTTPException(503,'Optional pinned Lab heatmap renderer failed; inspect isolated logs.')
    if len(result.stdout)>5_000_000:raise HTTPException(413,'Heatmap SVG exceeds limit.')
    tree=ET.fromstring(result.stdout);ns='{http://www.w3.org/2000/svg}'
    height = float(tree.attrib['height'])
    tree.set('viewBox', f'0 0 860 {height+45}');tree.set('height',str(height+45))
    # Add a labeled scientific color bar to the existing renderer output.
    for i,color in enumerate(PALETTES[palette]):
        ET.SubElement(tree,ns+'rect',{'x':str(100+i*85),'y':str(height+2),'width':'85','height':'12','fill':color})
    mid=(math.sqrt(lo*hi) if transform=='log10' else (lo+hi)/2)
    for x,value,anchor in [(100,lo,'start'),(397.5,mid,'middle'),(695,hi,'end')]:
        ET.SubElement(tree,ns+'text',{'x':str(x),'y':str(height+33),'text-anchor':anchor,'font-family':'sans-serif','font-size':'12'}).text=f'{value:.6g} {unit}'
    if transform=='log10':ET.SubElement(tree,ns+'text',{'x':'100','y':str(height+52),'font-family':'sans-serif','font-size':'11'}).text='Logarithmic color scale; labels and cell annotations retain original values.'
    tree.set('viewBox',f'0 0 860 {height+65}');tree.set('height',str(height+65))
    ET.SubElement(tree,ns+'desc').text='Missing cells remain unfilled. Values are source results; scale changes do not recalculate them.'
    return ET.tostring(tree,encoding='unicode'),{'owner_module':'lab','source_schema':obj['schema'],
        'source_identity':{'artifact_id':ref['artifact_id'],'sha256':ref['sha256']},
        'source_provenance':{'description':obj.get('description'),'unit':unit,
            'spatial_reference':obj.get('spatialReference'), 'axis_labels':{'x':spec['xLabel'],'y':spec['yLabel']}, 'cell_count':len(clean),
            'missing_cells':len(xs)*len(ys)-len(clean),'axes_centers':{'x':xs,'y':ys}},
        'scientific_status':ref.get('evidence_classification','unverified'),
        'uncertainty':'not inferred','render_type':'heatmap','source_fingerprint_verified':False,
        'projection':'2D source grid; no interpolation, reprojection, temporal or volumetric inference'}
