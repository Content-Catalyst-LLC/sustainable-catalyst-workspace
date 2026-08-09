(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  if(root) root.SCWorkspaceProjectDiff=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-change-review/1.0';
  const VOLATILE=new Set(['createdAt','updatedAt']);
  const OMIT=new Set(['persistence','recentTools','activity','activeObjectId','activeQuestionId','activeClaimId','activeMethodId','activeDecisionId','activeBoardId','activeDraftId','activeRunId','activeSessionId']);
  function clean(value){
    if(Array.isArray(value)) return value.map(clean);
    if(!value||typeof value!=='object') return value;
    const out={};Object.keys(value).sort().forEach(k=>{if(VOLATILE.has(k)||OMIT.has(k))return;out[k]=clean(value[k]);});return out;
  }
  function stable(value){return JSON.stringify(clean(value));}
  function changedFields(a,b){const aa=clean(a||{}),bb=clean(b||{}),keys=new Set([...Object.keys(aa),...Object.keys(bb)]);return [...keys].filter(k=>JSON.stringify(aa[k])!==JSON.stringify(bb[k])).sort();}
  function label(item){return String(item?.title||item?.label||item?.text||item?.risk||item?.id||'Untitled').slice(0,180);}
  function compareList(category,base,target,kind='content'){
    const a=Array.isArray(base)?base:[],b=Array.isArray(target)?target:[],am=new Map(a.filter(x=>x&&x.id).map(x=>[String(x.id),x])),bm=new Map(b.filter(x=>x&&x.id).map(x=>[String(x.id),x]));
    const changes=[];
    for(const [id,item] of bm){if(!am.has(id))changes.push({change:'added',id,label:label(item),fields:[]});else if(stable(am.get(id))!==stable(item))changes.push({change:'modified',id,label:label(item),fields:changedFields(am.get(id),item)});}
    for(const [id,item] of am){if(!bm.has(id))changes.push({change:'removed',id,label:label(item),fields:[]});}
    return {category,kind,changes};
  }
  function compareMetadata(base,target){const keys=['title','description','status','pinned','notes','archivedAt'];const changes=[];for(const key of keys){if(JSON.stringify(base?.[key]??null)!==JSON.stringify(target?.[key]??null))changes.push({change:'modified',id:key,label:key,fields:[key]});}return {category:'Project metadata',kind:'content',changes};}
  function compareProjects(base,target,meta={}){
    if(!base||!target||typeof base!=='object'||typeof target!=='object')throw new Error('Two project snapshots are required.');
    const cats=[
      compareMetadata(base,target),
      compareList('Canonical objects',base.objects,target.objects),
      compareList('Research questions',base.research?.questions,target.research?.questions),
      compareList('Research claims',base.research?.claims,target.research?.claims),
      compareList('Evidence links',base.research?.evidenceLinks,target.research?.evidenceLinks,'relationship'),
      compareList('Analysis assumptions',base.analysis?.assumptions,target.analysis?.assumptions),
      compareList('Analysis methods',base.analysis?.methods,target.analysis?.methods),
      compareList('Analysis findings',base.analysis?.findings,target.analysis?.findings),
      compareList('Decisions',base.decision?.decisions,target.decision?.decisions),
      compareList('Decision options',base.decision?.options,target.decision?.options),
      compareList('Decision criteria',base.decision?.criteria,target.decision?.criteria),
      compareList('Decision assessments',base.decision?.assessments,target.decision?.assessments),
      compareList('Decision risks',base.decision?.risks,target.decision?.risks),
      compareList('Evidence assessments',base.traceability?.evidenceAssessments,target.traceability?.evidenceAssessments),
      compareList('Traceability relationships',base.traceability?.lineage,target.traceability?.lineage,'relationship'),
      compareList('Reproducibility records',base.traceability?.reproducibility,target.traceability?.reproducibility),
      compareList('Canvas boards',base.canvas?.boards,target.canvas?.boards),
      compareList('Canvas nodes',base.canvas?.nodes,target.canvas?.nodes),
      compareList('Canvas relationships',base.canvas?.edges,target.canvas?.edges,'relationship'),
      compareList('Briefing drafts',base.briefing?.drafts,target.briefing?.drafts),
      compareList('Guided workflows',base.guidedWorkflows?.runs,target.guidedWorkflows?.runs)
    ].filter(c=>c.changes.length);
    let added=0,removed=0,modified=0,relationships=0;
    cats.forEach(c=>{c.changes.forEach(ch=>{if(ch.change==='added')added++;else if(ch.change==='removed')removed++;else modified++;if(c.kind==='relationship')relationships++;});});
    const flags=[];
    const by=name=>cats.find(c=>c.category===name)?.changes.length||0;
    if(by('Canonical objects'))flags.push('Canonical objects changed');
    if(by('Research claims')||by('Evidence links')||by('Evidence assessments'))flags.push('Evidence basis changed');
    if(by('Analysis assumptions'))flags.push('Assumptions changed');
    if(by('Analysis findings')||by('Analysis methods'))flags.push('Analysis changed');
    if(by('Decisions')||by('Decision options')||by('Decision criteria')||by('Decision assessments')||by('Decision risks'))flags.push('Decision record changed');
    if(relationships)flags.push('Relationships changed');
    return {schema:SCHEMA,generatedAt:new Date().toISOString(),projectId:String(target.id||base.id||''),projectTitle:String(target.title||base.title||'Workspace project'),base:meta.base||{},target:meta.target||{},summary:{added,removed,modified,total:added+removed+modified,relationshipsChanged:relationships,categoriesChanged:cats.length},attention:flags,categories:cats,governance:{automaticApply:false,automaticRestore:false,automaticSync:false,score:false,reviewOnly:true}};
  }
  return {SCHEMA,clean,stable,changedFields,compareProjects};
});
