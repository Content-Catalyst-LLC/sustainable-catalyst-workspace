(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else { root.SCWorkspaceApiEmbed=api; api.autoRender(); }
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const DURABLE_REF_SCHEMA='sc-workspace-durable-reference/1.0';
  const PROJECTION_SCHEMA='sc-workspace-readonly-projection/1.0';
  const API_SCHEMA='sc-workspace-readonly-api-envelope/1.0';
  const EMBED_SCHEMA='sc-workspace-embed-descriptor/1.0';
  const LEDGER_SCHEMA='sc-workspace-api-embed-ledger/1.0';
  const STORAGE_KEY='sc_workspace_api_embed_v1';
  const ALLOWED_KINDS=new Set(['object','notebook','notebook-block','research-question','research-claim']);
  const text=v=>String(v??'');
  const clean=v=>text(v).replace(/[\u0000-\u001f\u007f]/g,' ').trim();
  const enc=v=>encodeURIComponent(clean(v));
  const dec=v=>{try{return decodeURIComponent(v);}catch(_){return v;}};
  const clone=v=>JSON.parse(JSON.stringify(v));
  function durableReference(entry){
    if(!entry||!ALLOWED_KINDS.has(entry.kind)||!clean(entry.projectId)||!clean(entry.id))return null;
    const uri=`scw://project/${enc(entry.projectId)}/${enc(entry.kind)}/${enc(entry.id)}`;
    return {schema:DURABLE_REF_SCHEMA,uri,projectId:clean(entry.projectId).slice(0,160),kind:entry.kind,id:clean(entry.id).slice(0,160),notebookId:clean(entry.notebookId).slice(0,160),sectionId:clean(entry.sectionId).slice(0,160),authorization:false};
  }
  function parseDurableReference(value){
    const uri=typeof value==='string'?value:text(value&&value.uri);const m=/^scw:\/\/project\/([^/]+)\/([^/]+)\/([^/]+)$/.exec(uri);if(!m)return null;
    const kind=dec(m[2]);if(!ALLOWED_KINDS.has(kind))return null;
    return {schema:DURABLE_REF_SCHEMA,uri,projectId:dec(m[1]),kind,id:dec(m[3]),authorization:false};
  }
  function resolve(entries,reference){const r=parseDurableReference(reference);if(!r)return null;return (Array.isArray(entries)?entries:[]).find(e=>e&&e.projectId===r.projectId&&e.kind===r.kind&&e.id===r.id)||null;}
  function normalizeFields(input={}){return {summary:input.summary!==false,tags:Boolean(input.tags),provenance:Boolean(input.provenance),content:Boolean(input.content)};}
  function projectionData(entry,fields){
    const data={title:clean(entry.title).slice(0,500),projectTitle:clean(entry.projectTitle).slice(0,240),kind:entry.kind,subtype:clean(entry.subtype).slice(0,160),origin:clean(entry.origin).slice(0,240),updatedAt:clean(entry.updatedAt).slice(0,80)};
    if(fields.summary)data.summary=clean(entry.summary).slice(0,4000);
    if(fields.tags)data.tags=(Array.isArray(entry.tags)?entry.tags:[]).map(clean).filter(Boolean).slice(0,50);
    if(fields.provenance){const p=entry.provenance&&typeof entry.provenance==='object'?entry.provenance:{};data.provenance={sourceTitle:clean(p.sourceTitle).slice(0,500),sourceUrl:clean(p.sourceUrl).slice(0,2000),bibliography:p.bibliography&&typeof p.bibliography==='object'?clone(p.bibliography):{}};}
    if(fields.content)data.content=clean(entry.content).slice(0,50000);
    return data;
  }
  function createProjection(entry,options={},now=()=>new Date().toISOString(),id=()=>`projection-${Date.now()}`){
    const ref=durableReference(entry);if(!ref)return null;const fields=normalizeFields(options.fields||{});
    return {schema:PROJECTION_SCHEMA,id:clean(id()).slice(0,180),createdAt:now(),exposure:'public-readonly',durableRef:ref,fields,data:projectionData(entry,fields),sourceRevision:clean(entry.updatedAt).slice(0,80),fingerprint:'',governance:{explicitDisclosure:true,readOnly:true,canonicalSourceUnchanged:true,durableReferenceIsAuthorization:false,liveServerRead:false,automaticPublication:false,automaticRefresh:false}};
  }
  function stable(value){if(Array.isArray(value))return value.map(stable);if(value&&typeof value==='object'){const out={};Object.keys(value).sort().forEach(k=>out[k]=stable(value[k]));return out;}return value;}
  function fingerprintPayload(p){const x=clone(p);delete x.fingerprint;return JSON.stringify(stable(x));}
  function withFingerprint(p,fingerprint){const out=clone(p);out.fingerprint=clean(fingerprint).slice(0,160);return out;}
  function validateProjection(p){const errors=[];if(!p||p.schema!==PROJECTION_SCHEMA)errors.push('schema');if(!parseDurableReference(p&&p.durableRef))errors.push('durable-ref');if(p&&p.exposure!=='public-readonly')errors.push('exposure');if(!p||!p.data||!clean(p.data.title))errors.push('title');if(!p||!p.governance||p.governance.readOnly!==true||p.governance.durableReferenceIsAuthorization!==false)errors.push('governance');return {ok:errors.length===0,errors};}
  function apiEnvelope(projection,workspaceVersion=''){if(!validateProjection(projection).ok)return null;return {schema:API_SCHEMA,workspaceVersion:clean(workspaceVersion),readOnly:true,generatedAt:new Date().toISOString(),reference:clone(projection.durableRef),projection:clone(projection),links:{self:''},governance:{staticProjection:true,serverDataEndpoint:false,authenticationByReference:false,canonicalMutation:false}};}
  function embedDescriptor(projection,workspaceVersion='',rendererUrl=''){const env=apiEnvelope(projection,workspaceVersion);if(!env)return null;return {schema:EMBED_SCHEMA,renderer:'sc-workspace-api-embed-v1',rendererUrl:clean(rendererUrl).slice(0,2000),payload:env,fingerprint:clean(projection.fingerprint),governance:{readOnly:true,staticPayload:true,noLiveDataFetch:true,identifierIsNotAuthorization:true}};}
  function normalizeLedger(raw={}){const list=Array.isArray(raw.projections)?raw.projections:[];return {schema:LEDGER_SCHEMA,projections:list.filter(p=>validateProjection(p).ok).slice(0,200),updatedAt:clean(raw.updatedAt)};}
  function upsert(ledger,projection){const l=normalizeLedger(ledger),p=clone(projection);l.projections=[p,...l.projections.filter(x=>x.id!==p.id)].slice(0,200);l.updatedAt=new Date().toISOString();return l;}
  function remove(ledger,id){const l=normalizeLedger(ledger);l.projections=l.projections.filter(p=>p.id!==id);l.updatedAt=new Date().toISOString();return l;}
  function escJsonForHtml(v){return JSON.stringify(v).replace(/</g,'\\u003c').replace(/-->/g,'--\\u003e');}
  function embedHtml(descriptor,rendererUrl){if(!descriptor)return'';const url=clean(rendererUrl||descriptor.rendererUrl);return `<div class="sc-workspace-embed" data-sc-workspace-embed><script type="application/json" data-sc-workspace-embed-data>${escJsonForHtml(descriptor)}</script></div>${url?`<script src="${url.replace(/&/g,'&amp;').replace(/"/g,'&quot;')}"></script>`:''}`;}
  function renderElement(host,descriptor){
    if(!host||!descriptor||descriptor.schema!==EMBED_SCHEMA||descriptor.governance?.readOnly!==true)return false;const p=descriptor.payload?.projection;if(!validateProjection(p).ok)return false;host.textContent='';
    const card=document.createElement('article');card.setAttribute('aria-label',p.data.title);card.style.cssText='box-sizing:border-box;border:1px solid #d9d9d9;border-top:4px solid #000;background:#fff;color:#111;padding:20px;font-family:Montserrat,Arial,sans-serif;line-height:1.55;max-width:760px';
    const meta=document.createElement('div');meta.textContent=[p.data.kind,p.data.projectTitle].filter(Boolean).join(' · ');meta.style.cssText='font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#666;margin-bottom:8px';card.appendChild(meta);
    const h=document.createElement('h3');h.textContent=p.data.title;h.style.cssText='font-size:24px;line-height:1.15;margin:0 0 10px;color:#000';card.appendChild(h);
    if(p.data.summary){const s=document.createElement('p');s.textContent=p.data.summary;s.style.cssText='margin:0 0 12px;color:#444';card.appendChild(s);}
    if(p.data.content){const c=document.createElement('div');c.textContent=p.data.content;c.style.cssText='white-space:pre-wrap;margin-top:14px;padding-top:14px;border-top:1px solid #e5e5e5;color:#222';card.appendChild(c);}
    if(Array.isArray(p.data.tags)&&p.data.tags.length){const t=document.createElement('div');t.textContent=p.data.tags.join(' · ');t.style.cssText='margin-top:12px;font-size:12px;color:#666';card.appendChild(t);}
    const f=document.createElement('div');f.textContent=p.durableRef.uri;f.style.cssText='margin-top:14px;padding-top:10px;border-top:1px solid #eee;font-size:10px;color:#777;overflow-wrap:anywhere';card.appendChild(f);host.appendChild(card);return true;
  }
  function autoRender(){if(typeof document==='undefined')return;const run=()=>document.querySelectorAll('[data-sc-workspace-embed]').forEach(host=>{if(host.dataset.scwRendered==='1')return;const node=host.querySelector('[data-sc-workspace-embed-data]');if(!node)return;try{const d=JSON.parse(node.textContent||'{}');if(renderElement(host,d))host.dataset.scwRendered='1';}catch(_){}});if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();}
  return {DURABLE_REF_SCHEMA,PROJECTION_SCHEMA,API_SCHEMA,EMBED_SCHEMA,LEDGER_SCHEMA,STORAGE_KEY,ALLOWED_KINDS,durableReference,parseDurableReference,resolve,normalizeFields,createProjection,fingerprintPayload,withFingerprint,validateProjection,apiEnvelope,embedDescriptor,normalizeLedger,upsert,remove,embedHtml,renderElement,autoRender};
});
