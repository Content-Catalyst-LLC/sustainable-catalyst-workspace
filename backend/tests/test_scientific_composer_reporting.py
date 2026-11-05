from copy import deepcopy
import json
from pathlib import Path
from test_research_reporting import setup,env,stage,save,url
from test_wxr_private_projects import ORIGIN

def figure():return json.loads((Path(__file__).parent/'fixtures/sc_rvf_01/scientific_comparison_synthetic.json').read_text())

def test_native_comparison_pinned_and_exported(setup):
 client,_,_,pid=setup
 ref,_=stage(setup,figure());report=save(client,pid,ref);target=url(pid,report)
 result=client.get(target).json()
 assert result['view']['source']['render_type']=='scientific-composer'
 assert result['view']['source']['source_provenance']['table']['rows'][0][5]==10.5
 for ext in ['csv','png','pdf','docx']:
  first=client.get(target+'/export.'+ext);second=client.get(target+'/export.'+ext)
  assert first.status_code==200,first.text[:100]
  assert first.content==second.content
 assert 'per experimental hectare' in client.get(target+'/export.csv').text

def test_tampered_or_active_composer_svg_rejected(setup):
 from app.reporting_composer_figures import adapt_composer_figure
 from fastapi import HTTPException
 import pytest,hashlib
 obj=figure();obj['svg']+='<script/>'
 with pytest.raises(HTTPException) as e:adapt_composer_figure(obj)
 assert e.value.status_code==409
 obj=figure();obj['svg']=obj['svg'].replace('</svg>','<script>alert(1)</script></svg>');obj['svg_sha256']=hashlib.sha256(obj['svg'].encode()).hexdigest()
 with pytest.raises(HTTPException) as e:adapt_composer_figure(obj)
 assert e.value.status_code==422
