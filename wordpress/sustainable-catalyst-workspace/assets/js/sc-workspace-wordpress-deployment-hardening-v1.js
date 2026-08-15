(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceWordPressDeploymentHardening=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-wordpress-deployment-hardening/1.0';
  const REPORT_SCHEMA='sc-workspace-wordpress-deployment-report/1.0';
  const CHECKLIST_SCHEMA='sc-workspace-wordpress-deployment-checklist/1.0';
  const RELEASE_VERSION='1.10.0';
  const PREVIOUS_RELEASE='1.9.0';
  const ROLLBACK_RELEASE='1.9.0';
  const EXPECTED_SCRIPT='workspace-v1.10.0.js';
  const EXPECTED_STYLE='workspace-v1.10.0.css';
  const checks=Object.freeze([
    ['root-version','Workspace runtime version','The rendered Workspace root must report the current v1.10.0 release.'],
    ['localized-version','Localized WordPress version','The WordPress-localized identity configuration must agree with the rendered runtime version.'],
    ['server-state','Server package state','The server-side deployment marker and required release files must be coherent.'],
    ['current-script','Current cumulative JavaScript','The page must load workspace-v1.10.0.js rather than an older cumulative shell.'],
    ['current-style','Current cumulative stylesheet','The page must load workspace-v1.10.0.css rather than an older cumulative stylesheet.'],
    ['asset-query','WordPress asset cache version','Current cumulative assets must carry the current WordPress version query when query strings are present.'],
    ['release-stage','Release stage','The deployment must identify either the inherited release-candidate stage or the General Availability stage.'],
    ['release-candidate','Inherited Release Candidate runtime','The Release Candidate I runtime must still be available after deployment hardening.']
  ].map(([id,label,detail])=>Object.freeze({id,label,detail})));
  const manualItems=Object.freeze([
    ['upload-metadata','WordPress replacement metadata','Before replacement, verify WordPress shows Uploaded Version 1.10.0 and the expected author/requirements.'],
    ['activation-smoke','Activation and public-page smoke','Activate/replace the plugin and verify the public Workspace reaches the site footer without a PHP critical error or broken application shell.'],
    ['rest-health','REST health identity','Verify /wp-json/sc-workspace/v1/health reports version 1.10.0 and the deployment-hardening contract is reachable.'],
    ['logged-out-in','Anonymous and authenticated smoke','Open the Workspace logged out and logged in; confirm the local-first workspace remains usable in both states.'],
    ['project-preservation','Local project preservation','Open a representative existing browser-local project after upgrade and confirm it is unchanged before performing any sync/import action.'],
    ['cache-coherence','Cache/coherence verification','If a mixed-version warning appears, purge only the relevant WordPress/CDN/browser page/asset caches and reload; do not alter project storage as a cache remedy.'],
    ['rollback-rehearsal','v1.9.0 rollback rehearsal','Verify the bundled v1.9.0 WordPress rollback artifact can be restored and existing browser-local projects remain readable.']
  ].map(([id,label,procedure])=>Object.freeze({id,label,procedure})));
  const stamp=()=>new Date().toISOString();
  const finding=(id,label,pass,detail)=>({id,label,state:pass?'pass':'blocked',detail:String(detail||'')});
  function parseAsset(doc,kind,expected){
    const nodes=kind==='script'?[...(doc?.querySelectorAll?.('script[src]')||[])]:[...(doc?.querySelectorAll?.('link[rel="stylesheet"][href]')||[])];
    const attr=kind==='script'?'src':'href';
    const match=nodes.map(node=>String(node.getAttribute?.(attr)||node[attr]||'')).find(value=>value.includes(expected))||'';
    const stale=nodes.map(node=>String(node.getAttribute?.(attr)||node[attr]||'')).filter(value=>/workspace-v\d+\.\d+\.\d+\.(?:js|css)/.test(value)&&!value.includes(expected));
    return {present:Boolean(match),url:match,stale};
  }
  function versionQueryMatches(url){
    if(!url)return false;
    const q=String(url).split('?')[1]||'';
    if(!q)return true; // fixtures/offline renderers may omit WordPress query strings.
    try{return new URLSearchParams(q).get('ver')===RELEASE_VERSION;}catch(_){return q.includes(`ver=${RELEASE_VERSION}`);}
  }
  function assess(workspaceRoot,options={}){
    const env=options.env||globalThis,doc=options.document||env.document||null;
    const rootVersion=String(workspaceRoot?.dataset?.version||'');
    const localizedVersion=String(env.SCWorkspaceIdentity?.workspaceVersion||'');
    const serverState=String(workspaceRoot?.dataset?.scwDeploymentServerState||workspaceRoot?.dataset?.deploymentServerState||'');
    const releaseStage=String(workspaceRoot?.dataset?.releaseStage||'');
    const script=parseAsset(doc,'script',EXPECTED_SCRIPT),style=parseAsset(doc,'style',EXPECTED_STYLE);
    const out=[];
    out.push(finding('root-version','Workspace runtime version',rootVersion===RELEASE_VERSION,`Root reports ${rootVersion||'unset'}; expected ${RELEASE_VERSION}.`));
    out.push(finding('localized-version','Localized WordPress version',localizedVersion===RELEASE_VERSION,`Localized configuration reports ${localizedVersion||'unset'}; expected ${RELEASE_VERSION}.`));
    out.push(finding('server-state','Server package state',serverState==='server-ready',`Server deployment state is ${serverState||'unset'}; expected server-ready.`));
    out.push(finding('current-script','Current cumulative JavaScript',script.present&&script.stale.length===0,script.present?`${EXPECTED_SCRIPT} is present${script.stale.length?`; ${script.stale.length} stale cumulative script(s) also detected.`:'.'}`:`${EXPECTED_SCRIPT} is not present in the document.`));
    out.push(finding('current-style','Current cumulative stylesheet',style.present&&style.stale.length===0,style.present?`${EXPECTED_STYLE} is present${style.stale.length?`; ${style.stale.length} stale cumulative stylesheet(s) also detected.`:'.'}`:`${EXPECTED_STYLE} is not present in the document.`));
    out.push(finding('asset-query','WordPress asset cache version',versionQueryMatches(script.url)&&versionQueryMatches(style.url),'Current cumulative assets use the current WordPress version query, or the offline fixture omits query strings.'));
    out.push(finding('release-stage','Release stage',['release-candidate','general-availability','ga-stabilization','workspace-home','universal-search','library-continuity','knowledge-graph-explorer','lab-scientific-integration','workbench-decision-roundtrip','cross-device-production','shared-review-rooms','institutional-audit-studio','research-operations'].includes(releaseStage),`Workspace stage is ${releaseStage||'unset'}; expected release-candidate, general-availability, ga-stabilization, workspace-home, universal-search, or library-continuity, knowledge-graph-explorer, lab-scientific-integration, workbench-decision-roundtrip, or cross-device-production, or shared-review-rooms, institutional-audit-studio, or research-operations.`));
    out.push(finding('release-candidate','Inherited Release Candidate runtime',Boolean(env.SCWorkspaceReleaseCandidateI),env.SCWorkspaceReleaseCandidateI?'Release Candidate I runtime is available.':'Release Candidate I runtime is unavailable.'));
    const blocked=out.filter(x=>x.state==='blocked').length;
    return {schema:SCHEMA,generatedAt:stamp(),workspaceVersion:RELEASE_VERSION,state:blocked?'blocked':'deployment-automated-ready',automatedDeploymentGate:blocked===0,knownAutomatedBlockerCount:blocked,checks:out,assets:{expectedScript:EXPECTED_SCRIPT,expectedStyle:EXPECTED_STYLE,scriptPresent:script.present,stylePresent:style.present,staleScriptCount:script.stale.length,staleStyleCount:style.stale.length},manualFieldItems:manualItems.map(x=>({...x,state:'manual'})),claimBoundary:'Automated deployment coherence is not proof of production WordPress health. Activation, public-page, cache, preservation, and rollback checks remain explicit human work.',governance:{releaseCandidate:true,featureFreeze:true,schemaMigration:false,projectDataRead:false,projectDataMutation:false,automaticCachePurge:false,automaticRollback:false,automaticProjectMigration:false,telemetry:false,hiddenScore:false}};
  }
  function report(version,result){return{schema:REPORT_SCHEMA,generatedAt:stamp(),workspaceVersion:String(version||RELEASE_VERSION).slice(0,40),assessment:result||null,privacy:{projectContentIncluded:false,projectTitlesIncluded:false,sourceContentIncluded:false,sourceUrlsIncluded:false,storageValuesIncluded:false,storageKeysIncluded:false,accountIdentityIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,serverFilesystemPathsIncluded:false,automaticSubmission:false},governance:{releaseCandidate:true,featureFreeze:true,automaticCachePurge:false,automaticRollback:false,automaticProjectMigration:false,canonicalMutation:false,telemetry:false}};}
  function checklist(version){return{schema:CHECKLIST_SCHEMA,generatedAt:stamp(),workspaceVersion:String(version||RELEASE_VERSION).slice(0,40),rollbackRelease:ROLLBACK_RELEASE,items:manualItems.map(x=>({...x,state:'not-verified'})),instructions:'Perform these checks on the deployed WordPress Release Candidate. A green automated gate does not close the manual items.',governance:{manual:true,automaticCompletion:false,automaticSubmission:false,projectDataMutation:false}};}
  function contract(){return{schema:SCHEMA,reportSchema:REPORT_SCHEMA,checklistSchema:CHECKLIST_SCHEMA,releaseVersion:RELEASE_VERSION,previousRelease:PREVIOUS_RELEASE,rollbackRelease:ROLLBACK_RELEASE,releaseCandidate:true,featureFreeze:true,storageSchemaVersion:35,projectSchema:'sc-workspace-project/20.0',projectExportSchema:'sc-workspace-project-export/20.0',schemaMigrationRequired:false,safeBootstrapGuard:true,activationPreflight:true,boundedDeploymentHistory:true,mixedVersionBrowserDetection:true,versionedAssetFilenames:true,rollbackArtifactRequired:true,automaticCachePurge:false,automaticRollback:false,automaticProjectMigration:false,projectDataRead:false,projectDataMutation:false,telemetry:false};}
  return Object.freeze({SCHEMA,REPORT_SCHEMA,CHECKLIST_SCHEMA,RELEASE_VERSION,PREVIOUS_RELEASE,ROLLBACK_RELEASE,EXPECTED_SCRIPT,EXPECTED_STYLE,checks,manualItems,assess,report,checklist,contract});
});
