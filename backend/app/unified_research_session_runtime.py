from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import hashlib, json
from typing import Any, Dict, Mapping
from uuid import uuid4

VERSION='3.66.0'
RUNTIME_SCHEMA='sc-workspace-unified-research-session-runtime/1.0'
REQUEST_SCHEMA='sc-workspace-unified-research-session-request/1.0'
RESULT_SCHEMA='sc-workspace-unified-research-session-result/1.0'
SESSION_SCHEMA='sc-workspace-unified-research-session/1.0'
BINDING_SCHEMA='sc-workspace-unified-research-session-binding/1.0'
TRANSITION_SCHEMA='sc-workspace-unified-research-session-transition/1.0'
CHECKPOINT_SCHEMA='sc-workspace-unified-research-session-checkpoint/1.0'
SNAPSHOT_SCHEMA='sc-workspace-unified-research-session-snapshot/1.0'
EXPORT_SCHEMA='sc-workspace-unified-research-session-export/1.0'
UPSTREAM={
 'integratedResearchOS':'sc-workspace-integrated-research-os-runtime/1.0',
 'productionCertification':'sc-workspace-production-certification-agentic-runtime/1.0',
 'researchSessionBinding':'sc-workspace-research-session-object-binding-runtime/1.0',
}
STAGES=('projects','sources','analysis','models','agents','governance','visualizations','decisions','publication')
STATUSES=('active','paused','completed','archived')
OPERATIONS=(
 'workspace.research-session.validate','workspace.research-session.create','workspace.research-session.bind-object',
 'workspace.research-session.transition','workspace.research-session.checkpoint','workspace.research-session.resume',
 'workspace.research-session.snapshot','workspace.research-session.export',
)
BOUNDARIES={
 'boundedOperationsOnly':True,'arbitraryCodeExecution':False,'automaticModelExecutionEnabled':False,
 'automaticAgentExecutionEnabled':False,'automaticApprovalEnabled':False,'automaticGovernanceBypassEnabled':False,
 'automaticPublicationEnabled':False,'automaticExternalSideEffectsEnabled':False,'automaticTruthDeterminationEnabled':False,
 'automaticEvidenceRankingEnabled':False,'automaticNarrativeSelectionEnabled':False,'automaticDecisionAuthorityEnabled':False,
 'automaticResumeExecutionEnabled':False,'automaticReplayEnabled':False,'automaticStageAdvanceEnabled':False,
 'sourceObjectMutationEnabled':False,'sessionAuthorityMayOverrideUpstream':False,'stageAuthorityPreserved':True,
 'humanGovernancePreserved':True,'provenancePreserved':True,'dissentPreserved':True,
 'checkpointImmutabilityRequired':True,'resumeRestoresStateOnly':True,'backendPersistenceAdapterRequiredForDurability':True,
 'maxBindings':2048,'maxTransitions':4096,'maxCheckpoints':512,
}

def _now(): return datetime.now(timezone.utc).isoformat()
def _id(prefix): return f'{prefix}_{uuid4().hex}'
def _copy(v): return deepcopy(v)
def _digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def _authority():
    return {'executeModels':False,'executeAgents':False,'approveGovernance':False,'bypassGovernance':False,
            'publish':False,'externalSideEffects':False,'determineTruth':False,'rankEvidence':False,
            'selectNarrative':False,'decide':False}

def _session(payload:Mapping[str,Any], require_open=False):
    raw=payload.get('session')
    if not isinstance(raw,dict) or raw.get('schema')!=SESSION_SCHEMA: raise ValueError('valid unified research session is required')
    s=_copy(raw)
    if s.get('version')!=VERSION: raise ValueError('unified research session version mismatch')
    if require_open and s.get('status') not in ('active','paused'): raise ValueError('unified research session is not resumable')
    if s.get('currentStage') not in STAGES: raise ValueError('invalid current research stage')
    auth=s.get('authority') or {}
    if any(bool(auth.get(k)) for k in _authority()): raise ValueError('unified research session authority boundary violated')
    return s

def _stage_index(stage):
    if stage not in STAGES: raise ValueError('unsupported research stage')
    return STAGES.index(stage)

def validate(payload):
    try: s=_session(payload)
    except ValueError as e: return {'valid':False,'errors':[str(e)]}
    errors=[]
    if not s.get('sessionId'): errors.append('sessionId is required')
    if not s.get('projectRef'): errors.append('projectRef is required')
    if not isinstance(s.get('bindings'),list): errors.append('bindings must be a list')
    if not isinstance(s.get('transitionHistory'),list): errors.append('transitionHistory must be a list')
    if not isinstance(s.get('checkpointRefs'),list): errors.append('checkpointRefs must be a list')
    if len(s.get('bindings') or [])>BOUNDARIES['maxBindings']: errors.append('binding limit exceeded')
    if len(s.get('transitionHistory') or [])>BOUNDARIES['maxTransitions']: errors.append('transition limit exceeded')
    if len(s.get('checkpointRefs') or [])>BOUNDARIES['maxCheckpoints']: errors.append('checkpoint limit exceeded')
    return {'valid':not errors,'errors':errors}

