(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceResearchCollections=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const COLLECTION_SCHEMA='sc-workspace-research-collection/1.0';
  const VIEW_SCHEMA='sc-workspace-research-view/1.0';
  const COLLECTION_STORAGE_KEY='sc_workspace_research_collections_v1';
  const VIEW_STORAGE_KEY='sc_workspace_research_views_v1';
  const MAX_COLLECTIONS=30,MAX_VIEWS=30;
  const GROUPS=new Set(['none','project','kind','subtype','origin']);
  const DENSITIES=new Set(['compact','comfortable']);
  const text=v=>String(v==null?'':v);
  const list=v=>Array.isArray(v)?v:[];
  const now=()=>new Date().toISOString();
  const baseCriteria=()=>({query:'',kind:'all',subtype:'all',project:'all',tag:'',origin:'all',provenance:'all',scope:'active',sort:'relevance'});
  function criteria(raw={},searchApi){
    const merged=Object.assign(baseCriteria(),raw&&typeof raw==='object'?raw:{});
    return searchApi&&typeof searchApi.normalizePrefs==='function'?searchApi.normalizePrefs(merged):merged;
  }
  function smartCollection(raw={},idFactory,searchApi){
    const stamp=now(),source=raw&&typeof raw==='object'?raw:{};
    const id=text(source.id||(typeof idFactory==='function'?idFactory():`rc-${Date.now().toString(36)}`)).slice(0,160);
    return {schema:COLLECTION_SCHEMA,id,name:(text(source.name||'Smart collection').trim().slice(0,120)||'Smart collection'),description:text(source.description).trim().slice(0,600),criteria:criteria(source.criteria||source.preferences||source,searchApi),createdAt:text(source.createdAt||stamp),updatedAt:text(source.updatedAt||stamp)};
  }
  function researchView(raw={},idFactory,searchApi){
    const stamp=now(),source=raw&&typeof raw==='object'?raw:{},presentation=source.presentation&&typeof source.presentation==='object'?source.presentation:{};
    const id=text(source.id||(typeof idFactory==='function'?idFactory():`rv-${Date.now().toString(36)}`)).slice(0,160);
    return {schema:VIEW_SCHEMA,id,name:(text(source.name||'Research view').trim().slice(0,120)||'Research view'),criteria:criteria(source.criteria||source.preferences||source,searchApi),presentation:{groupBy:GROUPS.has(text(presentation.groupBy))?text(presentation.groupBy):'project',density:DENSITIES.has(text(presentation.density))?text(presentation.density):'comfortable',limit:Math.max(10,Math.min(200,Number(presentation.limit)||60))},builtin:Boolean(source.builtin),createdAt:text(source.createdAt||stamp),updatedAt:text(source.updatedAt||stamp)};
  }
  const BUILTINS=[
    {id:'sources',name:'Sources',description:'Source objects in the current project/scope lens.',subtype:'source'},
    {id:'evidence',name:'Evidence',description:'Evidence objects in the current project/scope lens.',subtype:'evidence'},
    {id:'decisions',name:'Decisions',description:'Decision objects in the current project/scope lens.',subtype:'decision'},
    {id:'analysis',name:'Analysis',description:'Analysis objects in the current project/scope lens.',subtype:'analysis'},
    {id:'notebooks',name:'Notebooks',description:'Notebook-level records in the current project/scope lens.',kind:'notebook'},
    {id:'documented',name:'Documented',description:'Records with source or bibliographic provenance.',provenance:'documented'}
  ];
  function builtinCriteria(id,current={},searchApi){
    const def=BUILTINS.find(x=>x.id===id);if(!def)return criteria(current,searchApi);
    const next=Object.assign(baseCriteria(),{project:text(current.project||'all'),scope:text(current.scope)==='all'?'all':'active',sort:'updated-desc'});
    if(def.subtype){next.kind='object';next.subtype=def.subtype;}
    if(def.kind)next.kind=def.kind;
    if(def.provenance)next.provenance=def.provenance;
    return criteria(next,searchApi);
  }
  function builtinViews(current={},searchApi){return BUILTINS.map(def=>researchView({id:`builtin-${def.id}`,name:def.name,criteria:builtinCriteria(def.id,current,searchApi),presentation:{groupBy:'project',density:'compact',limit:80},builtin:true,createdAt:'',updatedAt:''},null,searchApi));}
  function normalizeCollections(raw,searchApi){return list(raw).map(x=>smartCollection(x,null,searchApi)).filter(x=>x.id&&x.name).slice(0,MAX_COLLECTIONS);}
  function normalizeViews(raw,searchApi){return list(raw).map(x=>researchView(x,null,searchApi)).filter(x=>x.id&&x.name&&!x.builtin).slice(0,MAX_VIEWS);}
  function serializeCollections(items,searchApi){return JSON.stringify(normalizeCollections(items,searchApi));}
  function serializeViews(items,searchApi){return JSON.stringify(normalizeViews(items,searchApi));}
  function evaluate(entries,collection,state,searchApi){if(!searchApi||typeof searchApi.search!=='function')return[];const c=collection&&collection.criteria?collection.criteria:collection||{};return searchApi.search(list(entries),criteria(c,searchApi),state);}
  function group(rows,groupBy='project'){
    const mode=GROUPS.has(groupBy)?groupBy:'project';if(mode==='none')return[{key:'all',label:'All results',rows:list(rows)}];
    const map=new Map();
    list(rows).forEach(row=>{const e=row.entry||row;let key='',label='';if(mode==='project'){key=text(e.projectId||'unknown');label=text(e.projectTitle||'Unknown project');}else if(mode==='kind'){key=text(e.kind||'unknown');label=text(e.kind||'Unknown kind').replaceAll('-',' ');}else if(mode==='subtype'){key=text(e.subtype||'unknown');label=text(e.subtype||'Unknown subtype').replaceAll('-',' ');}else{key=text(e.origin||'unknown');label=text(e.origin||'Unknown origin');}if(!map.has(key))map.set(key,{key,label,rows:[]});map.get(key).rows.push(row);});
    return [...map.values()].sort((a,b)=>a.label.localeCompare(b.label));
  }
  function dashboard(entries,state,searchApi,current={}){
    const base=criteria({project:current.project||'all',scope:current.scope||'active',sort:'updated-desc'},searchApi);
    const scoped=searchApi&&typeof searchApi.search==='function'?searchApi.search(list(entries),base,state).map(x=>x.entry):list(entries);
    const subtype=t=>scoped.filter(e=>e.kind==='object'&&e.subtype===t).length;
    const documented=scoped.filter(e=>searchApi&&typeof searchApi.provenanceFacts==='function'&&searchApi.provenanceFacts(e,state).documented).length;
    return {records:scoped.length,projects:new Set(scoped.map(e=>e.projectId).filter(Boolean)).size,sources:subtype('source'),evidence:subtype('evidence'),decisions:subtype('decision'),documented};
  }
  return {COLLECTION_SCHEMA,VIEW_SCHEMA,COLLECTION_STORAGE_KEY,VIEW_STORAGE_KEY,MAX_COLLECTIONS,MAX_VIEWS,GROUPS,DENSITIES,BUILTINS,criteria,smartCollection,researchView,builtinCriteria,builtinViews,normalizeCollections,normalizeViews,serializeCollections,serializeViews,evaluate,group,dashboard};
});
