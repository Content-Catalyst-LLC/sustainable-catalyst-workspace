(function(root){'use strict';
const VERSION='3.82.3';
const CONTEXT_SCHEMA='sc-shared-research-surface-context/1.0';
const q=(s,r=document)=>r.querySelector(s);
const clean=(v,max=240)=>String(v==null?'':v).replace(/[\u0000-\u001f]/g,'').trim().slice(0,max);
function contextFromLocation(loc){
  const u=loc instanceof URL?loc:new URL(String(loc||location.href),location.href),p=u.searchParams;
  if(p.get('sc_context')!=='1'&&!p.get('sc_object')&&!p.get('sc_source'))return null;
  return {schema:CONTEXT_SCHEMA,source:clean(p.get('sc_source')||'public'),objectId:clean(p.get('sc_object')||''),kind:clean(p.get('sc_kind')||''),view:clean(p.get('sc_view')||'terrain'),lens:clean(p.get('sc_lens')||'all'),returnUrl:clean(p.get('sc_return')||'',1000)};
}
function contextForNode(node,source='wordpress',extra={}){
  return {schema:CONTEXT_SCHEMA,source:clean(source),objectId:clean(node?.id||''),kind:clean(node?.group||node?.kind||''),view:clean(extra.view||'terrain'),lens:clean(extra.lens||'all'),returnUrl:clean(extra.returnUrl||'',1000)};
}
function workspaceUrl(base,ctx){
  const u=new URL(String(base||'https://workspace.sustainablecatalyst.com'),location.href),c=ctx||{};
  u.searchParams.set('sc_context','1');u.searchParams.set('sc_source',clean(c.source||'public'));
  if(c.objectId)u.searchParams.set('sc_object',clean(c.objectId));
  if(c.kind)u.searchParams.set('sc_kind',clean(c.kind));
  u.searchParams.set('sc_view',clean(c.view||'terrain'));u.searchParams.set('sc_lens',clean(c.lens||'all'));
  if(c.returnUrl)u.searchParams.set('sc_return',clean(c.returnUrl,1000));
  u.hash='research-map';return u.toString();
}
async function fetchGraph(url){
  const r=await fetch(url,{credentials:'same-origin',headers:{Accept:'application/json'},cache:'no-store'});
  if(!r.ok)throw new Error('graph '+r.status);return r.json();
}
async function mountPublic(container,opts={}){
  if(!container)return null;
  const runtime=root.SCSharedResearchGraphRuntime;
  if(!runtime||typeof runtime.create!=='function')throw new Error('Shared research graph runtime unavailable');
  container.innerHTML='<div class="sc-surface-head"><div><span>PUBLIC RESEARCH SURFACE</span><strong>Scientific Knowledge Terrain</strong></div><a class="sc-surface-open" target="_blank" rel="noopener">Open in Workspace →</a></div><div class="sc-surface-mount"></div><div class="sc-surface-boundary">Read-only public surface · project authority remains in Workspace · private project data is never requested.</div>';
  const mount=q('.sc-surface-mount',container),open=q('.sc-surface-open',container);
  let graph;
  try{graph=await fetchGraph(opts.graphUrl)}catch(e){container.dataset.surfaceState='unavailable';q('.sc-surface-boundary',container).textContent='Public research surface temporarily unavailable.';return null}
  const view=runtime.create(),baseCtx={source:opts.source||'wordpress',view:'terrain',lens:graph.lens||'all',returnUrl:opts.returnUrl||location.href};
  open.href=workspaceUrl(opts.workspaceUrl,baseCtx);
  mount.addEventListener('sc:research-object-selected',e=>{const node=e.detail&&e.detail.node;if(!node)return;open.href=workspaceUrl(opts.workspaceUrl,contextForNode(node,baseCtx.source,{view:'terrain',lens:graph.lens||'all',returnUrl:baseCtx.returnUrl}));open.textContent='Open '+String(node.label||node.id).slice(0,42)+' in Workspace →';});
  view.render(mount,graph,{onLens:opts.onLens||(()=>{})});
  container.dataset.surfaceState='ready';return {graph,view};
}
function installStandalone(){
  const app=q('[data-sc-workspace-standalone]');if(!app)return null;
  const ctx=contextFromLocation(location.href);
  if(!ctx)return null;
  let bar=q('[data-sc-surface-context]',app);
  if(!bar){bar=document.createElement('div');bar.className='sc-surface-context';bar.dataset.scSurfaceContext='1';app.insertBefore(bar,app.firstChild);}
  bar.innerHTML='<div><span>SHARED RESEARCH CONTEXT</span><strong></strong><small></small></div><div><button type="button" data-sc-context-graph>Open research map</button><a data-sc-context-return hidden>Return</a></div>';
  q('strong',bar).textContent=ctx.objectId?('Object '+ctx.objectId):'Public research context';
  q('small',bar).textContent=[ctx.source,ctx.kind,ctx.view,ctx.lens].filter(Boolean).join(' · ');
  q('[data-sc-context-graph]',bar).onclick=()=>q('#research-map')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  const back=q('[data-sc-context-return]',bar);if(ctx.returnUrl){back.hidden=false;back.href=ctx.returnUrl;back.textContent='Return to source';}
  app.dataset.sharedResearchContext=ctx.objectId||ctx.source;
  return ctx;
}
root.SCSharedResearchSurface=Object.freeze({version:VERSION,contextSchema:CONTEXT_SCHEMA,contextFromLocation,contextForNode,workspaceUrl,mountPublic,installStandalone});
})(globalThis);