def create(payload):
    project_ref=str(payload.get('projectRef') or '').strip()
    if not project_ref: raise ValueError('projectRef is required')
    now=_now()
    return {'schema':SESSION_SCHEMA,'version':VERSION,'sessionId':str(payload.get('sessionId') or _id('research_session')),
            'projectRef':project_ref,'researchOSContextRef':str(payload.get('researchOSContextRef') or ''),
            'platformCoreSessionRef':str(payload.get('platformCoreSessionRef') or ''),'parentSessionRef':str(payload.get('parentSessionRef') or ''),
            'title':str(payload.get('title') or 'Unified Research Session'),'status':'active','currentStage':'projects',
            'createdAt':now,'updatedAt':now,'resumedAt':None,'completedAt':None,'bindings':[],'transitionHistory':[],
            'checkpointRefs':[],'provenanceRefs':list(payload.get('provenanceRefs') or []),'dissentRefs':list(payload.get('dissentRefs') or []),
            'governanceRefs':list(payload.get('governanceRefs') or []),'metadata':_copy(payload.get('metadata') or {}),'authority':_authority(),
            'persistence':{'backendAuthoritative':True,'adapterContract':'workspace-postgresql-or-content-addressed-session-store',
                           'checkpointImmutabilityRequired':True,'resumeRestoresStateOnly':True}}

def bind_object(payload):
    s=_session(payload,True); stage=str(payload.get('stage') or s['currentStage']); _stage_index(stage)
    kind=str(payload.get('kind') or '').strip(); obj=str(payload.get('objectRef') or '').strip()
    if not kind or not obj: raise ValueError('kind and objectRef are required')
    if len(s['bindings'])>=BOUNDARIES['maxBindings']: raise ValueError('binding limit exceeded')
    b={'schema':BINDING_SCHEMA,'version':VERSION,'bindingId':str(payload.get('bindingId') or _id('session_binding')),
       'stage':stage,'kind':kind,'objectRef':obj,'role':str(payload.get('role') or 'context'),
       'revisionRef':str(payload.get('revisionRef') or ''),'fingerprint':str(payload.get('fingerprint') or ''),
       'provenanceRefs':list(payload.get('provenanceRefs') or []),'boundAt':_now(),'contentReplicated':False,'sourceAuthorityPreserved':True}
    if any(x.get('bindingId')==b['bindingId'] for x in s['bindings']): raise ValueError('bindingId already exists')
    s['bindings'].append(b); s['updatedAt']=_now(); return {'session':s,'binding':b}

def transition(payload):
    s=_session(payload,True); target=str(payload.get('toStage') or '').strip(); ti=_stage_index(target); ci=_stage_index(s['currentStage'])
    if ti<ci and not bool(payload.get('allowRevisit')): raise ValueError('backward lifecycle transition requires explicit allowRevisit')
    if ti>ci+1 and not bool(payload.get('allowSkip')): raise ValueError('stage skip requires explicit allowSkip')
    if len(s['transitionHistory'])>=BOUNDARIES['maxTransitions']: raise ValueError('transition limit exceeded')
    rec={'schema':TRANSITION_SCHEMA,'version':VERSION,'transitionId':str(payload.get('transitionId') or _id('session_transition')),
         'fromStage':s['currentStage'],'toStage':target,'reason':str(payload.get('reason') or ''),
         'authorizedByRef':str(payload.get('authorizedByRef') or ''),'governanceRef':str(payload.get('governanceRef') or ''),
         'revisit':ti<ci,'skippedStages':list(STAGES[ci+1:ti]) if ti>ci+1 else [],'transitionedAt':_now(),'automatic':False}
    s['transitionHistory'].append(rec); s['currentStage']=target; s['updatedAt']=_now()
    if payload.get('status') in STATUSES:
        s['status']=payload['status']
        if payload['status']=='completed': s['completedAt']=_now()
    return {'session':s,'transition':rec}

def checkpoint(payload):
    s=_session(payload)
    if len(s['checkpointRefs'])>=BOUNDARIES['maxCheckpoints']: raise ValueError('checkpoint limit exceeded')
    cid=str(payload.get('checkpointId') or _id('session_checkpoint')); captured=_now()
    body={'session':_copy(s),'reason':str(payload.get('reason') or ''),'capturedAt':captured,'storageRef':str(payload.get('storageRef') or '')}
    c={'schema':CHECKPOINT_SCHEMA,'version':VERSION,'checkpointId':cid,'sessionId':s['sessionId'],'projectRef':s['projectRef'],
       'currentStage':s['currentStage'],'capturedAt':captured,'reason':body['reason'],'storageRef':body['storageRef'],
       'session':body['session'],'checkpointDigest':_digest(body),'immutable':True,'authorityGranted':False}
    updated=_copy(s); updated['checkpointRefs'].append({'checkpointId':cid,'digest':c['checkpointDigest'],'storageRef':c['storageRef'],'capturedAt':captured}); updated['updatedAt']=_now()
    return {'session':updated,'checkpoint':c}

