(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspacePublicBetaII=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-public-beta-ii/1.0';
  const GATE_SCHEMA='sc-workspace-beta-gate/1.0';
  const SNAPSHOT_SCHEMA='sc-workspace-beta-field-snapshot/1.0';
  const now=()=>new Date().toISOString();
  const text=(v,max=500)=>String(v==null?'':v).trim().slice(0,max);
  function routeHealth(root){
    const sections=root&&root.querySelectorAll?Array.from(root.querySelectorAll('[data-scw-workspace-section]')):[];
    const visible=sections.filter(el=>!el.hidden && !(typeof getComputedStyle==='function'&&getComputedStyle(el).display==='none'));
    return {sectionCount:sections.length,visibleCount:visible.length,visibleViews:visible.map(el=>text(el.getAttribute('data-scw-workspace-section'),80)),isolated:visible.length<=1};
  }
  function recovery(env=globalThis){
    const win=env.window||env; let lastKnownGood=false,recoveryEnvelope=false,restorePoints=0;
    try{const e=JSON.parse(win.localStorage?.getItem('sc_workspace_last_good_v1')||'null');lastKnownGood=Boolean(e&&typeof e.raw==='string'&&e.raw.length);}catch(_){}
    try{recoveryEnvelope=Boolean(win.localStorage?.getItem('sc_workspace_recovery_v0_8_2'));}catch(_){}
    try{const s=JSON.parse(win.localStorage?.getItem('sc_workspace')||'null');restorePoints=Array.isArray(s?.versionHistory?.restorePoints)?s.versionHistory.restorePoints.length:0;}catch(_){}
    return {lastKnownGood,recoveryEnvelope,restorePoints,available:lastKnownGood||recoveryEnvelope||restorePoints>0};
  }
  function capability(env=globalThis){
    const win=env.window||env;let storage=false;try{const k='__scw_beta_ii_probe__';win.localStorage.setItem(k,'1');storage=win.localStorage.getItem(k)==='1';win.localStorage.removeItem(k);}catch(_){}
    return {localStorage:storage,sessionStorage:Boolean(win.sessionStorage),webCryptoSha256:Boolean((env.crypto||win.crypto)?.subtle?.digest),fileApi:Boolean(win.File&&win.FileReader&&win.Blob)};
  }
  function check(id,label,state,detail,route=''){return {id,label,state,detail,route};}
  function assess(input={}){
    const caps=input.capabilities||{}; const rh=input.routeHealth||{}; const rec=input.recovery||{};
    const checks=[
      check('storage','Local persistence',caps.localStorage?'ready':'limited',caps.localStorage?'Browser-local Workspace storage is writable.':'Browser-local storage is unavailable or blocked.','security'),
      check('integrity','Integrity support',caps.webCryptoSha256?'ready':'attention',caps.webCryptoSha256?'Web Crypto SHA-256 is available.':'SHA-256 integrity support is limited in this browser.','security'),
      check('files','Portable files',caps.fileApi?'ready':'limited',caps.fileApi?'File import/export APIs are available.':'File import/export APIs are unavailable.','interoperability'),
      check('shell','Focused application shell',rh.isolated?'ready':'attention',rh.isolated?'Inactive Workspace routes are isolated.':`${Number(rh.visibleCount||0)} Workspace routes appear visible at once.`,'start'),
      check('recovery','Recovery path',rec.available?'ready':'attention',rec.available?'At least one local recovery path is available.':'No local recovery snapshot or restore point is currently available.','history'),
      check('performance','Performance diagnostics',input.performanceAvailable?'ready':'attention',input.performanceAvailable?'Large-project performance diagnostics are available.':'Performance diagnostics helper is unavailable.','performance'),
      check('privacy','Security & privacy audit',input.securityAvailable?'ready':'attention',input.securityAvailable?'Security/privacy audit and complete local portability are available.':'Security/privacy audit helper is unavailable.','security'),
      check('version','Release identity',input.versionCurrent?'ready':'attention',input.versionCurrent?`Workspace ${text(input.workspaceVersion,40)} reports consistently.`:`Expected ${text(input.expectedVersion,40)||'current release'} but UI reports ${text(input.workspaceVersion,40)||'unknown'}.`,'start')
    ];
    const attention=checks.filter(c=>c.state!=='ready').map(c=>c.id);
    const limited=checks.some(c=>c.state==='limited');
    return {schema:GATE_SCHEMA,generatedAt:now(),state:limited?'limited':attention.length?'attention':'ready',checks,attention,governance:{hiddenScore:false,automaticTelemetry:false,automaticSubmission:false,automaticRepair:false,automaticProjectMutation:false}};
  }
  function fieldSnapshot(workspaceVersion,gate,diagnostic=null){
    const safeDiagnostic=diagnostic?JSON.parse(JSON.stringify(diagnostic)):null;
    if(safeDiagnostic?.issue)delete safeDiagnostic.issue;
    return {schema:SNAPSHOT_SCHEMA,generatedAt:now(),workspaceVersion:text(workspaceVersion,40),gate,diagnostic:safeDiagnostic,privacy:{automaticTelemetry:false,automaticSubmission:false,projectContentIncluded:false,objectTextIncluded:false,sourceUrlsIncluded:false,deviceIdentifierIncluded:false}};
  }
  function summary(gate){const g=gate||{};const checks=Array.isArray(g.checks)?g.checks:[];return {state:g.state||'limited',ready:checks.filter(c=>c.state==='ready').length,attention:checks.filter(c=>c.state==='attention').length,limited:checks.filter(c=>c.state==='limited').length,total:checks.length,hiddenScore:false};}
  return Object.freeze({SCHEMA,GATE_SCHEMA,SNAPSHOT_SCHEMA,routeHealth,recovery,capability,assess,fieldSnapshot,summary});
});
