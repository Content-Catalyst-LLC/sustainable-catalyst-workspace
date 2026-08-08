(() => {
  'use strict';
  const OUTBOUND_KEY='sc_workspace_handoff_v2';
  const RETURN_KEY='sc_workspace_handoff_return_v1';
  const ADAPTER_SCHEMA='sc-workspace-return-adapter/1.0';
  const DESTINATIONS=new Set(['research-librarian','knowledge-library','site-intelligence','workbench','analytics-r','decision-studio','catalyst-canvas','catalyst-data','lab']);
  function nowIso(){return new Date().toISOString();}
  function uid(){if(window.crypto&&typeof window.crypto.randomUUID==='function')return `scr-${window.crypto.randomUUID()}`;return `scr-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,10)}`;}
  function context(){try{const raw=JSON.parse(window.sessionStorage.getItem(OUTBOUND_KEY)||'null');return raw&&raw.schema==='sc-workspace-handoff/2.0'?raw:null;}catch(_){return null;}}
  function artifacts(input){const list=Array.isArray(input)?input:[];return list.slice(0,20).map((item)=>({type:String(item&&item.type||'document'),title:String(item&&item.title||'Returned artifact').slice(0,160),summary:String(item&&item.summary||'').slice(0,1200),content:String(item&&item.content||'').slice(0,50000),tags:Array.isArray(item&&item.tags)?item.tags.slice(0,20):[],status:String(item&&item.status||'ready'),sourceTitle:String(item&&item.sourceTitle||'').slice(0,240),sourceUrl:String(item&&item.sourceUrl||'').slice(0,2000)}));}
  function build(options={}){const ctx=context();if(!ctx)throw new Error('No Workspace handoff context is available in this browser session.');const destination=String(options.destination||ctx.destination||'');if(!DESTINATIONS.has(destination))throw new Error('Unsupported Workspace return destination.');return{schema:ADAPTER_SCHEMA,returnId:String(options.returnId||uid()).slice(0,160),handoffId:ctx.handoffId,projectId:ctx.projectId,destination,destinationLabel:String(options.destinationLabel||destination).slice(0,120),intent:String(options.intent||ctx.intent||'general'),returnedAt:nowIso(),artifacts:artifacts(options.artifacts)};}
  function submit(options={}){const packet=build(options);window.sessionStorage.setItem(RETURN_KEY,JSON.stringify(packet));try{if(window.opener&&!window.opener.closed)window.opener.postMessage({type:'sc-workspace-return',payload:packet},window.location.origin);}catch(_){}const ctx=context();if(options.redirect!==false&&ctx&&ctx.returnUrl){window.location.assign(ctx.returnUrl);}return packet;}
  window.SCWorkspaceToolReturnAdapter={schema:ADAPTER_SCHEMA,outboundStorageKey:OUTBOUND_KEY,returnStorageKey:RETURN_KEY,context,build,submit};
})();
