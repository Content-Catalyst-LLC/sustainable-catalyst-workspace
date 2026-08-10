(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceGroundedResearchAssistant=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-grounded-research-assistant/1.0';
  const REQUEST_SCHEMA='sc-workspace-grounded-research-request/1.0';
  const RESPONSE_SCHEMA='sc-workspace-grounded-research-response/1.0';
  const REQUEST_EXPORT_SCHEMA='sc-workspace-grounded-research-request-export/1.0';
  const RESPONSE_EXPORT_SCHEMA='sc-workspace-grounded-research-response-export/1.0';
  const LIBRARY_SCHEMA='sc-workspace-grounded-research-assistant-library/1.0';
  const STORAGE_KEY='sc_workspace_grounded_research_assistant_v1';
  const MAX_SESSIONS=80,MAX_SCOPE=64,MAX_QUESTION=6000,MAX_RESPONSE=40000,MAX_EXCERPT=6000;
  const TASKS=new Set(['grounded-summary','evidence-gaps','compare-alternatives','briefing-draft','method-explanation','general-question']);
  const STATUS=new Set(['prepared','response-draft','reviewed','rejected','materialized']);
  const SOURCES=new Set(['manual','research-librarian','adapter','external']);
  const text=v=>String(v==null?'':v), list=v=>Array.isArray(v)?v:[];
  function clean(v,n=240){return text(v).trim().slice(0,n);}
  function fnv1a(value){let h=0x811c9dc5;const s=text(value);for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}return h.toString(16).padStart(8,'0');}
  function canonicalGrounding(entry,number){
    const p=entry&&entry.provenance&&typeof entry.provenance==='object'?entry.provenance:{};
    const excerpt=clean(entry?.content||entry?.summary,MAX_EXCERPT);
    const g={number:Number(number)||1,key:clean(entry?.key,420),kind:clean(entry?.kind,80),subtype:clean(entry?.subtype,80),projectId:clean(entry?.projectId,160),projectTitle:clean(entry?.projectTitle,240),id:clean(entry?.id,160),title:clean(entry?.title,320)||'Untitled research record',origin:clean(entry?.origin,160),updatedAt:clean(entry?.updatedAt,80),ref:entry?.ref&&typeof entry.ref==='object'?JSON.parse(JSON.stringify(entry.ref)):null,excerpt,provenance:{sourceTitle:clean(p.sourceTitle||p.capture?.sourceTitle||p.bibliography?.title,500),sourceUrl:clean(p.sourceUrl||p.capture?.sourceUrl||p.bibliography?.url,2000),bibliography:p.bibliography&&typeof p.bibliography==='object'?JSON.parse(JSON.stringify(p.bibliography)):{} }};
    g.fingerprint=fnv1a(JSON.stringify([g.key,g.projectId,g.id,g.updatedAt,g.excerpt,g.provenance]));
    return g;
  }
  function prepareRequest(raw,entries,idFn,nowFn){
    const r=raw&&typeof raw==='object'?raw:{};const keys=[...new Set(list(r.selectedKeys).map(x=>text(x)).filter(Boolean))].slice(0,MAX_SCOPE);const map=new Map(list(entries).map(e=>[text(e.key),e]));const grounding=keys.map(k=>map.get(k)).filter(Boolean).map((e,i)=>canonicalGrounding(e,i+1));
    const stamp=typeof nowFn==='function'?nowFn():new Date().toISOString();
    return {schema:REQUEST_SCHEMA,id:typeof idFn==='function'?idFn('gra'):clean(r.id,160)||`gra-${Date.now()}`,title:clean(r.title,240)||'Grounded research question',task:TASKS.has(text(r.task))?text(r.task):'general-question',question:clean(r.question,MAX_QUESTION),status:'prepared',grounding,groundingFingerprint:fnv1a(JSON.stringify(grounding.map(g=>g.fingerprint))),response:'',responseSource:'manual',citations:[],citationCoverage:{valid:false,markers:[],invalidMarkers:[],uncitedSegments:[]},reviewedAt:null,materializedDocumentId:'',createdAt:stamp,updatedAt:stamp};
  }
  function markers(value){return [...text(value).matchAll(/\[(\d{1,3})\]/g)].map(m=>Number(m[1]));}
  function citationCoverage(request,response){
    const validNums=new Set(list(request?.grounding).map(g=>Number(g.number)));const seen=markers(response);const invalid=[...new Set(seen.filter(n=>!validNums.has(n)))];
    const segments=text(response).split(/\n\s*\n/).map(s=>s.trim()).filter(Boolean);const uncited=segments.filter(seg=>{if(seg.length<24||/^#{1,6}\s/.test(seg))return false;return !markers(seg).some(n=>validNums.has(n));}).slice(0,50);
    const citations=[...new Set(seen.filter(n=>validNums.has(n)))].sort((a,b)=>a-b).map(n=>request.grounding.find(g=>Number(g.number)===n)).filter(Boolean).map(g=>({number:g.number,key:g.key,title:g.title,projectTitle:g.projectTitle,origin:g.origin,fingerprint:g.fingerprint}));
    return {valid:Boolean(text(response).trim())&&citations.length>0&&invalid.length===0&&uncited.length===0,markers:[...new Set(seen)].sort((a,b)=>a-b),invalidMarkers:invalid,uncitedSegments:uncited,citations};
  }
  function applyResponse(request,response,source='manual',nowFn){
    const next=JSON.parse(JSON.stringify(request||{}));const body=clean(response,MAX_RESPONSE);const coverage=citationCoverage(next,body);if(!coverage.valid)return {ok:false,message:!body?'Enter a response draft.':coverage.invalidMarkers.length?`Invalid citation marker(s): ${coverage.invalidMarkers.map(n=>`[${n}]`).join(', ')}`:coverage.uncitedSegments.length?'Every substantive response segment must include at least one citation marker from the grounding set.':'The response must cite at least one selected grounding record.',coverage};
    const stamp=typeof nowFn==='function'?nowFn():new Date().toISOString();next.response=body;next.responseSource=SOURCES.has(text(source))?text(source):'manual';next.citations=coverage.citations;next.citationCoverage={valid:true,markers:coverage.markers,invalidMarkers:[],uncitedSegments:[]};next.status='response-draft';next.updatedAt=stamp;return {ok:true,record:next,coverage};
  }
  function promptMarkdown(request){
    const r=request||{};const lines=[`# ${clean(r.title,240)||'Grounded research request'}`,'',`Task: ${clean(r.task,80)}`,'',`Question: ${clean(r.question,MAX_QUESTION)}`,'','## Grounding set'];
    list(r.grounding).forEach(g=>{lines.push('',`[${g.number}] ${g.title} — ${g.projectTitle||'Workspace'} (${g.kind}${g.subtype?` / ${g.subtype}`:''})`,g.provenance?.sourceTitle?`Recorded source: ${g.provenance.sourceTitle}`:'',g.provenance?.sourceUrl?`Recorded URL: ${g.provenance.sourceUrl}`:'',g.excerpt?`Excerpt:\n${g.excerpt}`:'');});
    lines.push('','## Response requirements','Use only the grounding set above. Cite factual or interpretive claims with [1], [2], etc. Every substantive paragraph or list block must contain at least one valid citation marker. Do not invent sources, metadata, relationships, or facts outside the supplied grounding set. Return a draft for human review.');return lines.filter((v,i,a)=>v!==''||a[i-1]!=='').join('\n');
  }
  function materializationPayload(request){const r=request||{};const refs=list(r.citations).map(c=>`[${c.number}] ${c.title}${c.projectTitle?` — ${c.projectTitle}`:''}`).join('\n');return {title:`${clean(r.title,200)||'Grounded research'} — reviewed draft`,summary:`Grounded Research Assistant II draft based on ${list(r.grounding).length} explicitly selected Integrated Knowledge record(s).`,content:`${text(r.response).trim()}${refs?`\n\n## Grounding references\n${refs}`:''}`,status:'working',tags:['grounded-research-assistant','grounded-draft'],provenance:{sourceType:'tool',sourceTitle:'Grounded Research Assistant II',sourceUrl:'',capturedAt:new Date().toISOString(),requestId:clean(r.id,160),groundingFingerprint:clean(r.groundingFingerprint,80)}};}
  function normalizeSession(raw){const r=raw&&typeof raw==='object'?JSON.parse(JSON.stringify(raw)):{};r.schema=REQUEST_SCHEMA;r.id=clean(r.id,160);r.title=clean(r.title,240)||'Grounded research question';r.task=TASKS.has(text(r.task))?r.task:'general-question';r.question=clean(r.question,MAX_QUESTION);r.status=STATUS.has(text(r.status))?r.status:'prepared';r.grounding=list(r.grounding).slice(0,MAX_SCOPE).map((g,i)=>({...g,number:i+1}));r.response=clean(r.response,MAX_RESPONSE);r.responseSource=SOURCES.has(text(r.responseSource))?r.responseSource:'manual';r.citations=list(r.citations);return r;}
  function normalizeLibrary(raw){const x=raw&&typeof raw==='object'?raw:{};return {schema:LIBRARY_SCHEMA,sessions:list(x.sessions).map(normalizeSession).filter(s=>s.id).slice(0,MAX_SESSIONS),updatedAt:clean(x.updatedAt,80)};}
  function exportRequest(request){return {schema:REQUEST_EXPORT_SCHEMA,exportedAt:new Date().toISOString(),request:normalizeSession(request),governance:{explicitScope:true,citationEnforced:true,draftOnly:true,automaticAI:false,automaticMutation:false}};}
  function exportResponse(request){return {schema:RESPONSE_EXPORT_SCHEMA,exportedAt:new Date().toISOString(),response:normalizeSession(request),governance:{humanReviewRequired:true,canonicalWrite:false}};}
  function governance(){return {schema:SCHEMA,explicitScopeRequired:true,groundingFrozenInRequest:true,citationMarkersRequired:true,invalidCitationsRejected:true,substantiveSegmentsRequireCitations:true,draftOnlyOutputs:true,humanReviewRequired:true,automaticAI:false,automaticScopeExpansion:false,automaticCanonicalMutation:false,metadataInvention:false,providerNeutral:true,localFirst:true};}
  return {SCHEMA,REQUEST_SCHEMA,RESPONSE_SCHEMA,REQUEST_EXPORT_SCHEMA,RESPONSE_EXPORT_SCHEMA,LIBRARY_SCHEMA,STORAGE_KEY,MAX_SESSIONS,MAX_SCOPE,MAX_QUESTION,MAX_RESPONSE,TASKS,STATUS,SOURCES,canonicalGrounding,prepareRequest,markers,citationCoverage,applyResponse,promptMarkdown,materializationPayload,normalizeSession,normalizeLibrary,exportRequest,exportResponse,governance,fnv1a};
});
