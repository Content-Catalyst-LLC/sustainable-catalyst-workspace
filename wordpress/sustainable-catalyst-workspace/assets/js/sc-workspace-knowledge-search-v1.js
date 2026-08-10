(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceKnowledgeSearch=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-knowledge-search/1.0';
  const SAVED_SEARCH_SCHEMA='sc-workspace-saved-search/1.0';
  const STORAGE_KEY='sc_workspace_saved_searches_v1';
  const SORTS=new Set(['relevance','updated-desc','updated-asc','title-asc','project-asc']);
  const PROVENANCE_FILTERS=new Set(['all','documented','linked','source-url','bibliographic']);
  const text=v=>String(v==null?'':v);
  const lower=v=>text(v).trim().toLowerCase();
  const list=v=>Array.isArray(v)?v:[];
  function normalizePrefs(raw={}){
    const p=raw&&typeof raw==='object'?raw:{};
    return {
      schema:SCHEMA,
      query:text(p.query).slice(0,320),
      kind:text(p.kind||'all').slice(0,80),
      subtype:text(p.subtype||'all').slice(0,80),
      project:text(p.project||'all').slice(0,160),
      tag:text(p.tag).slice(0,80),
      origin:text(p.origin||'all').slice(0,120),
      provenance:PROVENANCE_FILTERS.has(text(p.provenance))?text(p.provenance):'all',
      scope:text(p.scope)==='all'?'all':'active',
      sort:SORTS.has(text(p.sort))?text(p.sort):'relevance'
    };
  }
  function tokenize(query){
    const q=text(query).trim(); if(!q)return[];
    const out=[]; const re=/"([^"]+)"|(\S+)/g; let m;
    while((m=re.exec(q))!==null){const value=(m[1]||m[2]||'').trim();if(value)out.push(value.toLowerCase());if(out.length>=24)break;}
    return out;
  }
  function provenanceFacts(entry,state){
    const p=entry&&entry.provenance&&typeof entry.provenance==='object'?entry.provenance:{};
    const sourceTitle=text(p.sourceTitle||p.capture?.sourceTitle||p.bibliography?.title).trim();
    const sourceUrl=text(p.sourceUrl||p.capture?.sourceUrl||p.bibliography?.url).trim();
    const bibliography=p.bibliography&&typeof p.bibliography==='object'?p.bibliography:{};
    const bibliographic=Boolean(Object.values(bibliography).some(v=>text(v).trim()));
    const connections=connectionsFor(entry,state);
    return {sourceTitle,sourceUrl,bibliographic,linked:connections.length>0,documented:Boolean(sourceTitle||sourceUrl||bibliographic),connections};
  }
  function connectionsFor(entry,state){
    if(!entry||!state)return[];
    const out=[], seen=new Set(); const projects=list(state.projects); const project=projects.find(p=>text(p.id)===text(entry.projectId)); if(!project)return out;
    const add=(relation,source,targetKey='',detail='')=>{const key=[relation,source,targetKey,detail].join('|');if(seen.has(key))return;seen.add(key);out.push({relation,source,targetKey,detail});};
    const nws=project.notebooks&&typeof project.notebooks==='object'?project.notebooks:{};
    list(nws.links).forEach(link=>{
      const s=link.source||{},t=link.target||{};
      const match=r=>r&&(text(r.id)===text(entry.id)||text(r.notebookId)===text(entry.id)||text(r.id)===text(entry.notebookId));
      if(match(s)||match(t))add(text(link.relation||'related'),'explicit-notebook-link','',text(link.id));
    });
    if(entry.kind==='object'){
      list(project.research?.evidenceLinks).forEach(link=>{if(text(link.sourceObjectId)===text(entry.id)||text(link.evidenceObjectId)===text(entry.id))add('evidence-link','research-workspace','',text(link.id));});
      list(project.research?.claims).forEach(claim=>{if(list(claim.evidenceObjectIds).map(text).includes(text(entry.id)))add('supports-claim','research-workspace',`research-claim:${entry.projectId}:${claim.id}`,text(claim.id));});
      list(nws.promotions).forEach(pr=>{if(text(pr.targetId)===text(entry.id)||text(pr.destinationId)===text(entry.id))add('promoted-from-notebook','promotion-ledger','',text(pr.id));});
    }
    return out;
  }
  function fields(entry,state){
    const facts=provenanceFacts(entry,state);
    return {
      title:lower(entry.title), summary:lower(entry.summary), content:lower(entry.content),
      project:lower(entry.projectTitle), origin:lower(entry.origin), kind:lower(entry.kind), subtype:lower(entry.subtype),
      tags:list(entry.tags).map(lower), source:lower([facts.sourceTitle,facts.sourceUrl].join(' ')), facts
    };
  }
  function matches(entry,prefs,state){
    const p=normalizePrefs(prefs),f=fields(entry,state),tokens=tokenize(p.query);
    if(p.scope!=='all'&&entry.projectArchived)return false;
    if(p.project!=='all'&&text(entry.projectId)!==p.project)return false;
    if(p.kind!=='all'&&text(entry.kind)!==p.kind)return false;
    if(p.subtype!=='all'&&text(entry.subtype)!==p.subtype)return false;
    if(p.origin!=='all'&&text(entry.origin)!==p.origin)return false;
    const tag=lower(p.tag); if(tag&&!f.tags.some(t=>t.includes(tag)))return false;
    if(p.provenance==='documented'&&!f.facts.documented)return false;
    if(p.provenance==='linked'&&!f.facts.linked)return false;
    if(p.provenance==='source-url'&&!f.facts.sourceUrl)return false;
    if(p.provenance==='bibliographic'&&!f.facts.bibliographic)return false;
    if(tokens.length){const hay=[f.title,f.summary,f.content,f.project,f.origin,f.kind,f.subtype,f.tags.join(' '),f.source].join('\n');if(!tokens.every(t=>hay.includes(t)))return false;}
    return true;
  }
  function rank(entry,prefs,state){
    const p=normalizePrefs(prefs),f=fields(entry,state),tokens=tokenize(p.query);let score=0;const reasons=[];
    tokens.forEach(t=>{
      if(f.title.includes(t)){score+=40;reasons.push(`title matches “${t}”`);}
      else if(f.tags.some(x=>x.includes(t))){score+=28;reasons.push(`tag matches “${t}”`);}
      else if(f.source.includes(t)){score+=22;reasons.push(`recorded source matches “${t}”`);}
      else if(f.summary.includes(t)){score+=16;reasons.push(`summary matches “${t}”`);}
      else if(f.content.includes(t)){score+=8;reasons.push(`content matches “${t}”`);}
      if(f.project.includes(t)){score+=5;reasons.push(`project matches “${t}”`);}
    });
    if(f.facts.documented){score+=3;reasons.push('recorded provenance');}
    if(f.facts.linked){score+=2;reasons.push('explicit relationship');}
    if(!tokens.length)reasons.push('no text query; ordered by selected sort');
    return {score,reasons:[...new Set(reasons)].slice(0,8)};
  }
  function search(entries,prefs={},state={}){
    const p=normalizePrefs(prefs);
    const rows=list(entries).filter(e=>matches(e,p,state)).map(entry=>({entry,rank:rank(entry,p,state)}));
    const byTitle=(a,b)=>text(a.entry.title).localeCompare(text(b.entry.title));
    if(p.sort==='updated-desc')rows.sort((a,b)=>text(b.entry.updatedAt).localeCompare(text(a.entry.updatedAt))||byTitle(a,b));
    else if(p.sort==='updated-asc')rows.sort((a,b)=>text(a.entry.updatedAt).localeCompare(text(b.entry.updatedAt))||byTitle(a,b));
    else if(p.sort==='title-asc')rows.sort(byTitle);
    else if(p.sort==='project-asc')rows.sort((a,b)=>text(a.entry.projectTitle).localeCompare(text(b.entry.projectTitle))||byTitle(a,b));
    else rows.sort((a,b)=>b.rank.score-a.rank.score||text(b.entry.updatedAt).localeCompare(text(a.entry.updatedAt))||byTitle(a,b));
    return rows;
  }
  function facets(entries){
    const uniq=(values)=>[...new Set(values.filter(Boolean))].sort((a,b)=>a.localeCompare(b));
    return {kinds:uniq(list(entries).map(e=>text(e.kind))),subtypes:uniq(list(entries).map(e=>text(e.subtype))),origins:uniq(list(entries).map(e=>text(e.origin))),tags:uniq(list(entries).flatMap(e=>list(e.tags).map(text)))};
  }
  function related(target,entries,state){
    if(!target)return[];const all=list(entries),facts=provenanceFacts(target,state),out=[],seen=new Set();
    const push=(entry,reason,source)=>{if(!entry||entry.key===target.key||seen.has(entry.key))return;seen.add(entry.key);out.push({entry,reason,source});};
    facts.connections.forEach(c=>{if(c.targetKey){push(all.find(e=>e.key===c.targetKey),c.relation,c.source);}});
    const targetSource=lower(facts.sourceUrl||facts.sourceTitle);
    if(targetSource)all.forEach(e=>{const ef=provenanceFacts(e,state);const source=lower(ef.sourceUrl||ef.sourceTitle);if(source&&source===targetSource)push(e,'same recorded source','provenance');});
    if(target.notebookId)all.forEach(e=>{if(e.notebookId&&e.notebookId===target.notebookId)push(e,'same notebook','notebook containment');});
    if(target.kind==='object'){
      const project=list(state.projects).find(p=>text(p.id)===text(target.projectId));
      list(project?.research?.evidenceLinks).forEach(l=>{const other=text(l.sourceObjectId)===text(target.id)?text(l.evidenceObjectId):text(l.evidenceObjectId)===text(target.id)?text(l.sourceObjectId):'';if(other)push(all.find(e=>e.kind==='object'&&e.projectId===target.projectId&&e.id===other),'evidence relationship','research-workspace');});
    }
    return out.slice(0,20);
  }
  function savedSearch(raw,idFactory){
    const p=raw&&typeof raw==='object'?raw:{}; const id=text(p.id|| (typeof idFactory==='function'?idFactory():`ss-${Date.now().toString(36)}`)).slice(0,160);
    return {schema:SAVED_SEARCH_SCHEMA,id,name:text(p.name||'Saved search').trim().slice(0,120)||'Saved search',preferences:normalizePrefs(p.preferences||p),createdAt:text(p.createdAt||new Date().toISOString()),updatedAt:text(p.updatedAt||new Date().toISOString())};
  }
  function normalizeSavedSearches(raw){return list(raw).map(x=>savedSearch(x)).filter(x=>x.id&&x.name).slice(0,40);}
  function serializeSavedSearches(items){return JSON.stringify(normalizeSavedSearches(items));}
  return {SCHEMA,SAVED_SEARCH_SCHEMA,STORAGE_KEY,SORTS,PROVENANCE_FILTERS,normalizePrefs,tokenize,provenanceFacts,connectionsFor,matches,rank,search,facets,related,savedSearch,normalizeSavedSearches,serializeSavedSearches};
});
