(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  if(root) root.SCWorkspaceReconciliation=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-reconciliation/1.0';
  const PLAN_SCHEMA='sc-workspace-reconciliation-plan/1.0';
  const CATEGORY_PATHS={
    'Project metadata':null,
    'Canonical objects':['objects'],
    'Research questions':['research','questions'],
    'Research claims':['research','claims'],
    'Evidence links':['research','evidenceLinks'],
    'Analysis assumptions':['analysis','assumptions'],
    'Analysis methods':['analysis','methods'],
    'Analysis findings':['analysis','findings'],
    'Decisions':['decision','decisions'],
    'Decision options':['decision','options'],
    'Decision criteria':['decision','criteria'],
    'Decision assessments':['decision','assessments'],
    'Decision risks':['decision','risks'],
    'Evidence assessments':['traceability','evidenceAssessments'],
    'Traceability relationships':['traceability','lineage'],
    'Reproducibility records':['traceability','reproducibility'],
    'Canvas boards':['canvas','boards'],
    'Canvas nodes':['canvas','nodes'],
    'Canvas relationships':['canvas','edges'],
    'Briefing drafts':['briefing','drafts'],
    'Guided workflows':['guidedWorkflows','runs']
  };
  const clone=v=>JSON.parse(JSON.stringify(v));
  function key(category,change){return `${String(category||'')}::${String(change?.change||'')}::${String(change?.id||'')}`;}
  function getPath(obj,path){let cur=obj;for(const part of path||[]){if(!cur||typeof cur!=='object')return undefined;cur=cur[part];}return cur;}
  function ensurePath(obj,path){let cur=obj;for(let i=0;i<path.length-1;i++){const p=path[i];if(!cur[p]||typeof cur[p]!=='object')cur[p]={};cur=cur[p];}const last=path[path.length-1];if(!Array.isArray(cur[last]))cur[last]=[];return cur[last];}
  function allChanges(review){const out=[];(review?.categories||[]).forEach(category=>(category.changes||[]).forEach(change=>out.push({key:key(category.category,change),category:category.category,kind:category.kind||'content',change:change.change,id:String(change.id||''),label:String(change.label||''),fields:Array.isArray(change.fields)?change.fields.map(String):[]})));return out;}
  function buildPlan(review,selectedKeys,meta={}){
    if(!review||typeof review!=='object')throw new Error('A Change Review is required.');
    const wanted=new Set(Array.isArray(selectedKeys)?selectedKeys.map(String):[]);
    const selected=allChanges(review).filter(item=>wanted.has(item.key));
    return {schema:PLAN_SCHEMA,id:String(meta.id||''),createdAt:String(meta.createdAt||new Date().toISOString()),projectId:String(meta.projectId||review.projectId||''),projectTitle:String(meta.projectTitle||review.projectTitle||'Workspace project'),base:clone(meta.base||review.base||{}),target:clone(meta.target||review.target||{}),availableChangeCount:allChanges(review).length,selectedChangeCount:selected.length,selected,governance:{explicitSelectionRequired:true,automaticSelection:false,automaticMerge:false,automaticOverwrite:false,createsNewProjectCopy:true,preservesBothSourceStates:true}};
  }
  function applyOne(candidate,base,target,item){
    if(item.category==='Project metadata'){
      if(item.change!=='modified')return {ok:false,message:`Unsupported metadata operation: ${item.change}`};
      const field=item.id; if(!['title','description','status','pinned','notes','archivedAt'].includes(field))return {ok:false,message:`Unsupported project metadata field: ${field}`};
      candidate[field]=clone(target?.[field]??null);return {ok:true};
    }
    const path=CATEGORY_PATHS[item.category];if(!path)return {ok:false,message:`Unsupported reconciliation category: ${item.category}`};
    const baseList=Array.isArray(getPath(base,path))?getPath(base,path):[];
    const targetList=Array.isArray(getPath(target,path))?getPath(target,path):[];
    const list=ensurePath(candidate,path);const idx=list.findIndex(record=>String(record?.id||'')===item.id);
    if(item.change==='removed'){
      if(idx>=0)list.splice(idx,1);return {ok:true};
    }
    const source=targetList.find(record=>String(record?.id||'')===item.id);
    if(!source)return {ok:false,message:`Target record is unavailable for ${item.category}: ${item.label||item.id}`};
    if(idx>=0)list[idx]=clone(source);else list.push(clone(source));return {ok:true};
  }
  function ids(list){return new Set((Array.isArray(list)?list:[]).map(x=>String(x?.id||'')).filter(Boolean));}
  function missing(set,value){return Boolean(value)&&!set.has(String(value));}
  function validate(candidate){
    const blockers=[];
    const objectIds=ids(candidate?.objects), decisionIds=ids(candidate?.decision?.decisions), optionIds=ids(candidate?.decision?.options), criterionIds=ids(candidate?.decision?.criteria), boardIds=ids(candidate?.canvas?.boards), nodeIds=ids(candidate?.canvas?.nodes);
    const add=(category,id,message)=>blockers.push({category,id:String(id||''),message});
    (candidate?.research?.evidenceLinks||[]).forEach(x=>{if(missing(objectIds,x.evidenceObjectId)||missing(objectIds,x.sourceObjectId))add('Evidence links',x.id,'Evidence link references an object that is not present in the reconciled state.');});
    (candidate?.research?.claims||[]).forEach(x=>(x.evidenceObjectIds||[]).forEach(v=>{if(missing(objectIds,v))add('Research claims',x.id,'Claim references evidence that is not present in the reconciled state.');}));
    (candidate?.analysis?.assumptions||[]).forEach(x=>(x.evidenceObjectIds||[]).forEach(v=>{if(missing(objectIds,v))add('Analysis assumptions',x.id,'Assumption references evidence that is not present in the reconciled state.');}));
    (candidate?.analysis?.methods||[]).forEach(x=>{(x.datasetObjectIds||[]).forEach(v=>{if(missing(objectIds,v))add('Analysis methods',x.id,'Method references a dataset that is not present in the reconciled state.');});if(missing(objectIds,x.analysisObjectId))add('Analysis methods',x.id,'Method references an Analysis object that is not present in the reconciled state.');});
    (candidate?.analysis?.findings||[]).forEach(x=>{(x.evidenceObjectIds||[]).forEach(v=>{if(missing(objectIds,v))add('Analysis findings',x.id,'Finding references evidence that is not present in the reconciled state.');});if(missing(objectIds,x.analysisObjectId))add('Analysis findings',x.id,'Finding references an Analysis object that is not present in the reconciled state.');});
    (candidate?.decision?.decisions||[]).forEach(x=>{if(missing(objectIds,x.decisionObjectId))add('Decisions',x.id,'Decision references a canonical Decision object that is not present.');if(missing(optionIds,x.selectedOptionId))add('Decisions',x.id,'Decision references a selected option that is not present.');});
    (candidate?.decision?.options||[]).forEach(x=>{if(missing(decisionIds,x.decisionId))add('Decision options',x.id,'Option references a decision that is not present.');(x.evidenceObjectIds||[]).forEach(v=>{if(missing(objectIds,v))add('Decision options',x.id,'Option references evidence that is not present.');});(x.analysisObjectIds||[]).forEach(v=>{if(missing(objectIds,v))add('Decision options',x.id,'Option references analysis that is not present.');});});
    (candidate?.decision?.criteria||[]).forEach(x=>{if(missing(decisionIds,x.decisionId))add('Decision criteria',x.id,'Criterion references a decision that is not present.');});
    (candidate?.decision?.assessments||[]).forEach(x=>{if(missing(decisionIds,x.decisionId)||missing(optionIds,x.optionId)||missing(criterionIds,x.criterionId))add('Decision assessments',x.id,'Assessment references a missing decision, option, or criterion.');});
    (candidate?.decision?.risks||[]).forEach(x=>{if(missing(decisionIds,x.decisionId)||missing(optionIds,x.optionId))add('Decision risks',x.id,'Risk references a missing decision or option.');});
    (candidate?.traceability?.evidenceAssessments||[]).forEach(x=>{if(missing(objectIds,x.objectId))add('Evidence assessments',x.id,'Evidence assessment references an object that is not present.');});
    (candidate?.traceability?.lineage||[]).forEach(x=>{if(missing(objectIds,x.fromObjectId)||missing(objectIds,x.toObjectId))add('Traceability relationships',x.id,'Traceability relationship references an object that is not present.');});
    (candidate?.traceability?.reproducibility||[]).forEach(x=>{[x.analysisObjectId,...(x.datasetObjectIds||[]),...(x.evidenceObjectIds||[]),...(x.resultObjectIds||[])].filter(Boolean).forEach(v=>{if(missing(objectIds,v))add('Reproducibility records',x.id,'Reproducibility record references an object that is not present.');});});
    (candidate?.canvas?.nodes||[]).forEach(x=>{if(missing(boardIds,x.boardId))add('Canvas nodes',x.id,'Canvas node references a board that is not present.');if(missing(objectIds,x.objectId))add('Canvas nodes',x.id,'Canvas node references an object that is not present.');});
    (candidate?.canvas?.edges||[]).forEach(x=>{if(missing(boardIds,x.boardId)||missing(nodeIds,x.fromNodeId)||missing(nodeIds,x.toNodeId))add('Canvas relationships',x.id,'Canvas relationship references a missing board or node.');});
    (candidate?.briefing?.drafts||[]).forEach(x=>{[...(x.objectIds||[]),x.documentObjectId].filter(Boolean).forEach(v=>{if(missing(objectIds,v))add('Briefing drafts',x.id,'Briefing draft references an object that is not present.');});(x.sections||[]).forEach(section=>(section.objectIds||[]).forEach(v=>{if(missing(objectIds,v))add('Briefing drafts',x.id,'Briefing section references an object that is not present.');}));});
    const unique=[];const seen=new Set();blockers.forEach(item=>{const k=`${item.category}|${item.id}|${item.message}`;if(!seen.has(k)){seen.add(k);unique.push(item);}});return unique;
  }
  function applyPlan(base,target,plan){
    if(!base||!target||typeof base!=='object'||typeof target!=='object')throw new Error('Two source project states are required.');
    if(!plan||plan.schema!==PLAN_SCHEMA)throw new Error('A valid reconciliation plan is required.');
    if(!plan.selectedChangeCount)throw new Error('Select at least one change to reconcile.');
    const candidate=clone(base), errors=[];
    (plan.selected||[]).forEach(item=>{const result=applyOne(candidate,base,target,item);if(!result.ok)errors.push(result.message);});
    const blockers=validate(candidate);
    return {schema:SCHEMA,generatedAt:new Date().toISOString(),plan:clone(plan),candidate,appliedCount:(plan.selected||[]).length,errors,blockers,canCreate:errors.length===0&&blockers.length===0,governance:{sourceStatesMutated:false,automaticSelection:false,automaticMerge:false,automaticOverwrite:false,createsNewProjectCopy:true}};
  }
  return {SCHEMA,PLAN_SCHEMA,CATEGORY_PATHS,key,allChanges,buildPlan,applyPlan,validate};
});
