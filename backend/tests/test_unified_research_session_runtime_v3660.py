import pytest
from app.unified_research_session_runtime import *

def new_session(): return create({'projectRef':'project:alpha','title':'Alpha'})

def test_profile_contract():
    p=runtime_profile(); assert p['schema']==RUNTIME_SCHEMA; assert p['version']=='3.66.0'; assert p['researchStageCount']==9; assert p['boundedOperationCount']==8; assert p['resumeRestoresStateOnly'] is True

def test_create_session():
    s=new_session(); assert s['schema']==SESSION_SCHEMA; assert s['currentStage']=='projects'; assert s['status']=='active'; assert all(v is False for v in s['authority'].values())

def test_create_requires_project():
    with pytest.raises(ValueError): create({})

def test_validate_session(): assert validate({'session':new_session()})['valid'] is True

def test_bind_object():
    r=bind_object({'session':new_session(),'stage':'sources','kind':'evidence','objectRef':'evidence:1'}); assert len(r['session']['bindings'])==1; assert r['binding']['sourceAuthorityPreserved'] is True; assert r['binding']['contentReplicated'] is False

def test_bind_requires_ref():
    with pytest.raises(ValueError): bind_object({'session':new_session(),'kind':'evidence'})

def test_transition_adjacent():
    r=transition({'session':new_session(),'toStage':'sources'}); assert r['session']['currentStage']=='sources'; assert r['transition']['automatic'] is False

def test_transition_skip_requires_explicit_permission():
    with pytest.raises(ValueError): transition({'session':new_session(),'toStage':'analysis'})
    r=transition({'session':new_session(),'toStage':'analysis','allowSkip':True}); assert r['transition']['skippedStages']==['sources']

def test_backward_requires_explicit_revisit():
    s=transition({'session':new_session(),'toStage':'sources'})['session']
    with pytest.raises(ValueError): transition({'session':s,'toStage':'projects'})
    assert transition({'session':s,'toStage':'projects','allowRevisit':True})['transition']['revisit'] is True

def test_checkpoint_is_immutable():
    r=checkpoint({'session':new_session(),'reason':'before analysis','storageRef':'cas:abc'}); assert r['checkpoint']['immutable'] is True; assert len(r['checkpoint']['checkpointDigest'])==64; assert len(r['session']['checkpointRefs'])==1

def test_resume_restores_state_only():
    c=checkpoint({'session':new_session()})['checkpoint']; r=resume({'checkpoint':c}); assert r['session']['status']=='active'; assert r['resume']['restoredStateOnly'] is True; assert r['resume']['modelsExecuted'] is False; assert r['resume']['agentsExecuted'] is False; assert r['resume']['governanceApproved'] is False; assert r['resume']['publicationPerformed'] is False

def test_resume_rejects_non_checkpoint():
    with pytest.raises(ValueError): resume({'checkpoint':{'schema':'wrong'}})

def test_snapshot_portable_read_only():
    r=snapshot({'session':new_session()}); assert r['portable'] is True; assert r['readOnly'] is True; assert len(r['snapshotDigest'])==64

def test_export_contains_lineage():
    s=transition({'session':new_session(),'toStage':'sources'})['session']; e=export_session({'session':s}); assert e['schema']==EXPORT_SCHEMA; assert e['automaticExecutionOnImport'] is False; assert e['replayInstructionsIncluded'] is False; assert len(e['exportDigest'])==64; assert len(e['transitionHistory'])==1

def test_operation_index():
    x=operation_index(); assert len(x['items'])==8; assert all(i['bounded'] for i in x['items']); assert all(i['executionAuthority'] is False for i in x['items']); assert all(i['approvalAuthority'] is False for i in x['items']); assert all(i['publicationAuthority'] is False for i in x['items']); assert all(i['externalSideEffectAuthority'] is False for i in x['items'])

def test_dispatch_create(): assert execute('workspace.research-session.create',{'projectRef':'p'})['result']['schema']==SESSION_SCHEMA

def test_unknown_operation_rejected():
    with pytest.raises(ValueError): execute('workspace.research-session.magic',{})

def test_authority_violation_rejected():
    s=new_session(); s['authority']['executeAgents']=True
    with pytest.raises(ValueError): bind_object({'session':s,'kind':'evidence','objectRef':'x'})

def test_completed_session_not_mutable():
    s=new_session(); s['status']='completed'
    with pytest.raises(ValueError): bind_object({'session':s,'kind':'evidence','objectRef':'x'})

def test_upstream_contracts_declared():
    p=runtime_profile(); assert p['upstreamSchemas']['integratedResearchOS']=='sc-workspace-integrated-research-os-runtime/1.0'; assert p['upstreamSchemas']['productionCertification']=='sc-workspace-production-certification-agentic-runtime/1.0'; assert p['upstreamSchemas']['researchSessionBinding']=='sc-workspace-research-session-object-binding-runtime/1.0'
