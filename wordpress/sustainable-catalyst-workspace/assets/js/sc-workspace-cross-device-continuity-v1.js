(function(global){
  'use strict';
  const SCHEMA='sc-workspace-cross-device-continuity/1.0';
  const OPERATION_SCHEMA='sc-workspace-sync-operation/1.0';
  const MIGRATION_SCHEMA='sc-workspace-device-migration/1.0';
  const OPERATION_STATES=new Set(['pending','interrupted','completed','failed','superseded']);
  const OPERATION_KINDS=new Set(['push','pull','resolve-local','resolve-cloud','recreate-head']);
  function text(v,n=200){return String(v==null?'':v).slice(0,n);}
  function revision(v){return Math.max(0,Number(v)||0);}
  function operation(input={},makeId=()=>`syo-${Date.now()}`,now=()=>new Date().toISOString()){
    return {schema:OPERATION_SCHEMA,id:text(input.id||makeId(),160),projectId:text(input.projectId,160),kind:OPERATION_KINDS.has(input.kind)?input.kind:'push',state:OPERATION_STATES.has(input.state)?input.state:'pending',expectedRevision:revision(input.expectedRevision),remoteRevision:revision(input.remoteRevision),localFingerprint:text(input.localFingerprint,128),remoteFingerprint:text(input.remoteFingerprint,128),startedAt:text(input.startedAt||now(),80),updatedAt:text(input.updatedAt||now(),80),completedAt:text(input.completedAt,80),message:text(input.message,500)};
  }
  function normalizeOperations(items=[]){return (Array.isArray(items)?items:[]).map(x=>operation(x)).filter(x=>x.projectId).slice(0,80);}
  function markInterrupted(items=[],now=()=>new Date().toISOString()){
    const at=now();return normalizeOperations(items).map(x=>x.state==='pending'?{...x,state:'interrupted',updatedAt:at,message:x.message||'Workspace restarted before this sync operation recorded a final result.'}:x);
  }
  function pendingFor(items=[],projectId=''){return normalizeOperations(items).find(x=>x.projectId===projectId&&['pending','interrupted'].includes(x.state))||null;}
  function complete(op,message='',now=()=>new Date().toISOString()){const at=now();return {...operation(op),state:'completed',updatedAt:at,completedAt:at,message:text(message,500)};}
  function fail(op,message='',interrupted=false,now=()=>new Date().toISOString()){const at=now();return {...operation(op),state:interrupted?'interrupted':'failed',updatedAt:at,message:text(message,500)};}
  function migrationPackage(project,enrollment,workspaceVersion,projectFingerprint,now=()=>new Date().toISOString()){
    const p=JSON.parse(JSON.stringify(project||{}));
    if(p.persistence)p.persistence={scope:'device-migration-copy',syncState:'local-only',accountEligible:true,serverStored:false};
    if(Array.isArray(p.recentTools))p.recentTools=[];
    return {schema:MIGRATION_SCHEMA,workspaceVersion:text(workspaceVersion,40),createdAt:now(),source:{projectId:text(project?.id,160),projectTitle:text(project?.title,200),projectFingerprint:text(projectFingerprint,128)},continuity:{serverRevision:revision(enrollment?.serverRevision),lastSyncedFingerprint:text(enrollment?.lastSyncedFingerprint,128),remoteRevision:revision(enrollment?.remoteRevision),syncWasEnabled:Boolean(enrollment?.enabled),automaticEnrollmentOnImport:false},privacy:{deviceIdentityIncluded:false,accountProfileIncluded:false,restNonceIncluded:false,recentToolsIncluded:false},transport:{importMode:'new-local-copy',syncEnrollmentTransferred:false,automaticUpload:false,backgroundSync:false},project:p};
  }
  function inspectMigration(pkg){
    if(!pkg||typeof pkg!=='object'||pkg.schema!==MIGRATION_SCHEMA)return {ok:false,reason:'Unsupported device-migration package.'};
    if(!pkg.project||typeof pkg.project!=='object'||!String(pkg.source?.projectId||pkg.project?.id||''))return {ok:false,reason:'Migration package is missing a project.'};
    if(pkg.transport?.importMode!=='new-local-copy'||pkg.transport?.syncEnrollmentTransferred!==false)return {ok:false,reason:'Migration package does not preserve the new-copy/no-auto-enrollment boundary.'};
    return {ok:true,sourceProjectId:text(pkg.source?.projectId||pkg.project.id,160),sourceProjectTitle:text(pkg.source?.projectTitle||pkg.project.title||'Workspace project',200),projectFingerprint:text(pkg.source?.projectFingerprint,128),serverRevision:revision(pkg.continuity?.serverRevision),syncWasEnabled:Boolean(pkg.continuity?.syncWasEnabled)};
  }
  function migrationKey(sourceProjectId,fingerprint){return `${text(sourceProjectId,160)}::${text(fingerprint,128)}`;}
  global.SCWorkspaceCrossDeviceContinuity={SCHEMA,OPERATION_SCHEMA,MIGRATION_SCHEMA,operation,normalizeOperations,markInterrupted,pendingFor,complete,fail,migrationPackage,inspectMigration,migrationKey};
})(typeof window!=='undefined'?window:globalThis);
