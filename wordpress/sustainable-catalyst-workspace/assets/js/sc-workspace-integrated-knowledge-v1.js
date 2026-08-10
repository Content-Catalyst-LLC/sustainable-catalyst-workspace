(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceIntegratedKnowledge=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-integrated-knowledge/1.0';
  const REF_SCHEMA='sc-workspace-integrated-knowledge-ref/1.0';
  const KINDS=new Set(['object','notebook','notebook-block','research-question','research-claim']);
  const text=v=>String(v||'');
  function ref(kind,projectId,id,extra={}){return {schema:REF_SCHEMA,kind,projectId:text(projectId).slice(0,160),id:text(id).slice(0,160),notebookId:text(extra.notebookId).slice(0,160),sectionId:text(extra.sectionId).slice(0,160)};}
  function entry(base){return {schema:SCHEMA,key:base.key,kind:base.kind,subtype:base.subtype||'',projectId:base.projectId,projectTitle:base.projectTitle||'',projectArchived:Boolean(base.projectArchived),id:base.id,title:base.title||'Untitled',summary:base.summary||'',content:base.content||'',tags:Array.isArray(base.tags)?base.tags.slice(0,50):[],updatedAt:base.updatedAt||'',ref:base.ref,origin:base.origin||'',notebookId:base.notebookId||'',sectionId:base.sectionId||'',provenance:base.provenance&&typeof base.provenance==='object'?base.provenance:{}};}
  function derive(state){
    const out=[]; const projects=Array.isArray(state&&state.projects)?state.projects:[];
    projects.forEach(project=>{
      const pid=text(project.id), ptitle=text(project.title), archived=Boolean(project.archivedAt);
      (Array.isArray(project.objects)?project.objects:[]).forEach(o=>{if(!o||o.archivedAt)return;out.push(entry({key:`object:${pid}:${o.id}`,kind:'object',subtype:text(o.type),projectId:pid,projectTitle:ptitle,projectArchived:archived,id:text(o.id),title:text(o.title),summary:text(o.summary),content:text(o.content),tags:o.tags,updatedAt:o.updatedAt,ref:ref('object',pid,o.id),origin:'Personal Knowledge / Workspace Object',provenance:o.provenance}));});
      const research=project.research&&typeof project.research==='object'?project.research:{};
      (Array.isArray(research.questions)?research.questions:[]).forEach(q=>out.push(entry({key:`research-question:${pid}:${q.id}`,kind:'research-question',subtype:text(q.status),projectId:pid,projectTitle:ptitle,projectArchived:archived,id:text(q.id),title:text(q.text).slice(0,180)||'Research question',summary:text(q.text),content:text(q.text),tags:[],updatedAt:q.updatedAt,ref:ref('research-question',pid,q.id),origin:'Research Workspace'})));
      (Array.isArray(research.claims)?research.claims:[]).forEach(c=>out.push(entry({key:`research-claim:${pid}:${c.id}`,kind:'research-claim',subtype:text(c.status),projectId:pid,projectTitle:ptitle,projectArchived:archived,id:text(c.id),title:text(c.text).slice(0,180)||'Research claim',summary:text(c.text),content:text(c.text),tags:[],updatedAt:c.updatedAt,ref:ref('research-claim',pid,c.id),origin:'Research Workspace'})));
      const nws=project.notebooks&&typeof project.notebooks==='object'?project.notebooks:{};
      (Array.isArray(nws.notebooks)?nws.notebooks:[]).forEach(nb=>{
        out.push(entry({key:`notebook:${pid}:${nb.id}`,kind:'notebook',subtype:'notebook',projectId:pid,projectTitle:ptitle,projectArchived:archived,id:text(nb.id),title:text(nb.title),summary:text(nb.description),content:text(nb.description),tags:[],updatedAt:nb.updatedAt,ref:ref('notebook',pid,nb.id,{notebookId:nb.id}),origin:'Research Notebook',notebookId:text(nb.id)}));
        (Array.isArray(nb.sections)?nb.sections:[]).forEach(sec=>(Array.isArray(sec.blocks)?sec.blocks:[]).forEach(block=>out.push(entry({key:`notebook-block:${pid}:${nb.id}:${block.id}`,kind:'notebook-block',subtype:text(block.type),projectId:pid,projectTitle:ptitle,projectArchived:archived,id:text(block.id),title:text(block.title)||text(block.content).slice(0,120)||'Notebook block',summary:text(block.content).slice(0,500),content:text(block.content),tags:block.tags,updatedAt:block.updatedAt,ref:ref('notebook-block',pid,block.id,{notebookId:nb.id,sectionId:sec.id}),origin:'Research Notebook',notebookId:text(nb.id),sectionId:text(sec.id),provenance:{sourceTitle:block.sourceTitle||'',sourceUrl:block.sourceUrl||'',bibliography:block.bibliography||{},capture:block.capture||{}}}))));
      });
    });
    return out.sort((a,b)=>text(b.updatedAt).localeCompare(text(a.updatedAt))||a.title.localeCompare(b.title));
  }
  function filter(entries,prefs={}){const q=text(prefs.query).trim().toLowerCase(),kind=text(prefs.kind||'all'),project=text(prefs.project||'all'),scope=text(prefs.scope||'active');return (Array.isArray(entries)?entries:[]).filter(e=>{if(scope!=='all'&&e.projectArchived)return false;if(project!=='all'&&e.projectId!==project)return false;if(kind!=='all'&&e.kind!==kind)return false;if(!q)return true;const hay=[e.title,e.summary,e.content,e.projectTitle,e.origin,e.subtype,...e.tags,text(e.provenance&&e.provenance.sourceTitle),text(e.provenance&&e.provenance.sourceUrl)].join('\n').toLowerCase();return hay.includes(q);});}
  function stats(entries){const list=Array.isArray(entries)?entries:[];return {total:list.length,objects:list.filter(e=>e.kind==='object').length,notebooks:list.filter(e=>e.kind==='notebook'||e.kind==='notebook-block').length,research:list.filter(e=>e.kind==='research-question'||e.kind==='research-claim').length,projects:new Set(list.map(e=>e.projectId)).size};}
  function connections(target,state){if(!target)return[];const out=[];const project=(state.projects||[]).find(p=>p.id===target.projectId);if(!project)return out;const nws=project.notebooks||{};(nws.links||[]).forEach(l=>{const s=l.source||{},t=l.target||{};const match=(r)=>r&&(r.id===target.id||r.notebookId===target.id);if(match(s)||match(t))out.push({relation:l.relation||'related',source:'explicit-notebook-link',linkId:l.id||''});});if(target.kind==='object'){(project.research?.evidenceLinks||[]).forEach(l=>{if(l.sourceObjectId===target.id||l.evidenceObjectId===target.id)out.push({relation:'evidence-link',source:'research-workspace',linkId:l.id||''});});(project.research?.claims||[]).forEach(c=>{if((c.evidenceObjectIds||[]).includes(target.id))out.push({relation:'supports-claim',source:'research-workspace',linkId:c.id||''});});}return out;}
  function snapshot(state,prefs={}){const entries=derive(state);return {schema:SCHEMA,generatedAt:new Date().toISOString(),entries:filter(entries,prefs),stats:stats(entries),governance:{derivedFromCanonicalRecords:true,duplicatesCanonicalContent:false,automaticSemanticInference:false,automaticAI:false,automaticMutation:false,localFirst:true}};}
  return {SCHEMA,REF_SCHEMA,KINDS,derive,filter,stats,connections,snapshot,ref};
});
