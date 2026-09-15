from pathlib import Path
import json

from app.polyglot import RUNTIMES, OPERATION_LANGUAGE, arrow_compatible_descriptor, _sql_execute

ROOT=Path(__file__).resolve().parents[1]

def test_version_and_lineage():
    cfg=(ROOT/'backend/app/config.py').read_text()
    assert 'service_version: str = "2.12.0"' in cfg
    dep=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text()
    assert "const PREVIOUS_RELEASE = '2.11.0';" in dep
    assert "const ROLLBACK_RELEASE = '2.11.0';" in dep

def test_runtime_catalog_has_five_languages():
    assert [r.language for r in RUNTIMES] == ['python','sql','r','julia','wasm']
    assert set(OPERATION_LANGUAGE.values()) == {'python','sql','r','julia','wasm'}

def test_no_arbitrary_code_contract():
    src=(ROOT/'backend/app/polyglot.py').read_text()
    assert 'arbitraryCodeExecution":False' in src or '"arbitraryCodeExecution":False' in src
    assert 'subprocess' not in src
    assert 'shell=True' not in src
    assert 'eval(' not in src
    assert 'exec(' not in src

def test_arrow_descriptor():
    d=arrow_compatible_descriptor([{'a':1,'b':'x'},{'a':2,'b':None}])
    assert d['schema']=='sc-workspace-arrow-compatible-table/1.0'
    assert d['rowCount']==2
    cols={x['name']:x for x in d['columns']}
    assert cols['a']['logicalType']=='int64'
    assert cols['b']['logicalType']=='utf8'
    assert cols['b']['nullable'] is True

def test_bounded_sql_aggregate():
    out=_sql_execute('workspace.polyglot.sql.aggregate', {'rows':[{'x':1},{'x':3},{'x':5}], 'column':'x','aggregate':'avg'})
    assert out['value']==3.0
    assert out['exchange']['rowCount']==3

def test_bounded_sql_group_summary():
    out=_sql_execute('workspace.polyglot.sql.group-summary', {'rows':[{'g':'a','x':1},{'g':'a','x':3},{'g':'b','x':4}], 'groupBy':'g','valueColumn':'x','aggregate':'sum'})
    assert out['rows']==[{'group':'a','value':4},{'group':'b','value':4}]

def test_migration_and_wordpress_routes():
    mig=(ROOT/'backend/migrations/012_polyglot_scientific_runtime_fabric.sql').read_text()
    assert 'workspace_polyglot_execution_receipts' in mig
    assert 'GRANT SELECT, INSERT, UPDATE, DELETE' in mig
    php=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    for token in ('backend-polyglot-runtimes','backend-polyglot-operations','backend-polyglot-receipts'):
        assert token in php

def test_compose_runtime_routes_are_server_configured():
    compose=(ROOT/'backend/docker-compose.example.yml').read_text()
    for token in ('SC_WORKSPACE_RUNTIME_R_URL','SC_WORKSPACE_RUNTIME_JULIA_URL','SC_WORKSPACE_RUNTIME_WASM_URL'):
        assert token in compose
    assert 'read_only: true' in compose
    assert 'no-new-privileges:true' in compose
