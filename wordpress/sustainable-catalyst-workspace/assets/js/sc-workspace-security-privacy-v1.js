(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceSecurityPrivacy=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-security-privacy-audit/1.0';
  const THREAT_MODEL_SCHEMA='sc-workspace-threat-model/1.0';
  const PORTABILITY_SCHEMA='sc-workspace-data-portability-bundle/1.0';
  const DELETION_SCHEMA='sc-workspace-deletion-receipt/1.0';
  const PREFIX='sc_workspace';
  const CONFIRM_PHRASE='DELETE WORKSPACE DATA';
  const DISCLOSURE_KEYS=new Set([
    'sc_workspace_api_embed_v1','sc_workspace_shared_review_handoff_v1','sc_workspace_shared_review_packages_v1',
    'sc_workspace_institutional_research_packages_v1','sc_workspace_handoff_v2','sc_workspace_handoff_return_v1',
    'sc_workspace_institutional_receipt_v1','sc_workspace_ai_request_v1','sc_workspace_ai_response_v1',
    'sc_workspace_notebook_assistance_request_v1','sc_workspace_notebook_assistance_response_v1'
  ]);
  const RECOVERY_KEYS=new Set(['sc_workspace_last_good_v1','sc_workspace_recovery_v0_8_2']);
  const KNOWN_STORES=Object.freeze([
    ['sc_workspace','Canonical Workspace state','canonical-private'],['sc_workspace_v0_1','Legacy Workspace state','legacy-private'],
    ['sc_workspace_last_good_v1','Last-known-good recovery snapshot','recovery-private'],['sc_workspace_recovery_v0_8_2','Damaged-state recovery envelope','recovery-private'],
    ['sc_workspace_device_v1','Local device identifier','identity-local'],['sc_workspace_handoff_v2','Portable handoff ledger','exchange-private'],
    ['sc_workspace_handoff_return_v1','Handoff return packet','exchange-private'],['sc_workspace_processed_returns_v1','Processed return identifiers','exchange-local'],
    ['sc_workspace_notebook_capture_v1','Notebook capture session','research-private'],['sc_workspace_notebook_assistance_request_v1','Notebook assistance request','assistance-private'],
    ['sc_workspace_notebook_assistance_response_v1','Notebook assistance response','assistance-private'],['sc_workspace_ai_request_v1','AI request packet','assistance-private'],
    ['sc_workspace_ai_response_v1','AI response packet','assistance-private'],['sc_workspace_institutional_receipt_v1','Institutional receipt','exchange-private'],
    ['sc_workspace_saved_searches_v1','Saved research searches','preference-local'],['sc_workspace_research_collections_v1','Research collection definitions','research-local'],
    ['sc_workspace_research_views_v1','Research view definitions','preference-local'],['sc_workspace_reference_library_v1','Reference library','research-private'],
    ['sc_workspace_citation_preferences_v1','Citation preferences','preference-local'],['sc_workspace_composition_library_v1','Composition drafts','research-private'],
    ['sc_workspace_cross_project_knowledge_v1','Cross-project reference ledger','research-private'],['sc_workspace_research_templates_v1','Research templates','research-local'],
    ['sc_workspace_experience_v0500','Experience preferences','preference-local'],['sc_workspace_grounded_research_assistant_v1','Grounded research sessions','assistance-private'],
    ['sc_workspace_research_tasks_v1','Research task ledger','research-private'],['sc_workspace_collaboration_architecture_v1','Collaboration architecture','collaboration-private'],
    ['sc_workspace_shared_review_handoff_v1','Shared review handoffs','exchange-private'],['sc_workspace_api_embed_v1','Read-only API/embed projections','disclosure-artifact'],
    ['sc_workspace_research_automation_v1','Research automation declarations','research-private'],['sc_workspace_institutional_research_packages_v1','Institutional research packages','disclosure-artifact']
  ].map(([key,label,dataClass])=>Object.freeze({key,label,dataClass,portable:true,deletableLocally:true})));
  const KNOWN_BY_KEY=new Map(KNOWN_STORES.map(x=>[x.key,x]));
  const text=v=>String(v==null?'':v);
  const bytes=v=>{try{return typeof TextEncoder!=='undefined'?new TextEncoder().encode(text(v)).length:unescape(encodeURIComponent(text(v))).length;}catch(_){return text(v).length;}};
  const stable=v=>{if(Array.isArray(v))return v.map(stable);if(v&&typeof v==='object'){const o={};Object.keys(v).sort().forEach(k=>{o[k]=stable(v[k]);});return o;}return v;};
  function fnv1a(value){let h=0x811c9dc5;const s=JSON.stringify(stable(value));for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193);}return ('00000000'+(h>>>0).toString(16)).slice(-8);}
  function storageKeys(storage){const out=[];if(!storage)return out;try{for(let i=0;i<storage.length;i++){const k=storage.key(i);if(k&&k.startsWith(PREFIX))out.push(k);}}catch(_){}return [...new Set(out)].sort();}
  function inventory(storage){
    const keys=storageKeys(storage);return keys.map(key=>{let raw='';try{raw=text(storage.getItem(key)||'');}catch(_){}const known=KNOWN_BY_KEY.get(key);return {key,label:known?known.label:'Unclassified Workspace-owned store',dataClass:known?known.dataClass:'unclassified-private',known:Boolean(known),bytes:bytes(raw),hasData:raw.length>0,portable:true,deletableLocally:true,disclosureArtifact:DISCLOSURE_KEYS.has(key),recoveryArtifact:RECOVERY_KEYS.has(key)};});
  }
  function threatModel(){return {schema:THREAT_MODEL_SCHEMA,boundaries:[
    {id:'browser-local',title:'Browser-local primary storage',status:'declared',detail:'Workspace primary state and supporting ledgers are stored in the browser profile. Same-origin scripts and anyone with access to that browser profile may be able to read them.'},
    {id:'encryption',title:'Encryption at rest',status:'not-provided',detail:'Workspace does not claim application-level encryption of browser localStorage. Device/browser security remains part of the threat model.'},
    {id:'integrity',title:'Integrity fingerprints',status:'integrity-only',detail:'Workspace fingerprints detect mismatched/tampered portable packages where implemented. A fingerprint is not encryption, authentication, or authorization.'},
    {id:'server',title:'Server/cloud boundary',status:'separate',detail:'Account backups, sync heads, and WordPress server data are separate from browser-local deletion and require their own authenticated lifecycle controls.'},
    {id:'disclosure',title:'Disclosure actions',status:'explicit',detail:'API/embed projections, review handoffs, institutional packages, and portable exports are explicit disclosure actions; private research is not publicly enumerable by default.'},
    {id:'automation',title:'Automation boundary',status:'manual',detail:'Research automation schedules are declarations. They do not run as browser-closed background daemons or silently mutate canonical research.'}
  ],nonClaims:{endToEndEncryption:false,localStorageEncryption:false,fingerprintIsAuthentication:false,durableReferenceIsAuthorization:false,publicProjectEnumeration:false,backgroundAutomation:false}};}
  function audit(storage,options={}){
    const stores=inventory(storage),totalBytes=stores.reduce((n,x)=>n+x.bytes,0),unknown=stores.filter(x=>!x.known),disclosure=stores.filter(x=>x.disclosureArtifact&&x.hasData),recovery=stores.filter(x=>x.recoveryArtifact&&x.hasData);
    const findings=[];
    if(options.storageAvailable===false)findings.push({severity:'critical',code:'storage-unavailable',message:'Browser local storage is unavailable; persistence, portability, and verified local deletion cannot be guaranteed in this context.'});
    if(unknown.length)findings.push({severity:'attention',code:'unclassified-stores',message:`${unknown.length} Workspace-owned storage key${unknown.length===1?' is':'s are'} not in the current audit registry.`});
    if(disclosure.length)findings.push({severity:'attention',code:'disclosure-artifacts',message:`${disclosure.length} local disclosure/exchange artifact store${disclosure.length===1?' contains':'s contain'} data. Review before sharing the device or exporting a full bundle.`});
    findings.push({severity:'boundary',code:'localstorage-plaintext-boundary',message:'Workspace does not claim application-level encryption of browser localStorage.'});
    if(options.serverBackupsKnown) findings.push({severity:'boundary',code:'server-backup-separate',message:'Server/account backups are outside browser-local deletion scope.'});
    return {schema:SCHEMA,generatedAt:options.now||new Date().toISOString(),stores,totalBytes,counts:{stores:stores.length,unknown:unknown.length,disclosureArtifacts:disclosure.length,recoveryArtifacts:recovery.length},findings,threatModel:threatModel(),portability:{browserLocalCoverage:'complete-prefix-inventory',includesUnknownWorkspaceKeys:true,serverDataIncluded:false},deletion:{browserLocalVerified:true,serverDeletionSeparate:true,unrelatedLocalStorageUntouched:true},governance:{advisoryAudit:true,automaticDeletion:false,automaticUpload:false,automaticDisclosure:false,canonicalMutation:false}};
  }
  function buildPortabilityBundle(storage,options={}){
    const keys=storageKeys(storage),stores={};keys.forEach(k=>{try{stores[k]=text(storage.getItem(k)||'');}catch(_){stores[k]='';}});
    const payload={schema:PORTABILITY_SCHEMA,createdAt:options.now||new Date().toISOString(),workspaceVersion:options.workspaceVersion||'',warning:'Contains private Workspace browser-local data. Protect this file accordingly.',scope:{browserLocalWorkspacePrefix:PREFIX,serverAccountDataIncluded:false,unrelatedBrowserDataIncluded:false},stores};
    return {...payload,fingerprint:{algorithm:'fnv1a-32-integrity-receipt-not-encryption',value:fnv1a(payload)}};
  }
  function verifyPortabilityBundle(pkg){if(!pkg||pkg.schema!==PORTABILITY_SCHEMA||!pkg.fingerprint)return{ok:false,reason:'schema'};const {fingerprint,...payload}=pkg;return {ok:fingerprint.value===fnv1a(payload),reason:fingerprint.value===fnv1a(payload)?'ok':'fingerprint'};}
  function deletionPlan(storage){const keys=storageKeys(storage);return {schema:'sc-workspace-deletion-plan/1.0',keys,count:keys.length,scope:'browser-local-workspace-prefix-only',requiresPhrase:CONFIRM_PHRASE,serverBackupsIncluded:false,unrelatedLocalStorageIncluded:false};}
  function executeDeletion(storage,confirmation,options={}){
    const before=storageKeys(storage);if(confirmation!==CONFIRM_PHRASE)return{ok:false,reason:'confirmation',removed:[],failed:[],remaining:before};const removed=[],failed=[];for(const key of before){try{storage.removeItem(key);if(storage.getItem(key)===null)removed.push(key);else failed.push(key);}catch(_){failed.push(key);}}
    const remaining=storageKeys(storage),payload={schema:DELETION_SCHEMA,executedAt:options.now||new Date().toISOString(),scope:'browser-local-workspace-prefix-only',removed,failed,remaining,serverBackupsDeleted:false,unrelatedLocalStorageTouched:false,verified:failed.length===0&&remaining.length===0};return {...payload,ok:payload.verified,fingerprint:{algorithm:'fnv1a-32-integrity-receipt-not-encryption',value:fnv1a(payload)}};
  }
  function contract(){return {schema:SCHEMA,threatModelSchema:THREAT_MODEL_SCHEMA,portabilitySchema:PORTABILITY_SCHEMA,deletionSchema:DELETION_SCHEMA,features:{workspaceStoreInventory:true,unknownWorkspaceKeyDetection:true,explicitFullBrowserLocalExport:true,verifiedBrowserLocalDeletion:true,recoveryBoundaryAudit:true,disclosureArtifactAudit:true,schemaStable:true},privacy:{browserLocalPrimary:true,localStorageEncryptionClaim:false,serverDataSeparate:true,privateByDefault:true},governance:{explicitExport:true,typedDeletionConfirmation:true,noAutomaticDeletion:true,noAutomaticUpload:true,noAutomaticDisclosure:true,noCanonicalMutation:true}};}
  return {SCHEMA,THREAT_MODEL_SCHEMA,PORTABILITY_SCHEMA,DELETION_SCHEMA,PREFIX,CONFIRM_PHRASE,KNOWN_STORES,bytes,stable,fnv1a,storageKeys,inventory,threatModel,audit,buildPortabilityBundle,verifyPortabilityBundle,deletionPlan,executeDeletion,contract};
});
