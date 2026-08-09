(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.SCWorkspaceResearchNotebook=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const WORKSPACE_SCHEMA='sc-workspace-notebook-workspace/1.0';
  const NOTEBOOK_SCHEMA='sc-workspace-notebook/1.0';
  const BLOCK_SCHEMA='sc-workspace-notebook-block/1.0';
  const EXPORT_SCHEMA='sc-workspace-notebook-export/1.0';
  const BLOCK_TYPES=new Set(['note','source','excerpt','question','claim','reference','checklist','divider','attachment']);
  const PROMOTION_KINDS=new Set(['','object','research-question','research-claim']);
  const MAX_NOTEBOOKS=30,MAX_SECTIONS=40,MAX_BLOCKS_PER_NOTEBOOK=300,MAX_BLOCKS_PER_PROJECT=600;
  const LIMITS={notebooksPerProject:MAX_NOTEBOOKS,sectionsPerNotebook:MAX_SECTIONS,blocksPerNotebook:MAX_BLOCKS_PER_NOTEBOOK,blocksPerProject:MAX_BLOCKS_PER_PROJECT};
  const iso=()=>new Date().toISOString();
  const rid=(prefix)=>`${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,9)}`;
  const text=(v,n)=>String(v??'').trim().slice(0,n);
  const tags=(v)=>{const src=Array.isArray(v)?v:String(v||'').split(',');const out=[],seen=new Set();for(const raw of src){const t=text(raw,48),k=t.toLowerCase();if(t&&!seen.has(k)&&out.length<20){seen.add(k);out.push(t);}}return out;};
  const validIso=(v)=>typeof v==='string'&&!Number.isNaN(Date.parse(v));
  function promotion(raw){const v=raw&&typeof raw==='object'?raw:{};const kind=PROMOTION_KINDS.has(v.targetKind)?v.targetKind:'';return {status:v.status==='promoted'?'promoted':'none',targetKind:kind,targetId:text(v.targetId,160),promotedAt:validIso(v.promotedAt)?v.promotedAt:null};}
  function block(raw,idFactory=rid,now=iso){const v=raw&&typeof raw==='object'?raw:{};const type=BLOCK_TYPES.has(v.type)?v.type:'note';const stamp=now();return {schema:BLOCK_SCHEMA,id:text(v.id||idFactory('nbb'),160),type,title:text(v.title,240),content:String(v.content??'').slice(0,50000),sourceObjectId:text(v.sourceObjectId,160),sourceTitle:text(v.sourceTitle,240),sourceUrl:String(v.sourceUrl??'').trim().slice(0,2000),referenceObjectId:text(v.referenceObjectId,160),tags:tags(v.tags),promotion:promotion(v.promotion),createdAt:validIso(v.createdAt)?v.createdAt:stamp,updatedAt:validIso(v.updatedAt)?v.updatedAt:stamp};}
  function section(raw,idFactory=rid,now=iso){const v=raw&&typeof raw==='object'?raw:{};const stamp=now();return {id:text(v.id||idFactory('nbs'),160),title:text(v.title||'Notes',160)||'Notes',blocks:(Array.isArray(v.blocks)?v.blocks:[]).map(x=>block(x,idFactory,now)).slice(0,MAX_BLOCKS_PER_NOTEBOOK),createdAt:validIso(v.createdAt)?v.createdAt:stamp,updatedAt:validIso(v.updatedAt)?v.updatedAt:stamp};}
  function notebook(raw,idFactory=rid,now=iso){const v=raw&&typeof raw==='object'?raw:{};const stamp=now();let sections=(Array.isArray(v.sections)?v.sections:[]).map(x=>section(x,idFactory,now)).slice(0,MAX_SECTIONS);if(!sections.length)sections=[section({title:'Notes'},idFactory,now)];const active=sections.some(s=>s.id===v.activeSectionId)?v.activeSectionId:sections[0].id;return {schema:NOTEBOOK_SCHEMA,id:text(v.id||idFactory('nb'),160),title:text(v.title||'Research Notebook',160)||'Research Notebook',description:String(v.description??'').trim().slice(0,1200),sections,activeSectionId:active,createdAt:validIso(v.createdAt)?v.createdAt:stamp,updatedAt:validIso(v.updatedAt)?v.updatedAt:stamp};}
  function workspace(raw,idFactory=rid,now=iso){const v=raw&&typeof raw==='object'?raw:{};let notebooks=(Array.isArray(v.notebooks)?v.notebooks:[]).map(x=>notebook(x,idFactory,now)).slice(0,MAX_NOTEBOOKS);const total=()=>notebooks.reduce((sum,n)=>sum+n.sections.reduce((s,sec)=>s+sec.blocks.length,0),0);while(total()>MAX_BLOCKS_PER_PROJECT){for(let i=notebooks.length-1;i>=0&&total()>MAX_BLOCKS_PER_PROJECT;i--){for(let j=notebooks[i].sections.length-1;j>=0&&total()>MAX_BLOCKS_PER_PROJECT;j--){notebooks[i].sections[j].blocks.pop();}}}const active=notebooks.some(n=>n.id===v.activeNotebookId)?v.activeNotebookId:(notebooks[0]?.id||null);return {schema:WORKSPACE_SCHEMA,notebooks,activeNotebookId:active,createdAt:validIso(v.createdAt)?v.createdAt:now(),updatedAt:validIso(v.updatedAt)?v.updatedAt:now()};}
  function createNotebook(title='Research Notebook',description='',idFactory=rid,now=iso){return notebook({title,description},idFactory,now);}
  function createSection(title='Notes',idFactory=rid,now=iso){return section({title},idFactory,now);}
  function createBlock(type='note',values={},idFactory=rid,now=iso){return block({...values,type},idFactory,now);}
  function move(list,index,delta){if(!Array.isArray(list))return false;const to=index+delta;if(index<0||index>=list.length||to<0||to>=list.length)return false;const [item]=list.splice(index,1);list.splice(to,0,item);return true;}
  function blockCount(ws){return workspace(ws).notebooks.reduce((sum,n)=>sum+n.sections.reduce((s,sec)=>s+sec.blocks.length,0),0);}
  function promotionTarget(type){switch(type){case 'source':case 'excerpt':case 'note':case 'checklist':case 'attachment':return 'object';case 'question':return 'research-question';case 'claim':return 'research-claim';default:return '';}}
  function promotionObjectType(type){switch(type){case 'source':case 'attachment':return 'source';case 'excerpt':return 'evidence';case 'note':case 'checklist':return 'document';default:return '';}}
  function exportNotebook(nb,project,workspaceVersion){const n=notebook(nb);return {schema:EXPORT_SCHEMA,workspaceVersion:String(workspaceVersion||''),exportedAt:iso(),project:{id:text(project?.id,160),title:text(project?.title,200)},notebook:n,governance:{automaticPromotion:false,automaticAi:false,sourceProjectMutation:false}};}
  return {WORKSPACE_SCHEMA,NOTEBOOK_SCHEMA,BLOCK_SCHEMA,EXPORT_SCHEMA,BLOCK_TYPES:Array.from(BLOCK_TYPES),LIMITS,MAX_NOTEBOOKS,MAX_SECTIONS,MAX_BLOCKS_PER_NOTEBOOK,MAX_BLOCKS_PER_PROJECT,workspace,notebook,section,block,createNotebook,createSection,createBlock,move,blockCount,promotionTarget,promotionObjectType,exportNotebook};
});
