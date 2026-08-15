(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceProductionCertification=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-production-certification/1.0';
  const REPORT_SCHEMA='sc-workspace-production-certification-report/1.0';
  const CHECKLIST_SCHEMA='sc-workspace-production-certification-checklist/1.0';
  const RELEASE_VERSION='0.82.1';
  const PREVIOUS_RELEASE='0.82.0';
  const ROLLBACK_RELEASE='0.81.0';
  const EXPECTED_SCRIPT='workspace-v0.82.1.js';
  const EXPECTED_STYLE='workspace-v0.82.1.css';
  const manualItems=Object.freeze([
    ['public-page','Public Workspace smoke','Load the production Workspace as a normal visitor and confirm the complete application shell reaches the site footer without a PHP critical error.'],
    ['rest-identity','Production REST identity','Verify /wp-json/sc-workspace/v1/health and /production-certification-contract both report v0.82.1.'],
    ['logged-out-in','Anonymous and authenticated smoke','Open Workspace logged out and logged in and confirm local-first use remains available in both states.'],
    ['project-preservation','Existing local project preservation','Open a representative pre-upgrade browser-local project and verify its content before any sync, import, or restore action.'],
    ['cache-coherence','WordPress/CDN/browser cache coherence','Verify the HTML, current cumulative JS, and current cumulative CSS all identify v0.82.1. If they do not, purge only page/asset caches—never Workspace project storage.'],
    ['rollback','v0.81.0 rollback rehearsal','Replace v0.82.1 with the bundled v0.81.0 rollback plugin, verify the public shell and existing local project, then reinstall v0.82.1 and repeat the smoke.']
  ].map(([id,label,procedure])=>Object.freeze({id,label,procedure})));
  const stamp=()=>new Date().toISOString();
  const finding=(id,label,pass,detail)=>({id,label,state:pass?'pass':'blocked',detail:String(detail||'')});
  function assetState(doc,kind,expected){
    const nodes=kind==='script'?[...(doc?.querySelectorAll?.('script[src]')||[])]:[...(doc?.querySelectorAll?.('link[rel="stylesheet"][href]')||[])];
    const attr=kind==='script'?'src':'href';
    const urls=nodes.map(n=>String(n.getAttribute?.(attr)||n[attr]||''));
    const current=urls.find(v=>v.includes(expected))||'';
    const cumulative=urls.filter(v=>/workspace-v0\.\d+\.\d+\.(?:js|css)(?:\?|$)/.test(v));
    const stale=cumulative.filter(v=>!v.includes(expected));
    return {present:Boolean(current),url:current,cumulativeCount:cumulative.length,stale};
  }
  function versionQueryMatches(url){
    if(!url)return false;
    const q=String(url).split('?')[1]||'';
    if(!q)return true;
    try{return new URLSearchParams(q).get('ver')===RELEASE_VERSION;}catch(_){return q.includes(`ver=${RELEASE_VERSION}`);}
  }
  function assess(workspaceRoot,options={}){
    const env=options.env||globalThis,doc=options.document||env.document||null;
    const rootVersion=String(workspaceRoot?.dataset?.version||'');
    const localizedVersion=String(env.SCWorkspaceIdentity?.workspaceVersion||'');
    const releaseStage=String(workspaceRoot?.dataset?.releaseStage||'');
    const serverState=String(workspaceRoot?.dataset?.scwDeploymentServerState||workspaceRoot?.dataset?.deploymentServerState||'');
    const script=assetState(doc,'script',EXPECTED_SCRIPT),style=assetState(doc,'style',EXPECTED_STYLE);
    const checks=[];
    checks.push(finding('runtime','Workspace runtime identity',rootVersion===RELEASE_VERSION,`Root reports ${rootVersion||'unset'}; expected ${RELEASE_VERSION}.`));
    checks.push(finding('localized','WordPress localized identity',localizedVersion===RELEASE_VERSION,`Localized runtime reports ${localizedVersion||'unset'}; expected ${RELEASE_VERSION}.`));
    checks.push(finding('server','Deployment server state',serverState==='server-ready',`Server deployment state is ${serverState||'unset'}; expected server-ready.`));
    checks.push(finding('script','Current cumulative JavaScript',script.present&&script.stale.length===0&&script.cumulativeCount===1,script.present?`${EXPECTED_SCRIPT} is loaded; ${script.stale.length} stale cumulative script(s) detected.`:`${EXPECTED_SCRIPT} is missing.`));
    checks.push(finding('style','Current cumulative stylesheet',style.present&&style.stale.length===0&&style.cumulativeCount===1,style.present?`${EXPECTED_STYLE} is loaded; ${style.stale.length} stale cumulative stylesheet(s) detected.`:`${EXPECTED_STYLE} is missing.`));
    checks.push(finding('query','Current cache-busting version',versionQueryMatches(script.url)&&versionQueryMatches(style.url),'Current cumulative asset version queries match v0.82.1, or an offline fixture omits query strings.'));
    checks.push(finding('stage','Release Candidate stage',releaseStage==='release-candidate',`Workspace stage is ${releaseStage||'unset'}; expected release-candidate.`));
    checks.push(finding('deployment-runtime','Inherited deployment hardening',Boolean(env.SCWorkspaceWordPressDeploymentHardening),env.SCWorkspaceWordPressDeploymentHardening?'v0.81 deployment hardening remains available.':'Deployment hardening runtime is unavailable.'));
    checks.push(finding('rc-runtime','Inherited Release Candidate runtime',Boolean(env.SCWorkspaceReleaseCandidateI),env.SCWorkspaceReleaseCandidateI?'Release Candidate runtime remains available.':'Release Candidate runtime is unavailable.'));
    const blocked=checks.filter(x=>x.state==='blocked').length;
    return {schema:SCHEMA,generatedAt:stamp(),workspaceVersion:RELEASE_VERSION,state:blocked?'blocked':'package-ready',packageAutomatedGate:blocked===0,knownAutomatedBlockerCount:blocked,productionCertified:false,checks,assets:{expectedScript:EXPECTED_SCRIPT,expectedStyle:EXPECTED_STYLE,scriptPresent:script.present,stylePresent:style.present,staleScriptCount:script.stale.length,staleStyleCount:style.stale.length},manualFieldItems:manualItems.map(x=>({...x,state:'manual-pending'})),claimBoundary:'Package-ready evidence does not certify the live WordPress deployment. Production certification requires the explicit public-page, REST, cache, project-preservation, and rollback field checks.',governance:{releaseCandidate:true,featureFreeze:true,schemaMigration:false,projectDataRead:false,projectDataMutation:false,automaticCachePurge:false,automaticRollback:false,automaticProjectMigration:false,automaticProductionCertification:false,telemetry:false,hiddenScore:false}};
  }
  function report(version,result){return{schema:REPORT_SCHEMA,generatedAt:stamp(),workspaceVersion:String(version||RELEASE_VERSION).slice(0,40),rollbackRelease:ROLLBACK_RELEASE,assessment:result||null,productionCertified:false,privacy:{projectContentIncluded:false,projectTitlesIncluded:false,sourceContentIncluded:false,sourceUrlsIncluded:false,storageValuesIncluded:false,storageKeysIncluded:false,accountIdentityIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,serverFilesystemPathsIncluded:false,automaticSubmission:false},governance:{releaseCandidate:true,featureFreeze:true,automaticCachePurge:false,automaticRollback:false,automaticProjectMigration:false,canonicalMutation:false,automaticProductionCertification:false,telemetry:false}};}
  function checklist(version){return{schema:CHECKLIST_SCHEMA,generatedAt:stamp(),workspaceVersion:String(version||RELEASE_VERSION).slice(0,40),rollbackRelease:ROLLBACK_RELEASE,items:manualItems.map(x=>({...x,state:'not-verified'})),instructions:'Perform these checks on the live production WordPress deployment. The packaged automated gate cannot complete them for you.',governance:{manual:true,automaticCompletion:false,automaticSubmission:false,projectDataMutation:false}};}
  function contract(){return{schema:SCHEMA,reportSchema:REPORT_SCHEMA,checklistSchema:CHECKLIST_SCHEMA,releaseVersion:RELEASE_VERSION,previousRelease:PREVIOUS_RELEASE,rollbackRelease:ROLLBACK_RELEASE,releaseCandidate:true,featureFreeze:true,storageSchemaVersion:35,projectSchema:'sc-workspace-project/20.0',projectExportSchema:'sc-workspace-project-export/20.0',schemaMigrationRequired:false,packageSmokeGate:true,cacheVersionCoherenceGate:true,rollbackRehearsalTooling:true,rollbackArtifactRequired:true,liveProductionChecksManual:true,automaticCachePurge:false,automaticRollback:false,automaticProjectMigration:false,automaticProductionCertification:false,projectDataRead:false,projectDataMutation:false,telemetry:false};}
  return Object.freeze({SCHEMA,REPORT_SCHEMA,CHECKLIST_SCHEMA,RELEASE_VERSION,PREVIOUS_RELEASE,ROLLBACK_RELEASE,EXPECTED_SCRIPT,EXPECTED_STYLE,manualItems,assess,report,checklist,contract});
});
