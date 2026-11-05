"""Preserve Lab Figure Composer's canonical structured scientific figure."""
import hashlib,json
from fastapi import HTTPException
from .reporting_workbench_bridge import validate_inert_svg
SCHEMA='sc-lab-source-bound-scientific-figure/1.0'
def adapt_composer_figure(obj):
    try:
        spec=obj['spec'];svg=obj['svg']
        encoded=json.dumps(spec,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
        if hashlib.sha256(encoded).hexdigest()!=obj['spec_sha256'] or hashlib.sha256(svg.encode()).hexdigest()!=obj['svg_sha256']:
            raise HTTPException(409,'Lab scientific figure fingerprint mismatch.')
        if obj.get('renderer_version') not in {'sc-lab-figure-composer-scientific/1.0','sc-lab-figure-composer-scientific/1.1'} or obj.get('net_removal_status')!='NOT_QUANTIFIED':raise ValueError()
        validate_inert_svg(svg)
        sources=spec['sources'];table=obj['table']
        if not isinstance(table['columns'],list) or not isinstance(table['rows'],list) or len(table['rows'])>100:raise ValueError()
        if any(len(row)!=len(table['columns']) for row in table['rows']):raise ValueError()
        return svg,{'owner_module':'lab','source_schema':SCHEMA,'source_identity':{'spec_sha256':obj['spec_sha256'],'svg_sha256':obj['svg_sha256'],'revision':spec['revision']},
            'source_provenance':{'table':table,'sources':sources,'scientific_spec':spec,'limitations':spec['limitations'],'renderer_version':obj['renderer_version']},
            'scientific_status':spec['status'],'uncertainty':'source-specific; never pooled','render_type':'scientific-composer',
            'source_fingerprint_verified':True,'projection':None}
    except (KeyError,ValueError,TypeError,AttributeError) as exc:raise HTTPException(422,'Invalid structured scientific figure.') from exc
