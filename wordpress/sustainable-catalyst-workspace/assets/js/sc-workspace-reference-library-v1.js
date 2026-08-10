(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceReferenceLibrary=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const REFERENCE_SCHEMA='sc-workspace-reference/1.0';
  const LIBRARY_SCHEMA='sc-workspace-reference-library/1.0';
  const PREFERENCES_SCHEMA='sc-workspace-citation-preferences/1.0';
  const EXPORT_SCHEMA='sc-workspace-reference-library-export/1.0';
  const STORAGE_KEY='sc_workspace_reference_library_v1';
  const PREFS_KEY='sc_workspace_citation_preferences_v1';
  const MAX_REFERENCES=1500;
  const STYLES=new Set(['apa7','chicago-author-date','mla9','ieee']);
  const TYPES=new Set(['article','book','chapter','report','webpage','dataset','thesis','conference','other']);
  const text=v=>String(v==null?'':v);
  const list=v=>Array.isArray(v)?v:[];
  const clean=v=>text(v).replace(/\s+/g,' ').trim();
  const lower=v=>clean(v).toLowerCase();
  const now=()=>new Date().toISOString();
  const slug=v=>lower(v).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');
  function normalizeDoi(v){return lower(v).replace(/^https?:\/\/(dx\.)?doi\.org\//,'').replace(/^doi:\s*/,'').trim();}
  function normalizeUrl(v){const s=clean(v);if(!s)return'';try{return new URL(s).toString();}catch(_){return s.slice(0,2000);}}
  function authors(raw){
    const values=Array.isArray(raw)?raw:text(raw).split(';');
    return values.map(clean).filter(Boolean).slice(0,20);
  }
  function yearOf(ref){const m=clean(ref&&ref.publicationDate).match(/\b(1[5-9]\d{2}|20\d{2}|21\d{2})\b/);return m?m[1]:'';}
  function surname(author){const a=clean(author);if(!a)return'';if(a.includes(','))return clean(a.split(',')[0]);const parts=a.split(' ');return parts[parts.length-1]||'';}
  function originRef(raw={}){return {schema:'sc-workspace-integrated-knowledge-ref/1.0',kind:clean(raw.kind).slice(0,80),projectId:clean(raw.projectId).slice(0,160),id:clean(raw.id).slice(0,160),key:clean(raw.key).slice(0,360)};}
  function normalizeReference(raw={},idFactory){
    const r=raw&&typeof raw==='object'?raw:{};const stamp=now();
    const id=clean(r.id||(typeof idFactory==='function'?idFactory():`ref-${Date.now().toString(36)}`)).slice(0,160);
    const doi=normalizeDoi(r.doi);const title=clean(r.title).slice(0,500);
    const out={schema:REFERENCE_SCHEMA,id,type:TYPES.has(clean(r.type))?clean(r.type):'other',title,authors:authors(r.authors),publicationDate:clean(r.publicationDate).slice(0,80),containerTitle:clean(r.containerTitle).slice(0,300),publisher:clean(r.publisher).slice(0,300),edition:clean(r.edition).slice(0,100),volume:clean(r.volume).slice(0,80),issue:clean(r.issue).slice(0,80),pages:clean(r.pages||r.locator).slice(0,120),url:normalizeUrl(r.url||r.sourceUrl),doi,identifier:clean(r.identifier).slice(0,240),citationKey:clean(r.citationKey).slice(0,120),tags:list(r.tags).length?list(r.tags).map(clean).filter(Boolean).slice(0,40):text(r.tags).split(',').map(clean).filter(Boolean).slice(0,40),notes:clean(r.notes).slice(0,4000),origins:list(r.origins).map(originRef).filter(x=>x.key||x.id).slice(0,40),createdAt:clean(r.createdAt||stamp),updatedAt:clean(r.updatedAt||stamp)};
    return out;
  }
  function fingerprint(raw){
    const r=normalizeReference(raw,()=>clean(raw&&raw.id)||'ref');
    if(r.doi)return`doi:${r.doi}`;
    const y=yearOf(r),first=lower(surname(r.authors[0]||'')),title=lower(r.title).replace(/[^a-z0-9]+/g,' ').trim();
    const id=lower(r.identifier);
    return`bib:${title}|${first}|${y}|${id}`;
  }
  function duplicateGroups(items){
    const map=new Map();list(items).forEach(item=>{const key=fingerprint(item);if(!key||key==='bib:|||')return;if(!map.has(key))map.set(key,[]);map.get(key).push(item);});
    return [...map.entries()].filter(([,refs])=>refs.length>1).map(([fingerprint,references])=>({fingerprint,references}));
  }
  function citationKeyBase(raw){
    const r=normalizeReference(raw,()=>clean(raw&&raw.id)||'ref');const a=slug(surname(r.authors[0]||''))||'source';const y=yearOf(r)||'nd';const word=slug(r.title).split('-').find(Boolean)||'work';return`${a}${y}${word}`.slice(0,100);
  }
  function uniqueCitationKey(raw,existing=[]){const base=citationKeyBase(raw);const used=new Set(list(existing).map(x=>lower(x.citationKey)).filter(Boolean));if(!used.has(lower(base)))return base;let i=2;while(used.has(lower(`${base}${i}`)))i++;return`${base}${i}`.slice(0,120);}
  function authorText(ref,style){const a=list(ref.authors);if(!a.length)return'';if(style==='mla9')return a.length===1?a[0]:`${a[0]} et al.`;if(style==='ieee')return a.join(', ');if(a.length===1)return a[0];if(a.length===2)return`${a[0]} & ${a[1]}`;return`${a.slice(0,-1).join(', ')}, & ${a[a.length-1]}`;}
  function format(raw,style='apa7',index=1){
    const r=normalizeReference(raw,()=>clean(raw&&raw.id)||'ref'),s=STYLES.has(style)?style:'apa7',a=authorText(r,s),y=yearOf(r),parts=[];
    const link=r.doi?`https://doi.org/${r.doi}`:r.url;
    if(s==='ieee'){
      if(a)parts.push(a);if(r.title)parts.push(`“${r.title},”`);if(r.containerTitle)parts.push(r.containerTitle);if(r.publisher)parts.push(r.publisher);if(y)parts.push(y);if(r.volume)parts.push(`vol. ${r.volume}`);if(r.issue)parts.push(`no. ${r.issue}`);if(r.pages)parts.push(`pp. ${r.pages}`);if(link)parts.push(link);return`[${index}] ${parts.join(', ').replace(/,+,/g,',')}`.trim();
    }
    if(s==='mla9'){
      if(a)parts.push(`${a}.`);if(r.title)parts.push(`“${r.title}.”`);if(r.containerTitle)parts.push(`${r.containerTitle},`);if(r.publisher)parts.push(`${r.publisher},`);if(y)parts.push(`${y}.`);if(r.pages)parts.push(`pp. ${r.pages}.`);if(link)parts.push(link);return parts.join(' ').replace(/\s+/g,' ').trim();
    }
    if(s==='chicago-author-date'){
      if(a)parts.push(`${a}.`);if(y)parts.push(`${y}.`);else parts.push('n.d.');if(r.title)parts.push(`“${r.title}.”`);if(r.containerTitle)parts.push(`${r.containerTitle}.`);if(r.publisher)parts.push(`${r.publisher}.`);if(link)parts.push(link);return parts.join(' ').replace(/\s+/g,' ').trim();
    }
    if(a)parts.push(`${a}.`);if(y)parts.push(`(${y}).`);else parts.push('(n.d.).');if(r.title)parts.push(`${r.title}.`);if(r.containerTitle)parts.push(`${r.containerTitle}.`);if(r.publisher)parts.push(`${r.publisher}.`);if(link)parts.push(link);return parts.join(' ').replace(/\s+/g,' ').trim();
  }
  function referenceFromEntry(entry,idFactory){
    const e=entry&&typeof entry==='object'?entry:{},p=e.provenance&&typeof e.provenance==='object'?e.provenance:{},b=p.bibliography&&typeof p.bibliography==='object'?p.bibliography:{};
    const r=normalizeReference({type:e.subtype==='dataset'?'dataset':(b.containerTitle?'article':'other'),title:b.title||p.sourceTitle||e.title,authors:b.authors||[],publicationDate:b.publicationDate||'',containerTitle:b.containerTitle||'',publisher:b.publisher||'',edition:b.edition||'',volume:b.volume||'',issue:b.issue||'',pages:b.locator||'',url:b.url||p.sourceUrl||'',doi:b.doi||'',identifier:b.identifier||'',tags:e.tags||[],notes:'',origins:[{kind:e.kind,projectId:e.projectId,id:e.id,key:e.key}]},idFactory);
    return r;
  }
  function normalizeLibrary(raw){const src=raw&&typeof raw==='object'?raw:{};const refs=list(src.references||raw).map(x=>normalizeReference(x)).filter(x=>x.id&&x.title).slice(0,MAX_REFERENCES);return{schema:LIBRARY_SCHEMA,references:refs,updatedAt:clean(src.updatedAt||now())};}
  function preferences(raw={}){const s=STYLES.has(clean(raw.style))?clean(raw.style):'apa7';return{schema:PREFERENCES_SCHEMA,style:s,showUrls:raw.showUrls!==false,updatedAt:clean(raw.updatedAt||now())};}
  function serializeLibrary(raw){return JSON.stringify(normalizeLibrary(raw));}
  function exportPackage(raw,prefs={}){const lib=normalizeLibrary(raw);return{schema:EXPORT_SCHEMA,exportedAt:now(),library:lib,preferences:preferences(prefs),integrity:{algorithm:'deterministic-reference-fingerprints',fingerprints:lib.references.map(r=>({id:r.id,fingerprint:fingerprint(r)}))}};}
  return {REFERENCE_SCHEMA,LIBRARY_SCHEMA,PREFERENCES_SCHEMA,EXPORT_SCHEMA,STORAGE_KEY,PREFS_KEY,MAX_REFERENCES,STYLES,TYPES,normalizeDoi,normalizeUrl,authors,yearOf,surname,originRef,normalizeReference,fingerprint,duplicateGroups,citationKeyBase,uniqueCitationKey,format,referenceFromEntry,normalizeLibrary,preferences,serializeLibrary,exportPackage};
});
