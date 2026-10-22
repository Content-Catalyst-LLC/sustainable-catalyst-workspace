"""Real temporary SQL store, synthetic snapshots and administrative decisions only."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import sqlite3
import subprocess
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import controlled_recovery as recovery, repository, session_auth
from app.models import Base, ProjectHead, ProjectRevision, DomainMutationReceipt, ArtifactHead, ArtifactRevision, RecoveryRestorationReceipt
from app.schemas import ProjectStoreRequest


@compiles(JSONB, 'sqlite')
def _jsonb_sqlite(element, compiler, **kw):
    return 'JSON'


def digest(value):
    return recovery._digest(value)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    test_url = os.getenv('SC_RECOVERY_TEST_DATABASE_URL')
    if test_url:
        from sqlalchemy.engine import make_url
        if make_url(test_url).database != 'sc_recovery_test':
            raise ValueError('Only the isolated sc_recovery_test database is allowed')
        engine = create_engine(test_url)
        Base.metadata.drop_all(engine, tables=[ProjectHead.__table__, ProjectRevision.__table__, DomainMutationReceipt.__table__, ArtifactHead.__table__, ArtifactRevision.__table__, RecoveryRestorationReceipt.__table__])
    else:
        engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[ProjectHead.__table__, ProjectRevision.__table__, DomainMutationReceipt.__table__, ArtifactHead.__table__, ArtifactRevision.__table__, RecoveryRestorationReceipt.__table__])
    monkeypatch.setattr(recovery, 'session_scope', lambda: Session(engine, expire_on_commit=False))
    local_settings = SimpleNamespace(max_project_bytes=10**6, max_account_bytes=10**7, max_projects_per_account=100, max_artifact_bytes=10**6, max_artifact_account_bytes=10**7, max_artifacts_per_account=100, object_storage_root=str(tmp_path/'workspace-objects'))
    monkeypatch.setattr(repository, 'get_settings', lambda: local_settings)
    monkeypatch.setattr(recovery.object_store, 'get_settings', lambda: local_settings)
    monkeypatch.setattr(session_auth, 'get_settings', lambda: SimpleNamespace(session_signing_secret='synthetic-session-key', service_token='', session_cookie_name='sc_workspace_session', session_issuer='synthetic-issuer', session_audience='workspace.sustainablecatalyst.com', session_ttl_seconds=3600))
    def seed(owner, pid):
        with Session(engine, expire_on_commit=False) as db:
            repository.store_project(db, owner, ProjectStoreRequest.model_validate({'schema': 'sc-workspace-sync-push/1.0', 'sourceProjectId': pid, 'expectedRevision': 0, 'operationId': 'seed-'+pid, 'project': {'schema': 'sc-workspace-project/20.0', 'title': 'Synthetic target', 'objects': [{'id': 'original-target-object', 'type': 'note', 'content': 'preserve me'}]}}))
    seed('alice', 'target-a'); seed('bob', 'target-b')
    catalog = {'projects': [{'project_id': 'source-a', 'name': 'Synthetic wetland study', 'owner_fingerprint': hashlib.sha256(b'alice').hexdigest()[:16]}], 'calculations': [{'record_id': 'calc-a', 'project_id': 'source-a', 'owner_fingerprint': hashlib.sha256(b'alice').hexdigest()[:16]}], 'artifacts': []}
    catalog_file, bundle_file, authorization_file = (tmp_path / n for n in ['catalog.json', 'bundle.json', 'authorization.json'])
    catalog_file.write_text(json.dumps(catalog)); catalog_hash = hashlib.sha256(catalog_file.read_bytes()).hexdigest()
    record = {'record_id': 'calc-a', 'project_id': 'source-a', 'owner_fingerprint': hashlib.sha256(b'alice').hexdigest()[:16], 'payload': {'schema': 'synthetic-scientific-result/v1', 'calculationObjectHash': 'c'*64, 'result': {'value': 12, 'unit': 'synthetic-unit'}}, 'environment_binding_sha256': 'e'*64}
    record['payload_sha256'] = digest(record['payload'])
    bundle = {'schema': recovery.BUNDLE_SCHEMA, 'catalog_sha256': catalog_hash, 'records': [record]}
    bundle_file.write_text(json.dumps(bundle))
    now = datetime.now(timezone.utc)
    policy = {'schema': recovery.AUTH_SCHEMA, 'subject_sha256': hashlib.sha256(b'alice').hexdigest(), 'source_project_id': 'source-a', 'target_project_id': 'target-a', 'catalog_sha256': catalog_hash, 'bundle_sha256': hashlib.sha256(bundle_file.read_bytes()).hexdigest(), 'record_ids': ['calc-a'], 'issued_at': (now-timedelta(seconds=1)).isoformat(), 'expires_at': (now+timedelta(hours=1)).isoformat(), 'ownership_evidence_sha256': 'f'*64, 'ownership_evidence_reference': 'synthetic-human-decision-only', 'environment_bindings': {'calc-a': 'e'*64}, 'approved_plan_sha256': None, 'allowed_actions': ['plan', 'restore', 'rollback'], 'backup_restore_evidence_sha256': '1'*64}
    def save():
        authorization_file.write_text(json.dumps(policy)); authorization_file.chmod(0o600)
    backup_root=tmp_path/'backups'; backup_root.mkdir()
    backup_manifest=tmp_path/'backup-manifest.json'
    def backups():
        (backup_root/'catalog.json').write_bytes(catalog_file.read_bytes())
        (backup_root/'bundle.json').write_bytes(bundle_file.read_bytes())
        database_backup=backup_root/'database.backup'
        if test_url and os.getenv('SC_RECOVERY_PG_CONTAINER'):
            container=os.environ['SC_RECOVERY_PG_CONTAINER']
            with database_backup.open('wb') as stream:
                subprocess.run(['docker','exec',container,'pg_dump','-U','recovery_test','-d','sc_recovery_test','-Fc'],stdout=stream,stderr=subprocess.PIPE,check=True)
            subprocess.run(['docker','exec','-i',container,'pg_restore','-U','recovery_test','--clean','--if-exists','--no-owner','-d','sc_recovery_rehearsal'],input=database_backup.read_bytes(),capture_output=True,check=True)
        elif test_url:
            pg_bin=os.getenv('SC_RECOVERY_PG_BIN','/opt/homebrew/opt/postgresql@18/bin')
            subprocess.run([pg_bin+'/pg_dump','--dbname',test_url.replace('postgresql+psycopg','postgresql'),'-Fc','-f',str(database_backup)],check=True,capture_output=True)
        else:
            database_backup.unlink(missing_ok=True)
            with engine.connect() as connection, sqlite3.connect(database_backup) as saved:
                connection.connection.driver_connection.backup(saved)
            with sqlite3.connect(database_backup) as restored:
                assert restored.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
                assert restored.execute('SELECT count(*) FROM workspace_project_heads').fetchone()[0]==2
        blob_root=Path(os.getenv('SC_WORKSPACE_RECOVERY_BLOB_ROOT',str(tmp_path/'no-blobs')))
        if blob_root.exists():
            for blob in blob_root.iterdir():
                if blob.is_file(): (backup_root/blob.name).write_bytes(blob.read_bytes())
        files=[{'relative_path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in backup_root.iterdir() if f.is_file()]
        manifest={'schema':'sc.workspace.recovery-backup-verification.v1','database_backup_sha256':hashlib.sha256(database_backup.read_bytes()).hexdigest(),'restore_rehearsal_evidence_sha256':hashlib.sha256(b'synthetic-local-test-rehearsal-only').hexdigest(),'files':files}
        backup_manifest.write_text(json.dumps(manifest));backup_manifest.chmod(0o600)
        policy['backup_restore_evidence_sha256']=hashlib.sha256(backup_manifest.read_bytes()).hexdigest()
    def snapshot():
        bundle_file.write_text(json.dumps(bundle)); policy['bundle_sha256'] = hashlib.sha256(bundle_file.read_bytes()).hexdigest(); backups(); save()
    backups(); save()
    monkeypatch.setenv('SC_WORKSPACE_RECOVERY_BACKUP_MANIFEST_FILE',str(backup_manifest))
    monkeypatch.setenv('SC_WORKSPACE_RECOVERY_BACKUP_ROOT',str(backup_root))
    for key, file in [('CATALOG', catalog_file), ('BUNDLE', bundle_file), ('AUTHORIZATION', authorization_file)]:
        monkeypatch.setenv('SC_WORKSPACE_RECOVERY_'+key+'_FILE', str(file))
    monkeypatch.delenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED', raising=False)
    app = FastAPI(); app.include_router(recovery.router)
    client = TestClient(app, base_url='https://workspace.sustainablecatalyst.com')
    client.cookies.set('sc_workspace_session', session_auth.issue_session_token('alice'))
    def project():
        with Session(engine) as db:
            row = repository.get_project(db, 'alice', 'target-a'); return deepcopy(row.package['project']), row.revision
    def plan():
        return client.get('/v1/private-research/recovery/plan', params={'source_project_id': 'source-a', 'target_project_id': 'target-a'})
    def approve():
        result = plan(); assert result.status_code == 200, result.text
        data = result.json(); policy['approved_plan_sha256'] = data['plan_sha256']; save()
        return {'source_project_id': 'source-a', 'target_project_id': 'target-a', 'plan_sha256': data['plan_sha256'], 'expected_revision': data['target_revision']}
    return SimpleNamespace(**locals())


HEADERS = {'Origin': 'https://workspace.sustainablecatalyst.com', 'X-Recovery-Intent': 'restore'}
RESTORE = '/v1/private-research/recovery/restore'
ROLLBACK = '/v1/private-research/recovery/rollback'


def test_plan_authenticated_deterministic_and_zero_sql_writes(setup):
    s=setup; before=s.project(); statements=[]
    def trace(conn, cursor, statement, params, context, many): statements.append(statement)
    event.listen(s.engine, 'before_cursor_execute', trace)
    first=s.plan(); second=s.plan()
    event.remove(s.engine, 'before_cursor_execute', trace)
    assert first.status_code == 200 and first.json() == second.json()
    assert s.project() == before
    assert all(q.lstrip().upper().startswith('SELECT') for q in statements)
    assert first.json()['records'][0]['classifications'] == ['UNMATCHED']
    assert first.json()['mutation_performed'] is False
    assert s.client.post(RESTORE,json=s.approve(),headers=HEADERS).status_code == 403
    assert s.project() == before


@pytest.mark.parametrize('case', ['anonymous','other_cookie','unapproved_source','unowned_target','forged_header'])
def test_source_and_target_authorization_denials(setup,case):
    s=setup
    if case in ['anonymous','forged_header']:s.client.cookies.clear()
    elif case=='other_cookie':s.client.cookies.set('sc_workspace_session',session_auth.issue_session_token('bob'))
    elif case=='unapproved_source':s.policy['source_project_id']='other-source';s.save()
    elif case=='unowned_target':s.policy['subject_sha256']=hashlib.sha256(b'bob').hexdigest();s.client.cookies.set('sc_workspace_session',session_auth.issue_session_token('bob'));s.save()
    response=s.client.get('/v1/private-research/recovery/plan',params={'source_project_id':'source-a','target_project_id':'target-a'},headers={'X-SC-User-ID':'alice','Authorization':'Bearer forged'})
    assert response.status_code in [401,403]
    assert 'calc-a' not in response.text


@pytest.mark.parametrize('case',['catalog','bundle','insecure_policy','expired','missing_config'])
def test_integrity_and_authorization_failure(setup,case):
    s=setup
    if case=='catalog':s.catalog_file.write_text('{}')
    elif case=='bundle':s.bundle_file.write_text('{}')
    elif case=='insecure_policy':s.authorization_file.chmod(0o644)
    elif case=='expired':s.policy['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();s.save()
    else:s.monkeypatch.delenv('SC_WORKSPACE_RECOVERY_AUTHORIZATION_FILE')
    assert s.plan().status_code in [403,503]


@pytest.mark.parametrize('case',['owner','environment','payload','conflicting_duplicate','missing_record'])
def test_unresolved_or_ambiguous_records_block_restore(setup,case):
    s=setup
    if case=='owner':s.policy['ownership_evidence_sha256']=None;s.save()
    elif case=='environment':s.policy['environment_bindings']={};s.save()
    elif case=='payload':s.bundle['records'][0]['payload']['result']['value']=99;s.snapshot()
    elif case=='missing_record':s.bundle['records']=[];s.snapshot()
    else:
        record=deepcopy(s.bundle['records'][0]);record['payload']['result']['value']=99;record['payload_sha256']=digest(record['payload']);s.bundle['records'].append(record);s.snapshot()
    data=s.plan().json(); assert 'BLOCKED' in data['records'][0]['classifications']
    if case=='conflicting_duplicate':assert 'AMBIGUOUS' in data['records'][0]['classifications']
    request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true');before=s.project()
    assert s.client.post(RESTORE,json=request,headers=HEADERS).status_code == 409
    assert s.project() == before


def test_duplicate_observations_do_not_duplicate_imports(setup):
    s=setup;s.bundle['records'].append(deepcopy(s.bundle['records'][0]));s.snapshot()
    assert 'DUPLICATE' in s.plan().json()['records'][0]['classifications']
    request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    assert s.client.post(RESTORE,json=request,headers=HEADERS).json()['created_objects']==1
    assert len(s.project()[0]['objects'])==2


def test_restore_idempotent_preserves_payload_and_scoped_rollback(setup):
    s=setup;request=s.approve();source=s.catalog_file.read_bytes(),s.bundle_file.read_bytes();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    response=s.client.post(RESTORE,json=request,headers=HEADERS);assert response.status_code==200,response.text
    receipt=response.json();project,revision=s.project();assert revision==2
    restored=project['objects'][1];assert restored['payload']==s.record['payload'];assert restored['recovery_provenance']['original_owner_fingerprint']==hashlib.sha256(b'alice').hexdigest()[:16]
    assert s.client.post(RESTORE,json=request,headers=HEADERS).json()['state']=='ALREADY_RESTORED'
    assert s.project()[1]==2
    assert 'MATCHED' in s.plan().json()['records'][0]['classifications']
    request.update(expected_revision=revision,batch_id=receipt['batch_id'])
    response=s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'});assert response.status_code==200,response.text
    project,revision=s.project();assert revision==3 and project['objects']==[{'id':'original-target-object','type':'note','content':'preserve me'}]
    assert project['traceability']['recoveryRestorations'][receipt['batch_id']]['state']=='ROLLED_BACK'
    assert s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'}).json()['state']=='ALREADY_ROLLED_BACK'
    assert source==(s.catalog_file.read_bytes(),s.bundle_file.read_bytes())


@pytest.mark.parametrize('case',['origin','intent','approval','revision','backup'])
def test_mutation_guards(setup,case):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true');headers=dict(HEADERS)
    if case=='origin':headers['Origin']='https://untrusted.invalid'
    elif case=='intent':headers.pop('X-Recovery-Intent')
    elif case=='approval':request['plan_sha256']='0'*64
    elif case=='revision':request['expected_revision']=99
    else:s.policy['backup_restore_evidence_sha256']=None;s.save()
    before=s.project();assert s.client.post(RESTORE,json=request,headers=headers).status_code in [403,409];assert s.project()==before


def test_failed_persistence_is_atomic(setup,monkeypatch):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true');before=s.project()
    def fail(db,subject,target,project,operation):
        target.package={'project':project};db.flush();raise RuntimeError('synthetic precommit failure')
    monkeypatch.setattr(recovery,'_save',fail)
    with pytest.raises(RuntimeError):s.client.post(RESTORE,json=request,headers=HEADERS)
    assert s.project()==before


def test_rollback_is_disabled_by_default_and_rechecks_identity(setup):
    s=setup;request=s.approve();before=s.project()
    request['batch_id']='recovery-'+request['plan_sha256'][:40]
    assert s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'}).status_code==403
    s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    s.client.cookies.set('sc_workspace_session',session_auth.issue_session_token('bob'))
    assert s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'}).status_code==403
    assert s.project()==before


def test_rollback_refuses_modified_recovered_object(setup):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    receipt=s.client.post(RESTORE,json=request,headers=HEADERS).json()
    with Session(s.engine) as db:
        row=repository.get_project(db,'alice','target-a');package=deepcopy(row.package);package['project']['objects'][1]['payload']['result']['value']=99;row.package=package;db.commit()
    before=s.project();request.update(expected_revision=before[1],batch_id=receipt['batch_id'])
    assert s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'}).status_code==409
    assert s.project()==before


def test_rollback_does_not_require_source_files_to_still_exist(setup):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    receipt=s.client.post(RESTORE,json=request,headers=HEADERS).json();s.catalog_file.unlink();s.bundle_file.unlink()
    request.update(expected_revision=2,batch_id=receipt['batch_id'])
    assert s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'}).status_code==200
    assert len(s.project()[0]['objects'])==1


def test_target_edit_invalidates_approved_plan(setup):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    with Session(s.engine) as db:
        row=repository.get_project(db,'alice','target-a');row.revision+=1;db.commit()
    before=s.project();assert s.client.post(RESTORE,json=request,headers=HEADERS).status_code==409;assert s.project()==before


def test_openapi_contract_has_only_bounded_routes(setup):
    schema=setup.app.openapi();assert {'/v1/private-research/recovery/plan',RESTORE,ROLLBACK,'/v1/private-research/recovery/ui','/v1/private-research/recovery/area'}.issubset(schema['paths'])
    assert set(schema['paths']['/v1/private-research/recovery/plan'])=={'get'}
    assert schema['components']['schemas']['Selection']['additionalProperties'] is False
    assert set(schema['components']['schemas']['Selection']['properties'])=={'source_project_id','target_project_id','plan_sha256','expected_revision'}


def attach_document(s):
    content=b'%PDF-1.4\nsynthetic source only\n%%EOF'
    sha=hashlib.sha256(content).hexdigest();root=s.tmp_path/'source-blobs';root.mkdir();(root/sha).write_bytes(content)
    s.monkeypatch.setenv('SC_WORKSPACE_RECOVERY_BLOB_ROOT',str(root))
    record=s.bundle['records'][0];record['payload']['sha256']=sha;record['payload_sha256']=digest(record['payload'])
    record.update(blob_sha256=sha,blob_size_bytes=len(content),filename='synthetic source.pdf',media_type='application/pdf')
    s.snapshot();return content,root/sha


def test_document_bytes_restored_to_existing_object_store_and_downloaded(setup):
    s=setup;content,source=attach_document(s);request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    result=s.client.post(RESTORE,json=request,headers=HEADERS);assert result.status_code==200,result.text
    project,revision=s.project();blob=project['objects'][1]['source_blob']
    response=s.client.get('/v1/private-research/recovery/artifacts/'+blob['artifact_id']);assert response.content==content
    assert response.headers['content-disposition'].startswith('attachment;')
    with Session(s.engine) as db:
        assert recovery.object_store.verify_artifact_storage(db,'alice')['ok'] is True
    request.update(expected_revision=revision,batch_id=result.json()['batch_id'])
    assert s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'}).status_code==200
    assert source.read_bytes()==content
    assert s.client.get('/v1/private-research/recovery/artifacts/'+blob['artifact_id']).status_code==403


def test_artifact_and_database_transaction_roll_back_together(setup,monkeypatch):
    s=setup;content,source=attach_document(s);request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true');before=s.project()
    def fail(*a,**kw):raise RuntimeError('synthetic failure after artifact flush')
    monkeypatch.setattr(recovery,'_save',fail)
    with pytest.raises(RuntimeError):s.client.post(RESTORE,json=request,headers=HEADERS)
    with Session(s.engine) as db:assert db.scalar(select(ArtifactHead)) is None
    assert s.project()==before and source.read_bytes()==content


def test_corrupt_blob_restricted_without_writes(setup):
    s=setup;content,source=attach_document(s);source.write_bytes(b'corrupt')
    data=s.plan().json();assert 'source_blob_integrity_failure' in data['records'][0]['blockers']
    assert data['mutation_performed'] is False


def test_corrupt_backup_prevents_restore(setup):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true');before=s.project()
    (s.backup_root/'database.backup').write_bytes(b'corrupt')
    result=s.client.post(RESTORE,json=request,headers=HEADERS);assert result.status_code==409
    assert s.project()==before


def test_foreign_historical_owner_cannot_be_mapped_by_review_visibility(setup):
    s=setup;foreign='f'*16;s.catalog['projects'][0]['owner_fingerprint']=foreign;s.catalog['calculations'][0]['owner_fingerprint']=foreign
    s.catalog_file.write_text(json.dumps(s.catalog));s.policy['catalog_sha256']=hashlib.sha256(s.catalog_file.read_bytes()).hexdigest();s.bundle['catalog_sha256']=s.policy['catalog_sha256'];s.bundle['records'][0]['owner_fingerprint']=foreign;s.snapshot()
    result=s.plan().json();assert 'existing_source_owner_authorization_denied' in result['records'][0]['blockers']
    request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true');assert s.client.post(RESTORE,json=request,headers=HEADERS).status_code==409


def test_eligible_record_restores_while_unrelated_record_stays_restricted(setup):
    s=setup
    s.catalog['calculations'].append({'record_id':'blocked-calc','project_id':'source-a','owner_fingerprint':hashlib.sha256(b'alice').hexdigest()[:16]})
    s.catalog_file.write_text(json.dumps(s.catalog));s.policy['catalog_sha256']=hashlib.sha256(s.catalog_file.read_bytes()).hexdigest();s.bundle['catalog_sha256']=s.policy['catalog_sha256']
    blocked=deepcopy(s.record);blocked['record_id']='blocked-calc';s.bundle['records'].append(blocked);s.policy['record_ids'].append('blocked-calc');s.snapshot()
    request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    result=s.client.post(RESTORE,json=request,headers=HEADERS);assert result.status_code==200,result.text
    assert result.json()['created_objects']==1 and result.json()['restricted_records']==1
    assert len(s.project()[0]['objects'])==2
    assert s.project()[0]['objects'][1]['recovery_provenance']['original_calculation_id']=='calc-a'


def test_private_area_creation_and_existing_area_preservation(setup):
    s=setup;s.policy['target_project_id']='new-private-area';s.policy['allowed_actions'].append('create-area');s.save();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    payload={'source_project_id':'source-a','target_project_id':'new-private-area'}
    response=s.client.post('/v1/private-research/recovery/area',json=payload,headers={**HEADERS,'X-Recovery-Intent':'create-area'});assert response.status_code==200,response.text
    assert response.json()['state']=='CREATED'
    assert s.client.post('/v1/private-research/recovery/area',json=payload,headers={**HEADERS,'X-Recovery-Intent':'create-area'}).json()['state']=='ALREADY_EXISTS'
    with Session(s.engine) as db:
        project=repository.get_project(db,'alice','new-private-area');assert project.package['project']['objects']==[] and project.package['project']['publication']=='disabled'
        assert repository.get_project(db,'bob','new-private-area') is None


def test_ui_authenticated_no_embedded_inventory_and_status_readonly(setup):
    s=setup;before=s.project();page=s.client.get('/v1/private-research/recovery/ui');assert page.status_code==200
    assert 'sha256-' in page.headers['content-security-policy'] and 'innerHTML' not in page.text and 'calc-a' not in page.text
    response=s.client.get('/v1/private-research/recovery/area-status');assert response.status_code==200
    assert response.json()['state']=='PRIVATE_RESEARCH_AREA' and response.json()['writes_enabled'] is False
    assert s.project()==before
    s.client.cookies.clear();assert s.client.get('/v1/private-research/recovery/ui').status_code==401
    assert s.client.get('/v1/private-research/recovery/area-status').status_code==401


def test_client_forged_project_manifest_cannot_authorize_rollback(setup):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true');batch='recovery-'+request['plan_sha256'][:40]
    with Session(s.engine) as db:
        row=repository.get_project(db,'alice','target-a');package=deepcopy(row.package)
        package['project']['traceability']={'recoveryRestorations':{batch:{'state':'RESTORED','plan_sha256':request['plan_sha256'],'source_project_id':'source-a','catalog_sha256':s.policy['catalog_sha256'],'bundle_sha256':s.policy['bundle_sha256'],'created_object_hashes':{'original-target-object':digest(package['project']['objects'][0])}}}}
        row.package=package;db.commit()
    before=s.project();request['batch_id']=batch
    assert s.client.post(ROLLBACK,json=request,headers={**HEADERS,'X-Recovery-Intent':'rollback'}).status_code==403
    assert s.project()==before


def test_forged_sync_operation_identity_cannot_claim_successful_restore(setup):
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    with Session(s.engine) as db:
        row=repository.get_project(db,'alice','target-a');row.last_operation_id='recovery-'+request['plan_sha256'][:40];db.commit()
    before=s.project();assert s.client.post(RESTORE,json=request,headers=HEADERS).status_code==409
    assert s.project()==before
    with Session(s.engine) as db:assert db.scalar(select(RecoveryRestorationReceipt)) is None


def test_independent_records_do_not_require_unrelated_environment_mapping(setup):
    s=setup;s.policy['environment_bindings']={};s.bundle['records'][0]['environment_dependencies']=[];s.bundle['records'][0].pop('environment_binding_sha256');s.snapshot()
    assert 'BLOCKED' not in s.plan().json()['records'][0]['classifications']
    request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    assert s.client.post(RESTORE,json=request,headers=HEADERS).status_code==200
    provenance=s.project()[0]['objects'][1]['recovery_provenance'];assert provenance['environment_binding_sha256'] is None


def test_empty_dependency_claim_does_not_hide_real_environment_reference(setup):
    s=setup;s.policy['environment_bindings']={};s.bundle['records'][0]['environment_dependencies']=[];s.bundle['records'][0]['payload']['environmentKey']='unmapped';s.bundle['records'][0]['payload_sha256']=digest(s.bundle['records'][0]['payload']);s.snapshot()
    assert 'research_environment_mapping_unresolved' in s.plan().json()['records'][0]['blockers']


@pytest.mark.skipif(not os.getenv('SC_RECOVERY_TEST_DATABASE_URL'),reason='PostgreSQL row locks require isolated PostgreSQL CI')
def test_postgres_concurrent_restore_is_idempotent(setup):
    from concurrent.futures import ThreadPoolExecutor
    s=setup;request=s.approve();s.monkeypatch.setenv('SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED','true')
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:s.client.post(RESTORE,json=request,headers=HEADERS),range(2)))
    assert all(r.status_code==200 for r in results),[r.text for r in results]
    assert sorted(r.json()['state'] for r in results)==['ALREADY_RESTORED','RESTORED']
    assert len(s.project()[0]['objects'])==2 and s.project()[1]==2


@pytest.mark.skipif(not os.getenv('SC_RECOVERY_TEST_DATABASE_URL'),reason='PostgreSQL migration requires isolated PostgreSQL CI')
def test_additive_migration_is_idempotent_and_keeps_existing_projects(setup):
    s=setup;before=s.project();RecoveryRestorationReceipt.__table__.drop(s.engine)
    sql=(Path(__file__).resolve().parents[1]/'migrations/051_controlled_research_restoration.sql').read_text()
    with s.engine.connect().execution_options(isolation_level='AUTOCOMMIT') as conn:
        conn.exec_driver_sql(sql);conn.exec_driver_sql(sql)
    assert s.project()==before
    with Session(s.engine) as db:assert db.scalar(select(RecoveryRestorationReceipt)) is None


@pytest.mark.skipif(not os.getenv('SC_RECOVERY_TEST_DATABASE_URL'),reason='PostgreSQL sync race requires isolated PostgreSQL CI')
def test_existing_sync_and_restore_writers_share_revision_lock(setup):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from fastapi import HTTPException
    s=setup;barrier=Barrier(2)
    def write(index):
        barrier.wait()
        with Session(s.engine) as db:
            payload=ProjectStoreRequest.model_validate({'schema':'sc-workspace-sync-push/1.0','sourceProjectId':'target-a','expectedRevision':1,'operationId':'parallel-'+str(index),'project':{'schema':'sc-workspace-project/20.0','objects':[{'id':'parallel-'+str(index)}]}})
            try:repository.store_project(db,'alice',payload);return 200
            except HTTPException as error:return error.status_code
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(write,range(2)))
    assert sorted(results)==[200,409] and s.project()[1]==2
