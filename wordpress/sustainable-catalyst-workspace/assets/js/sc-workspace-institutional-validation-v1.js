(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceInstitutionalValidation=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const VALIDATION_SCHEMA='sc-workspace-institutional-transfer-validation/1.0';
  const REPORT_SCHEMA='sc-workspace-institutional-validation-report/1.0';
  const POLICY_SCHEMA='sc-workspace-institutional-handoff-validation-policy/1.0';
  const RESEARCH_PACKAGE_SCHEMA='sc-workspace-institutional-research-package/1.0';
  const HANDOFF_PACKAGE_SCHEMA='sc-workspace-institutional-handoff-package/1.0';
  const RECEIPT_SCHEMA='sc-workspace-institutional-handoff-receipt/1.0';
  const TARGET_PRODUCT='catalyst-intelligence-platform';
  const text=v=>String(v==null?'':v), list=v=>Array.isArray(v)?v:[], clean=(v,n=4000)=>text(v).trim().slice(0,n);
  const clone=v=>JSON.parse(JSON.stringify(v==null?null:v));
  function check(key,label,status,detail){return {key,label,status,detail};}
  function summarize(checks){const failed=checks.filter(x=>x.status==='fail').length,attention=checks.filter(x=>x.status==='attention').length;return {failed,attention,passed:checks.filter(x=>x.status==='pass').length,status:failed?'blocked':attention?'attention':'pass',transferAllowed:failed===0};}
  function currentProject(state,id){return list(state&&state.projects).find(p=>p&&p.id===id&&!p.archivedAt)||null;}
  function exactSet(a,b){const x=[...new Set(list(a).map(String))].sort(),y=[...new Set(list(b).map(String))].sort();return x.length===y.length&&x.every((v,i)=>v===y[i]);}
  function researchPackageAssessment(pkg,state,researchHelper){
    const p=pkg&&typeof pkg==='object'?pkg:{},checks=[];
    checks.push(check('schema','Package schema',p.schema===RESEARCH_PACKAGE_SCHEMA?'pass':'fail',p.schema===RESEARCH_PACKAGE_SCHEMA?'Supported institutional research package.':'Unsupported institutional research package schema.'));
    const integrity=researchHelper&&typeof researchHelper.verifyPackage==='function'?researchHelper.verifyPackage(p):{ok:false,verified:false,message:'Research-package integrity helper unavailable.'};
    checks.push(check('integrity','Package fingerprint',integrity.ok?'pass':'fail',integrity.message||'Package fingerprint could not be verified.'));
    const institution=clean(p.institution,320),purpose=clean(p.purpose,4000);
    checks.push(check('recipient','Receiving institution',institution?'pass':'fail',institution?'Receiving institution/program is explicitly named.':'Receiving institution/program is required before transfer.'));
    checks.push(check('purpose','Transfer purpose',purpose?'pass':'fail',purpose?'Transfer purpose is explicitly recorded.':'Transfer purpose is required before transfer.'));
    const records=list(p.records),scope=p.manifest&&p.manifest.scope&&typeof p.manifest.scope==='object'?p.manifest.scope:{},keys=records.map(r=>clean(r&&r.key,420)).filter(Boolean),manifestKeys=list(scope.recordKeys).map(x=>clean(x,420)).filter(Boolean),count=Number(scope.recordCount);
    const scopeOk=records.length>0&&count===records.length&&keys.length===records.length&&exactSet(keys,manifestKeys);
    checks.push(check('scope','Disclosure scope',scopeOk?'pass':'fail',scopeOk?`${records.length} scoped record${records.length===1?'':'s'} match the frozen manifest.`:'Frozen manifest scope/count does not match packaged records.'));
    const counts=p.manifest&&p.manifest.counts||{},review=p.review&&typeof p.review==='object'?p.review:{},countsOk=Number(counts.records)===records.length&&Number(counts.references)===list(p.references).length&&Number(counts.tasks)===list(p.tasks).length&&Number(counts.comments)===list(review.comments).length&&Number(counts.proposals)===list(review.proposals).length;
    checks.push(check('counts','Disclosure counts',countsOk?'pass':'fail',countsOk?'Manifest counts match included disclosure layers.':'Manifest disclosure counts do not match package contents.'));
    const omitted=p.manifest&&p.manifest.omitted||{},gov=p.governance||{};
    const privacyOk=omitted.deviceIdentity===true&&omitted.accountIdentity===true&&omitted.cloudSyncState===true&&omitted.recentTools===true;
    checks.push(check('privacy','Personal-workspace boundary',privacyOk?'pass':'fail',privacyOk?'Device/account/sync/recent-tool state is explicitly omitted.':'Required personal-workspace omissions are not explicit.'));
    const governanceOk=gov.frozenDisclosureArtifact===true&&gov.sourceProjectUnchanged===true&&gov.automaticPublication===false&&gov.automaticUpload===false&&gov.automaticCanonicalMutation===false&&gov.organizationAccessControl===false;
    checks.push(check('governance','Governance boundary',governanceOk?'pass':'fail',governanceOk?'Frozen copy semantics and no-auto-transfer boundary are explicit.':'Institutional package governance boundary is incomplete.'));
    const sourceId=clean(p.sourceProject&&p.sourceProject.id,160),source=currentProject(state,sourceId),frozenAt=clean(p.sourceProject&&p.sourceProject.updatedAt,80),currentAt=clean(source&&source.updatedAt,80);
    let stale=false;
    if(!source)checks.push(check('source-revision','Source revision','attention','Source project is not present in this browser; freshness cannot be compared.'));
    else if(frozenAt&&currentAt&&frozenAt!==currentAt){stale=true;checks.push(check('source-revision','Source revision','attention',`Source project changed after this package snapshot (${frozenAt} → ${currentAt}).`));}
    else checks.push(check('source-revision','Source revision','pass','Frozen package matches the current locally visible source-project revision.'));
    const summary=summarize(checks);return {schema:VALIDATION_SCHEMA,kind:'institutional-research-package',packageId:clean(p.id,160),sourceProjectId:sourceId,checks,...summary,stale,staleAcknowledgementRequired:stale,integrityVerified:Boolean(integrity.verified),contentIncluded:false};
  }
  function handoffDraftAssessment(handoff,project){
    const h=handoff&&typeof handoff==='object'?handoff:{},p=project&&typeof project==='object'?project:null,checks=[];
    checks.push(check('project','Source project',p&&p.id===h.projectId?'pass':'fail',p?'Source project is locally available.':'Source project is unavailable.'));
    checks.push(check('recipient','Receiving organization',clean(h.organizationLabel,200)?'pass':'fail',clean(h.organizationLabel,200)?'Receiving organization is named.':'Receiving organization is required.'));
    checks.push(check('purpose','Promotion purpose',clean(h.purpose,3000)?'pass':'fail',clean(h.purpose,3000)?'Promotion purpose is recorded.':'Promotion purpose is required.'));
    const ids=[...new Set(list(h.objectIds).map(String))],active=p?list(p.objects).filter(o=>ids.includes(o.id)&&!o.archivedAt):[];
    checks.push(check('scope','Canonical object scope',ids.length>0&&active.length===ids.length?'pass':'fail',ids.length>0&&active.length===ids.length?`${ids.length} selected canonical object${ids.length===1?'':'s'} are locally resolvable.`:'Selected object scope is empty or contains missing/archived objects.'));
    const a=h.acknowledgements||{},acks=a.copyModel===true&&a.institutionalGovernance===true&&a.sharingReviewed===true;
    checks.push(check('acknowledgements','Human acknowledgements',acks?'pass':'fail',acks?'Copy/governance/sharing acknowledgements are recorded.':'All institutional handoff acknowledgements are required.'));
    checks.push(check('target','Target product',h.targetProduct===TARGET_PRODUCT?'pass':'fail',h.targetProduct===TARGET_PRODUCT?'Catalyst Intelligence is the explicit target product.':'Institutional target product is unsupported.'));
    const summary=summarize(checks);return {schema:VALIDATION_SCHEMA,kind:'institutional-handoff-draft',handoffId:clean(h.id,160),sourceProjectId:clean(h.sourceProjectId||h.projectId,160),checks,...summary,stale:false,contentIncluded:false};
  }
  async function sha256Text(value,cryptoObj){
    const c=cryptoObj||(typeof globalThis!=='undefined'?globalThis.crypto:null);if(c&&c.subtle&&typeof TextEncoder!=='undefined'){const hash=await c.subtle.digest('SHA-256',new TextEncoder().encode(text(value)));return [...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,'0')).join('');}
    if(typeof require==='function'){try{return require('crypto').createHash('sha256').update(text(value)).digest('hex');}catch(_){}}
    return '';
  }
  async function handoffPackageAssessment(pkg,state,cryptoObj){
    const p=pkg&&typeof pkg==='object'?pkg:{},checks=[];
    checks.push(check('schema','Promotion package schema',p.schema===HANDOFF_PACKAGE_SCHEMA&&p.kind==='promotion'?'pass':'fail',p.schema===HANDOFF_PACKAGE_SCHEMA?'Supported promotion package.':'Unsupported institutional promotion package.'));
    const m=p.manifest||{},h=p.handoff||{},proj=p.project||{},ids=list(proj.objects).filter(o=>o&&!o.archivedAt).map(o=>o.id);
    const idsConsistent=clean(m.handoffId,160)===clean(h.id,160)&&clean(m.sourceProjectId,160)===clean(h.sourceProjectId,160)&&m.targetProduct===TARGET_PRODUCT&&h.targetProduct===TARGET_PRODUCT&&h.requestedMode==='institutional-copy';
    checks.push(check('identity','Handoff identity',idsConsistent?'pass':'fail',idsConsistent?'Manifest and handoff identity/target agree.':'Manifest and handoff identity/target do not agree.'));
    const recipient=clean(h.organizationLabel||m.organizationLabel,200),purpose=clean(h.purpose,3000);checks.push(check('recipient','Receiving organization',recipient?'pass':'fail',recipient?'Receiving organization is explicit.':'Receiving organization is missing.'));checks.push(check('purpose','Promotion purpose',purpose?'pass':'fail',purpose?'Promotion purpose is explicit.':'Promotion purpose is missing.'));
    const scopeOk=ids.length>0&&Number(m.objectCount)===ids.length;checks.push(check('scope','Promotion scope',scopeOk?'pass':'fail',scopeOk?`${ids.length} copied canonical object${ids.length===1?'':'s'} match the manifest.`:'Manifest object count does not match the copied project scope.'));
    const privacy=m.privacy||{},privacyOk=['deviceIdentityIncluded','accountIdentityIncluded','connectedToolHandoffStateIncluded','recentToolsIncluded','activityHistoryIncluded','aiReviewHistoryIncluded','collaborationHistoryIncluded'].every(k=>privacy[k]===false);checks.push(check('privacy','Privacy minimization',privacyOk?'pass':'fail',privacyOk?'Personal/session/collaboration history exclusions are explicit.':'Promotion privacy manifest is incomplete.'));
    const gov=m.governance||{},govOk=gov.sourceWorkspaceRetainsIndependentCopy===true&&gov.institutionalCopyCreated===true&&gov.institutionalGovernanceBeginsAfterAcceptance===true&&gov.automaticUpload===false&&gov.automaticSourceMutation===false;checks.push(check('governance','Source-workspace boundary',govOk?'pass':'fail',govOk?'Personal Workspace remains an independent source record.':'Source/receiver governance boundary is incomplete.'));
    const expected=clean(p.integrity&&p.integrity.payloadFingerprint,128),algorithm=clean(p.integrity&&p.integrity.algorithm,32),actual=await sha256Text(JSON.stringify({manifest:m,handoff:h,project:proj}),cryptoObj),integrityOk=algorithm==='SHA-256'&&expected&&actual&&expected===actual;
    checks.push(check('integrity','SHA-256 package integrity',integrityOk?'pass':'fail',integrityOk?'Promotion package SHA-256 matches its payload.':!actual?'SHA-256 verification is unavailable in this runtime.':'Promotion package fingerprint does not match its payload.'));
    const local=currentProject(state,clean(m.sourceProjectId,160)),frozenAt=clean(proj.updatedAt,80),currentAt=clean(local&&local.updatedAt,80);let stale=false;
    if(!local)checks.push(check('source-revision','Source revision','attention','Source project is not present locally; freshness cannot be compared.'));
    else if(frozenAt&&currentAt&&frozenAt!==currentAt){stale=true;checks.push(check('source-revision','Source revision','attention',`Source project changed after promotion copy (${frozenAt} → ${currentAt}).`));}
    else checks.push(check('source-revision','Source revision','pass','Promotion copy matches the current locally visible source-project revision.'));
    const readiness=list(m.readiness),attentionReadiness=readiness.filter(x=>x&&x.status==='attention').length;checks.push(check('readiness','Explainable readiness',attentionReadiness?'attention':'pass',attentionReadiness?`${attentionReadiness} explainable readiness item${attentionReadiness===1?'':'s'} require human review.`:'No readiness attention items are recorded.'));
    const summary=summarize(checks);return {schema:VALIDATION_SCHEMA,kind:'institutional-handoff-package',handoffId:clean(h.id,160),sourceProjectId:clean(m.sourceProjectId,160),checks,...summary,stale,staleAcknowledgementRequired:stale,readinessAttention:attentionReadiness,integrityVerified:integrityOk,contentIncluded:false};
  }
  function receiptKey(pkg){const p=pkg&&typeof pkg==='object'?pkg:{};return [clean(p.handoffId,160),clean(p.sourceProjectId,160),clean(p.status,40),clean(p.receivedAt,80),clean(p.integrity&&p.integrity.payloadFingerprint,128)].join('|');}
  async function receiptAssessment(pkg,state,cryptoObj){
    const p=pkg&&typeof pkg==='object'?pkg:{},checks=[];
    const schemaOk=p.schema===RECEIPT_SCHEMA&&p.targetProduct===TARGET_PRODUCT&&['received','accepted','declined'].includes(p.status);checks.push(check('schema','Receipt schema/status',schemaOk?'pass':'fail',schemaOk?'Supported institutional receipt.':'Unsupported institutional receipt schema, target, or status.'));
    const inst=state&&state.institutional||{},handoff=list(inst.handoffs).find(h=>h&&h.id===clean(p.handoffId,160)&&h.sourceProjectId===clean(p.sourceProjectId,160));checks.push(check('match','Local handoff match',handoff?'pass':'fail',handoff?'Receipt matches a locally prepared institutional handoff.':'Receipt does not match a local handoff and source project.'));
    const hist=list(inst.history),key=receiptKey(p),duplicate=hist.some(x=>x&&x.direction==='import'&&x.kind==='receipt'&&clean(x.handoffId,160)===clean(p.handoffId,160)&&clean(x.status,40)===clean(p.status,40)&&clean(x.fingerprint,128)&&clean(x.fingerprint,128)===clean(p.integrity&&p.integrity.payloadFingerprint,128));checks.push(check('duplicate','Duplicate receipt',duplicate?'fail':'pass',duplicate?'This exact fingerprinted receipt appears to have been committed already.':'No matching committed receipt fingerprint was found.'));
    const expected=clean(p.integrity&&p.integrity.payloadFingerprint,128);let verified=false,unverified=false;if(expected){const x=clone(p);delete x.integrity;const actual=await sha256Text(JSON.stringify(x),cryptoObj);verified=Boolean(actual&&actual===expected);checks.push(check('integrity','Receipt integrity',verified?'pass':'fail',verified?'Receipt SHA-256 matches its payload.':!actual?'SHA-256 verification is unavailable.':'Receipt fingerprint does not match its payload.'));}else{unverified=true;checks.push(check('integrity','Receipt integrity','attention','Receipt has no SHA-256 fingerprint; explicit owner acknowledgement is required before commit.'));}
    const staleTime=Boolean(handoff&&handoff.exportedAt&&p.receivedAt&&Date.parse(p.receivedAt)<Date.parse(handoff.exportedAt));checks.push(check('chronology','Receipt chronology',staleTime?'attention':'pass',staleTime?'Receipt timestamp predates local package export; inspect the receiving-system record.':'Receipt chronology is consistent with local export history.'));
    const summary=summarize(checks);return {schema:VALIDATION_SCHEMA,kind:'institutional-receipt',handoffId:clean(p.handoffId,160),sourceProjectId:clean(p.sourceProjectId,160),checks,...summary,duplicate,integrityVerified:verified,requiresUnverifiedAcknowledgement:unverified,chronologyAttention:staleTime,receiptKey:key,commitAllowed:summary.failed===0,contentIncluded:false};
  }
  function report(items,workspaceVersion='',nowFn){const at=typeof nowFn==='function'?nowFn():new Date().toISOString(),rows=list(items);return {schema:REPORT_SCHEMA,workspaceVersion:clean(workspaceVersion,40),generatedAt:at,summary:{items:rows.length,blocked:rows.filter(x=>x.status==='blocked').length,attention:rows.filter(x=>x.status==='attention').length,pass:rows.filter(x=>x.status==='pass').length},items:rows.map(x=>({kind:x.kind||'',packageId:x.packageId||'',handoffId:x.handoffId||'',sourceProjectId:x.sourceProjectId||'',status:x.status,failed:x.failed||0,attention:x.attention||0,stale:Boolean(x.stale),integrityVerified:Boolean(x.integrityVerified)})),privacy:{projectContentIncluded:false,recordTitlesIncluded:false,purposeTextIncluded:false,recipientLabelIncluded:false,sourceUrlsIncluded:false,deviceIdentifierIncluded:false,accountIdentityIncluded:false},governance:{advisoryNotScored:true,automaticTransfer:false,automaticIngestion:false,automaticSourceMutation:false,organizationPermissionsCreated:false}};}
  function policy(){return {schema:POLICY_SCHEMA,workspaceVersion:'0.75.0',researchPackageScopeExact:true,recipientRequired:true,purposeRequired:true,sourceRevisionComparison:true,staleRequiresAcknowledgement:true,promotionSha256Required:true,receiptMatchRequired:true,duplicateReceiptBlocked:true,unsignedReceiptRequiresAcknowledgement:true,readinessIsExplainableNotScored:true,automaticUpload:false,automaticIngestion:false,automaticSourceMutation:false,organizationPermissionsInWorkspace:false,sourceWorkspaceIndependent:true,schemaMigration:false};}
  return {VALIDATION_SCHEMA,REPORT_SCHEMA,POLICY_SCHEMA,RESEARCH_PACKAGE_SCHEMA,HANDOFF_PACKAGE_SCHEMA,RECEIPT_SCHEMA,TARGET_PRODUCT,check,summarize,currentProject,researchPackageAssessment,handoffDraftAssessment,sha256Text,handoffPackageAssessment,receiptKey,receiptAssessment,report,policy};
});
