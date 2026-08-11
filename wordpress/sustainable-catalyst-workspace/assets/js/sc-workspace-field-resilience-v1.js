(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceFieldResilience=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-field-resilience/1.0';
  const ROUTE_SCHEMA='sc-workspace-route-state/1.0';
  const SNAPSHOT_SCHEMA='sc-workspace-resilience-snapshot/1.0';
  const STORAGE_KEY='sc_workspace_route_state_v0610';
  const LEGACY_RESEARCH_KEY='sc_workspace_research_surface_v0591';
  const MAX_AGE_MS=1000*60*60*24*30;
  const RESEARCH_SURFACES=['overview','search','collections','cross-project','tasks','assistant','citations','composition'];
  const text=(v,max=240)=>String(v==null?'':v).trim().slice(0,max);
  const now=()=>new Date().toISOString();
  function routeSet(workspaceRoot){
    const root=workspaceRoot;
    const fromButtons=root&&root.querySelectorAll?[...root.querySelectorAll('[data-scw-workspace-view]')].map(b=>text(b.dataset.scwWorkspaceView,80)).filter(Boolean):[];
    const fromSections=root&&root.querySelectorAll?[...root.querySelectorAll('[data-scw-workspace-section]')].map(s=>text(s.dataset.scwWorkspaceSection,80)).filter(Boolean):[];
    return [...new Set([...fromButtons,...fromSections,'start'])];
  }
  function normalizeResearchSurface(value){return RESEARCH_SURFACES.includes(String(value||''))?String(value):'overview';}
  function sanitizeRouteState(raw,allowedRoutes,currentVersion){
    const routes=Array.isArray(allowedRoutes)?allowedRoutes:[];
    const source=raw&&typeof raw==='object'?raw:{};
    const requested=text(source.view,80);
    const valid=routes.includes(requested);
    const researchSurface=normalizeResearchSurface(source.researchSurface);
    const at=Date.parse(String(source.at||''));
    const stale=Number.isFinite(at)?Date.now()-at>MAX_AGE_MS:false;
    const versionMismatch=Boolean(source.version&&currentVersion&&String(source.version)!==String(currentVersion));
    return {
      schema:ROUTE_SCHEMA,
      view:valid&&!stale?requested:'start',
      researchSurface:valid&&!stale&&requested==='research'?researchSurface:'overview',
      version:text(currentVersion||source.version,40),
      at:now(),
      sanitized:!valid||stale||versionMismatch||source.schema!==ROUTE_SCHEMA,
      reason:!valid?'invalid-route':stale?'expired-route-state':versionMismatch?'release-changed':source.schema!==ROUTE_SCHEMA?'legacy-route-state':'current'
    };
  }
  function readRouteState(storage,allowedRoutes,currentVersion){
    try{
      const raw=JSON.parse(storage&&storage.getItem(STORAGE_KEY)||'null');
      return sanitizeRouteState(raw,allowedRoutes,currentVersion);
    }catch(_){return sanitizeRouteState({},allowedRoutes,currentVersion);}
  }
  function writeRouteState(storage,input,allowedRoutes,currentVersion){
    const next=sanitizeRouteState({...input,schema:ROUTE_SCHEMA,version:currentVersion,at:now()},allowedRoutes,currentVersion);
    next.sanitized=false;next.reason='current';
    try{if(storage)storage.setItem(STORAGE_KEY,JSON.stringify(next));}catch(_){}
    return next;
  }
  function clearUiState(sessionStorage){
    const removed=[];
    [STORAGE_KEY,LEGACY_RESEARCH_KEY].forEach(key=>{try{if(sessionStorage&&sessionStorage.getItem(key)!==null){sessionStorage.removeItem(key);removed.push(key);}}catch(_){}});
    return {removed,canonicalDataTouched:false};
  }
  function capabilities(env=globalThis){
    const win=env.window||env;let local=false,session=false;
    try{const k='__scw_resilience_local__';win.localStorage.setItem(k,'1');local=win.localStorage.getItem(k)==='1';win.localStorage.removeItem(k);}catch(_){}
    try{const k='__scw_resilience_session__';win.sessionStorage.setItem(k,'1');session=win.sessionStorage.getItem(k)==='1';win.sessionStorage.removeItem(k);}catch(_){}
    return {
      localStorage:local,
      sessionStorage:session,
      historyApi:Boolean(win.history&&typeof win.history.pushState==='function'&&typeof win.history.replaceState==='function'),
      fileApi:Boolean(win.File&&win.FileReader&&win.Blob),
      webCryptoSha256:Boolean((env.crypto||win.crypto)?.subtle?.digest),
      online:typeof win.navigator?.onLine==='boolean'?win.navigator.onLine:null
    };
  }
  function recoveryState(env=globalThis){
    const win=env.window||env;let current='missing',lastKnownGood=false,quarantine=false,restorePoints=0;
    try{const raw=win.localStorage?.getItem('sc_workspace');if(raw){const parsed=JSON.parse(raw);current=parsed&&Array.isArray(parsed.projects)?'readable':'invalid';}}catch(_){current='invalid';}
    try{const e=JSON.parse(win.localStorage?.getItem('sc_workspace_last_good_v1')||'null');lastKnownGood=Boolean(e&&typeof e.raw==='string'&&e.raw.length);}catch(_){}
    try{quarantine=Boolean(win.localStorage?.getItem('sc_workspace_recovery_v0_8_2'));}catch(_){}
    try{const s=JSON.parse(win.localStorage?.getItem('sc_workspace')||'null');restorePoints=Array.isArray(s?.versionHistory?.restorePoints)?s.versionHistory.restorePoints.length:0;}catch(_){}
    const available=lastKnownGood||quarantine||restorePoints>0;
    const state=current==='invalid'?(available?'recoverable':'attention'):current==='readable'?'healthy':available?'recoverable':'empty';
    return {state,current,lastKnownGood,quarantine,restorePoints,available};
  }
  function assess({caps={},recovery={},routeState={},visibleSections=0}={}){
    const findings=[];
    const add=(id,state,label,detail,action)=>findings.push({id,state,label,detail,action});
    add('local-storage',caps.localStorage?'ready':'attention','Local persistence',caps.localStorage?'Browser-local storage is writable.':'Local storage is unavailable; changes may be temporary.','Open Security & Privacy');
    add('session-storage',caps.sessionStorage?'ready':'limited','Session navigation memory',caps.sessionStorage?'Safe UI position can be remembered for this tab.':'Session storage is unavailable; Workspace will fall back to Start after reload.','Reset navigation state');
    add('history',caps.historyApi?'ready':'limited','Back / forward navigation',caps.historyApi?'Workspace route changes can participate in browser history.':'History API is unavailable; in-app navigation still works.','None required');
    add('recovery',recovery.state==='healthy'||recovery.state==='recoverable'?'ready':recovery.state==='empty'?'limited':'attention','Recovery state',recovery.state==='healthy'?'Current Workspace state is readable.':recovery.state==='recoverable'?'A local recovery path is available.':recovery.state==='empty'?'No project state or recovery snapshot exists yet.':'Saved project state is unreadable and no recovery path was detected.','Open History / Recovery');
    add('route-state',routeState.sanitized?'limited':'ready','Saved UI position',routeState.sanitized?`Saved UI state was sanitized (${routeState.reason}).`:'Saved UI state is current and valid.','Reset navigation state');
    add('route-isolation',visibleSections<=1?'ready':'attention','Route isolation',visibleSections<=1?'Only one Workspace route is visible.':`${visibleSections} Workspace routes appear visible simultaneously.`,'Open Beta Readiness');
    const attention=findings.filter(f=>f.state==='attention').length,limited=findings.filter(f=>f.state==='limited').length;
    return {schema:SCHEMA,generatedAt:now(),state:attention?'attention':limited?'limited':'ready',findings,governance:{canonicalMutation:false,automaticRepair:false,automaticDeletion:false,automaticUpload:false,telemetry:false}};
  }
  function snapshot(workspaceVersion,assessment,caps,recovery,routeState){
    return {schema:SNAPSHOT_SCHEMA,generatedAt:now(),workspaceVersion:text(workspaceVersion,40),assessment,caps,recovery,routeState:{view:routeState.view,researchSurface:routeState.researchSurface,sanitized:routeState.sanitized,reason:routeState.reason},privacy:{projectContentIncluded:false,objectContentIncluded:false,sourceUrlsIncluded:false,deviceIdentifierIncluded:false,automaticTelemetry:false,automaticSubmission:false}};
  }
  return Object.freeze({SCHEMA,ROUTE_SCHEMA,SNAPSHOT_SCHEMA,STORAGE_KEY,LEGACY_RESEARCH_KEY,RESEARCH_SURFACES,routeSet,normalizeResearchSurface,sanitizeRouteState,readRouteState,writeRouteState,clearUiState,capabilities,recoveryState,assess,snapshot});
});