def resume(payload):
    c=payload.get('checkpoint')
    if not isinstance(c,dict) or c.get('schema')!=CHECKPOINT_SCHEMA: raise ValueError('valid immutable session checkpoint is required')
    if c.get('version')!=VERSION or c.get('immutable') is not True: raise ValueError('checkpoint is not eligible for resume')
    if not isinstance(c.get('session'),dict): raise ValueError('checkpoint session payload missing')
    s=_session({'session':c['session']}); s['status']='active'; s['resumedAt']=_now(); s['updatedAt']=_now()
    s['metadata']={**(s.get('metadata') or {}),'resumedFromCheckpointId':c.get('checkpointId'),'resumedFromCheckpointDigest':c.get('checkpointDigest')}
    return {'session':s,'resume':{'checkpointId':c.get('checkpointId'),'checkpointDigest':c.get('checkpointDigest'),'restoredStateOnly':True,
            'modelsExecuted':False,'agentsExecuted':False,'governanceApproved':False,'publicationPerformed':False,'externalSideEffectsPerformed':False}}

def snapshot(payload):
    s=_session(payload); captured=_now(); body={'session':s,'capturedAt':captured}
    return {'schema':SNAPSHOT_SCHEMA,'version':VERSION,'snapshotId':str(payload.get('snapshotId') or _id('session_snapshot')),
            'sessionId':s['sessionId'],'projectRef':s['projectRef'],'currentStage':s['currentStage'],'capturedAt':captured,
            'session':_copy(s),'snapshotDigest':_digest(body),'portable':True,'readOnly':True,'authorityGranted':False}

def export_session(payload):
    s=_session(payload); e={'schema':EXPORT_SCHEMA,'version':VERSION,'exportId':str(payload.get('exportId') or _id('session_export')),
      'sessionId':s['sessionId'],'projectRef':s['projectRef'],'currentStage':s['currentStage'],'exportedAt':_now(),'session':_copy(s),
      'bindings':_copy(s['bindings']),'transitionHistory':_copy(s['transitionHistory']),'checkpointRefs':_copy(s['checkpointRefs']),
      'provenanceRefs':_copy(s.get('provenanceRefs') or []),'governanceRefs':_copy(s.get('governanceRefs') or []),
      'dissentRefs':_copy(s.get('dissentRefs') or []),'replayInstructionsIncluded':False,'automaticExecutionOnImport':False,'authorityGranted':False}
    e['exportDigest']=_digest(e); return e

def runtime_profile():
    return {'schema':RUNTIME_SCHEMA,'version':VERSION,'title':'Unified Research Session & Lifecycle Persistence','researchStages':list(STAGES),
            'researchStageCount':len(STAGES),'sessionStatuses':list(STATUSES),'boundedOperations':list(OPERATIONS),'boundedOperationCount':len(OPERATIONS),
            'upstreamSchemas':dict(UPSTREAM),'capabilities':{'versionedUnifiedResearchSessions':True,'crossSessionLineage':True,
            'crossStageBindings':True,'lifecycleTransitionHistory':True,'immutableCheckpoints':True,'resumableResearchSessions':True,
            'portableSnapshots':True,'portableSessionExport':True,'backendPersistenceAdapterContract':True,'wordpressStandaloneParityExpected':True},**BOUNDARIES}

def operation_index():
    mut={'workspace.research-session.create','workspace.research-session.bind-object','workspace.research-session.transition','workspace.research-session.checkpoint','workspace.research-session.resume'}
    return {'schema':'sc-workspace-unified-research-session-operation-index/1.0','version':VERSION,
            'items':[{'operation':op,'input':REQUEST_SCHEMA,'output':RESULT_SCHEMA,'bounded':True,'executionAuthority':False,
                      'approvalAuthority':False,'publicationAuthority':False,'mutationAuthority':op in mut,'externalSideEffectAuthority':False} for op in OPERATIONS],**BOUNDARIES}

def execute(operation,payload):
    handlers={'workspace.research-session.validate':validate,'workspace.research-session.create':create,
      'workspace.research-session.bind-object':bind_object,'workspace.research-session.transition':transition,
      'workspace.research-session.checkpoint':checkpoint,'workspace.research-session.resume':resume,
      'workspace.research-session.snapshot':snapshot,'workspace.research-session.export':export_session}
    if operation not in handlers: raise ValueError('unsupported operation')
    return {'schema':RESULT_SCHEMA,'version':VERSION,'operation':operation,'result':handlers[operation](payload or {})}
