(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceScalePerformance=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-scale-performance/1.0';
  const PROFILE_SCHEMA='sc-workspace-scale-profile/1.0';
  const BUDGET_SCHEMA='sc-workspace-performance-budget/1.0';
  const BUDGETS=Object.freeze({
    workspaceBytesAttention:16*1024*1024,
    workspaceBytesCritical:32*1024*1024,
    projectsAttention:120,
    objectsAttention:12000,
    notebooksAttention:600,
    notebookBlocksAttention:20000,
    integratedEntriesAttention:30000,
    renderWindow:120,
    maxRenderWindow:600
  });
  const text=v=>String(v==null?'':v);
  const bytes=v=>{try{return typeof TextEncoder!=='undefined'?new TextEncoder().encode(text(v)).length:unescape(encodeURIComponent(text(v))).length;}catch(_){return text(v).length;}};
  function counts(state){
    const projects=Array.isArray(state&&state.projects)?state.projects:[];let objects=0,notebooks=0,notebookSections=0,notebookBlocks=0,researchQuestions=0,researchClaims=0;
    projects.forEach(p=>{
      objects+=(Array.isArray(p&&p.objects)?p.objects:[]).length;
      const ns=p&&p.notebooks&&Array.isArray(p.notebooks.notebooks)?p.notebooks.notebooks:[];notebooks+=ns.length;
      ns.forEach(n=>{const sections=Array.isArray(n&&n.sections)?n.sections:[];notebookSections+=sections.length;sections.forEach(s=>{notebookBlocks+=(Array.isArray(s&&s.blocks)?s.blocks:[]).length;});});
      const r=p&&p.research&&typeof p.research==='object'?p.research:{};researchQuestions+=(Array.isArray(r.questions)?r.questions:[]).length;researchClaims+=(Array.isArray(r.claims)?r.claims:[]).length;
    });
    return {projects:projects.length,activeProjects:projects.filter(p=>!p.archivedAt).length,objects,notebooks,notebookSections,notebookBlocks,researchQuestions,researchClaims};
  }
  function signature(state){
    const projects=Array.isArray(state&&state.projects)?state.projects:[];
    return projects.map(p=>[p.id,p.updatedAt,p.archivedAt||'',Array.isArray(p.objects)?p.objects.length:0,p.notebooks&&Array.isArray(p.notebooks.notebooks)?p.notebooks.notebooks.length:0]).flat().join('|');
  }
  let cache={signature:'',entries:null,hits:0,misses:0};
  function deriveIntegrated(state,integratedApi){
    if(!integratedApi||typeof integratedApi.derive!=='function')return[];
    const sig=signature(state);
    if(cache.entries&&cache.signature===sig){cache.hits++;return cache.entries;}
    const entries=integratedApi.derive(state);cache={signature:sig,entries,hits:cache.hits,misses:cache.misses+1};return entries;
  }
  function cacheStats(){return {hits:cache.hits,misses:cache.misses,entries:Array.isArray(cache.entries)?cache.entries.length:0};}
  function clearCache(){cache={signature:'',entries:null,hits:0,misses:0};}
  function windowed(items,limit=BUDGETS.renderWindow){const list=Array.isArray(items)?items:[],size=Math.max(1,Math.min(BUDGETS.maxRenderWindow,Number(limit)||BUDGETS.renderWindow));return {items:list.slice(0,size),visible:Math.min(list.length,size),total:list.length,hasMore:list.length>size,nextLimit:Math.min(BUDGETS.maxRenderWindow,size+BUDGETS.renderWindow)};}
  function pressure(rawBytes,quotaBytes=0){const used=Math.max(0,Number(rawBytes)||0),quota=Math.max(0,Number(quotaBytes)||0),ratio=quota?used/quota:0;const level=used>=BUDGETS.workspaceBytesCritical||ratio>=0.8?'critical':used>=BUDGETS.workspaceBytesAttention||ratio>=0.6?'attention':'normal';return {level,workspaceBytes:used,quotaBytes:quota,quotaRatio:ratio};}
  function profile(state,options={}){
    const c=counts(state),raw=options.raw!=null?text(options.raw):JSON.stringify(state||{}),integratedEntries=Math.max(0,Number(options.integratedEntries)||0),p=pressure(bytes(raw),options.quotaBytes);
    const attention=[];if(c.projects>BUDGETS.projectsAttention)attention.push('project-count');if(c.objects>BUDGETS.objectsAttention)attention.push('object-count');if(c.notebooks>BUDGETS.notebooksAttention)attention.push('notebook-count');if(c.notebookBlocks>BUDGETS.notebookBlocksAttention)attention.push('notebook-block-count');if(integratedEntries>BUDGETS.integratedEntriesAttention)attention.push('integrated-index-size');if(p.level!=='normal')attention.push(`storage-${p.level}`);
    return {schema:PROFILE_SCHEMA,generatedAt:new Date().toISOString(),counts:c,integratedEntries,storage:p,renderWindow:BUDGETS.renderWindow,attention,status:attention.some(x=>x==='storage-critical')?'critical':attention.length?'attention':'ready',governance:{advisoryOnly:true,automaticDeletion:false,automaticCompaction:false,automaticArchive:false,automaticMigration:false,canonicalMutation:false}};
  }
  function stressFixture(options={}){
    const projectCount=Math.max(1,Math.min(250,Number(options.projects)||20)),objectsPerProject=Math.max(0,Math.min(500,Number(options.objectsPerProject)||80)),notebooksPerProject=Math.max(0,Math.min(20,Number(options.notebooksPerProject)||4)),blocksPerNotebook=Math.max(0,Math.min(250,Number(options.blocksPerNotebook)||40));
    const projects=[];for(let p=0;p<projectCount;p++){const objects=[];for(let o=0;o<objectsPerProject;o++)objects.push({id:`o-${p}-${o}`,type:o%3===0?'source':o%3===1?'evidence':'document',title:`Object ${p}-${o}`,summary:'Synthetic scale fixture',content:'x'.repeat(64),tags:['stress'],updatedAt:'2026-08-10T00:00:00.000Z'});const notebooks=[];for(let n=0;n<notebooksPerProject;n++){const blocks=[];for(let b=0;b<blocksPerNotebook;b++)blocks.push({id:`b-${p}-${n}-${b}`,type:'note',title:`Block ${b}`,content:'Synthetic notebook block',updatedAt:'2026-08-10T00:00:00.000Z'});notebooks.push({id:`n-${p}-${n}`,title:`Notebook ${n}`,description:'Synthetic',sections:[{id:`s-${p}-${n}`,title:'Section',blocks}],updatedAt:'2026-08-10T00:00:00.000Z'});}projects.push({id:`p-${p}`,title:`Project ${p}`,objects,research:{questions:[],claims:[]},notebooks:{notebooks},updatedAt:'2026-08-10T00:00:00.000Z'});}return {projects};
  }
  function contract(){return {schema:SCHEMA,budgetSchema:BUDGET_SCHEMA,budgets:{...BUDGETS},features:{derivedIndexCache:true,boundedRenderWindows:true,storagePressureVisibility:true,largeProjectStressFixtures:true,schemaStable:true},governance:{advisoryOnly:true,noAutomaticDeletion:true,noAutomaticCompaction:true,noAutomaticArchival:true,noAutomaticMigration:true}};}
  return {SCHEMA,PROFILE_SCHEMA,BUDGET_SCHEMA,BUDGETS,bytes,counts,signature,deriveIntegrated,cacheStats,clearCache,windowed,pressure,profile,stressFixture,contract};
});
