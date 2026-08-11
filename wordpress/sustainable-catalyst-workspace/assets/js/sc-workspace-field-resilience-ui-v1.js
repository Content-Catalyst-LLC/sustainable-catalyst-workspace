(function(){
  'use strict';
  const helper=globalThis.SCWorkspaceFieldResilience;if(!helper)return;
  function boot(root){
    if(!root||root.dataset.scwFieldResilienceReady==='1')return;root.dataset.scwFieldResilienceReady='1';
    const version=String(root.dataset.version||'');const routes=helper.routeSet(root);let suppressHistory=false;
    const section=root.querySelector('[data-scw-field-resilience]');
    const badge=root.querySelector('[data-scw-resilience-badge]'),findings=root.querySelector('[data-scw-resilience-findings]'),status=root.querySelector('[data-scw-resilience-status]');
    const runButton=root.querySelector('[data-scw-resilience-run]'),resetButton=root.querySelector('[data-scw-resilience-reset]'),exportButton=root.querySelector('[data-scw-resilience-export]');
    let restored=helper.readRouteState(window.sessionStorage,routes,version),latest=null;
    function visibleSections(){return [...root.querySelectorAll('[data-scw-workspace-section]')].filter(el=>!el.hidden&&getComputedStyle(el).display!=='none').length;}
    function currentRoute(){const active=root.querySelector('[data-scw-workspace-view].is-active');return active?.dataset.scwWorkspaceView||'start';}
    function researchSurface(){return helper.normalizeResearchSurface(root.dataset.scwResearchSurface||'overview');}
    function remember(view,researchSurfaceValue,historyMode='push'){
      const next=helper.writeRouteState(window.sessionStorage,{view,researchSurface:researchSurfaceValue},routes,version);
      if(!suppressHistory&&helper.capabilities(window).historyApi){
        const state={...(window.history.state||{}),scWorkspace:{view:next.view,researchSurface:next.researchSurface}};
        const compat=globalThis.SCWorkspaceBrowserCompatibility;
        if(compat?.safeHistory)compat.safeHistory(window,historyMode,state);
        else try{historyMode==='replace'?window.history.replaceState(state,''):window.history.pushState(state,'');}catch(_){}
      }
      return next;
    }
    function navigate(view,surface,fromHistory=false){
      const safe=helper.sanitizeRouteState({schema:helper.ROUTE_SCHEMA,view,researchSurface:surface,version,at:new Date().toISOString()},routes,version);
      const button=root.querySelector(`[data-scw-workspace-view="${safe.view}"]`);
      suppressHistory=fromHistory;
      if(button)button.click();
      if(safe.view==='research'){
        const sb=root.querySelector(`[data-scw-research-surface="${safe.researchSurface}"]`);if(sb)sb.click();
      }
      if(fromHistory)window.setTimeout(()=>{suppressHistory=false;},0);else suppressHistory=false;
      helper.writeRouteState(window.sessionStorage,safe,routes,version);
      return safe;
    }
    root.querySelectorAll('[data-scw-workspace-view]').forEach(button=>button.addEventListener('click',()=>{
      const view=String(button.dataset.scwWorkspaceView||'start');window.setTimeout(()=>remember(view,view==='research'?researchSurface():'overview'),0);
    }));
    root.querySelectorAll('[data-scw-research-surface]').forEach(button=>button.addEventListener('click',()=>window.setTimeout(()=>{
      if(currentRoute()==='research')remember('research',button.dataset.scwResearchSurface);
    },0)));
    window.addEventListener('popstate',event=>{const state=event.state?.scWorkspace;if(state)navigate(state.view,state.researchSurface,true);});
    function run(){
      const caps=helper.capabilities(window),recovery=helper.recoveryState(window),routeState=helper.readRouteState(window.sessionStorage,routes,version);
      latest=helper.assess({caps,recovery,routeState,visibleSections:visibleSections()});
      if(badge)badge.textContent=latest.state.toUpperCase();
      if(findings){findings.innerHTML='';latest.findings.forEach(item=>{const row=document.createElement('article');row.className=`scw-resilience-finding is-${item.state}`;row.innerHTML=`<span>${item.state.toUpperCase()}</span><div><strong>${item.label}</strong><p>${item.detail}</p><small>${item.action}</small></div>`;findings.appendChild(row);});}
      if(status)status.textContent=`Reliability check: ${latest.findings.filter(f=>f.state==='ready').length}/${latest.findings.length} ready. Checks are local and advisory.`;
      return {caps,recovery,routeState,assessment:latest};
    }
    runButton?.addEventListener('click',run);
    resetButton?.addEventListener('click',()=>{const out=helper.clearUiState(window.sessionStorage);restored=helper.writeRouteState(window.sessionStorage,{view:'start',researchSurface:'overview'},routes,version);if(status)status.textContent=`Navigation state reset (${out.removed.length} UI key${out.removed.length===1?'':'s'} removed). Projects and research were not touched.`;navigate('start','overview',false);});
    exportButton?.addEventListener('click',()=>{const result=run(),payload=helper.snapshot(version,result.assessment,result.caps,result.recovery,result.routeState),compat=globalThis.SCWorkspaceBrowserCompatibility;if(compat?.downloadJson)compat.downloadJson(`workspace-v${version}-resilience-snapshot.json`,payload,window);else{const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`workspace-v${version}-resilience-snapshot.json`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}});
    window.setTimeout(()=>{
      if(restored.view!=='start'||restored.researchSurface!=='overview')navigate(restored.view,restored.researchSurface,true);
      else remember(currentRoute(),currentRoute()==='research'?researchSurface():'overview','replace');
      run();
    },0);
    if(section)section.dataset.scwResilienceInitialized='1';
  }
  const start=()=>document.querySelectorAll('[data-sc-workspace]').forEach(boot);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
