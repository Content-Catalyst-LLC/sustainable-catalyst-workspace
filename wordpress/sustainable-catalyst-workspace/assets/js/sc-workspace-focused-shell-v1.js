(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceFocusedShell=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-focused-shell/1.0';
  const STORAGE_KEY='sc_workspace_research_surface_v0591';
  const SURFACES=['overview','search','collections','cross-project','tasks','assistant','citations','composition'];
  const LABELS={overview:'Overview',search:'Search',collections:'Collections','cross-project':'Cross-project',tasks:'Tasks',assistant:'Assistant',citations:'Citations',composition:'Composition'};
  function normalizeSurface(value){return SURFACES.includes(String(value||''))?String(value):'overview';}
  function readSurface(storage){try{return normalizeSurface(storage&&storage.getItem(STORAGE_KEY));}catch(_){return 'overview';}}
  function writeSurface(storage,surface){try{if(storage)storage.setItem(STORAGE_KEY,normalizeSurface(surface));}catch(_){} return normalizeSurface(surface);}
  function visibilityPlan(surface,panels){const active=normalizeSurface(surface);return (panels||[]).map(panel=>({surface:String(panel.surface||''),hidden:String(panel.surface||'')!==active}));}
  function init(workspaceRoot){
    const root=workspaceRoot||document.querySelector('[data-sc-workspace]');
    if(!root||root.dataset.scwFocusedShellReady==='1')return null;
    root.dataset.scwFocusedShellReady='1';
    const research=root.querySelector('[data-scw-workspace-section="research"]');
    if(!research)return null;
    const nav=research.querySelector('[data-scw-research-tool-nav]');
    const buttons=[...research.querySelectorAll('[data-scw-research-surface]')];
    const jumps=[...research.querySelectorAll('[data-scw-research-surface-jump]')];
    const panels=[...research.querySelectorAll('[data-scw-research-surface-panel]')];
    let active='overview';
    function apply(surface,focus){
      active=normalizeSurface(surface);
      root.dataset.scwResearchSurface=active;
      buttons.forEach(button=>{
        const selected=button.dataset.scwResearchSurface===active;
        button.classList.toggle('is-active',selected);
        button.setAttribute('aria-pressed',selected?'true':'false');
        if(selected)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');
      });
      panels.forEach(panel=>{panel.hidden=panel.dataset.scwResearchSurfacePanel!==active;});
      writeSurface(window.sessionStorage,active);
      if(focus){
        const panel=panels.find(item=>!item.hidden);
        const heading=panel&&panel.querySelector('h3,h4');
        if(heading){if(!heading.hasAttribute('tabindex'))heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true});heading.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});}
        else if(nav)nav.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
      }
      return active;
    }
    buttons.forEach(button=>button.addEventListener('click',()=>apply(button.dataset.scwResearchSurface,true)));
    jumps.forEach(button=>button.addEventListener('click',()=>apply(button.dataset.scwResearchSurfaceJump,true)));
    root.querySelectorAll('[data-scw-research-route="research"]').forEach(button=>button.addEventListener('click',()=>apply('overview',false)));
    root.querySelectorAll('[data-scw-workspace-view="research"]').forEach(button=>button.addEventListener('click',()=>apply(active,false)));
    if(nav)nav.addEventListener('keydown',event=>{
      if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
      const current=Math.max(0,buttons.indexOf(document.activeElement));let next=current;
      if(event.key==='ArrowRight')next=(current+1)%buttons.length;
      if(event.key==='ArrowLeft')next=(current-1+buttons.length)%buttons.length;
      if(event.key==='Home')next=0;if(event.key==='End')next=buttons.length-1;
      event.preventDefault();buttons[next].focus();
    });
    active=readSurface(window.sessionStorage);
    apply(active,false);
    return {schema:SCHEMA,get active(){return active;},setSurface:apply};
  }
  if(typeof document!=='undefined'){
    const boot=()=>document.querySelectorAll('[data-sc-workspace]').forEach(init);
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
  }
  return {SCHEMA,STORAGE_KEY,SURFACES,LABELS,normalizeSurface,readSurface,writeSurface,visibilityPlan,init};
});
