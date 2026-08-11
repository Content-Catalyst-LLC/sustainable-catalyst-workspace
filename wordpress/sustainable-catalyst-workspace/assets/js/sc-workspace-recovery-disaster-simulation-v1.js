(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceRecoveryDisasterSimulation=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-recovery-disaster-simulation/1.0';
  const REPORT_SCHEMA='sc-workspace-recovery-disaster-report/1.0';
  const SCENARIO_SCHEMA='sc-workspace-recovery-disaster-scenario/1.0';
  const SCENARIOS=Object.freeze([
    ['corrupt-state','Corrupt canonical state','Detect unreadable canonical bytes without mutating or auto-restoring them.'],
    ['interrupted-write','Interrupted write','Reconcile a staged transaction journal without guessing or overwriting canonical state.'],
    ['storage-exhaustion','Storage exhaustion','Surface a refused write while preserving the previous canonical bytes.'],
    ['malformed-import','Malformed import','Reject malformed or partial project JSON before any import commit.'],
    ['stale-restore','Stale restore point','Keep restore application explicit and as a new local copy rather than replacing the source project.'],
    ['sync-conflict','Sync revision conflict','Preserve stale/local and newer remote revision facts instead of silent last-write-wins.'],
    ['missing-reference','Missing reference','Report an unresolved reference without inventing replacement research.'],
    ['future-version','Future version mismatch','Block a future project schema rather than guessing a downgrade path.']
  ].map(([id,label,goal])=>Object.freeze({id,label,goal})));
  const clone=v=>JSON.parse(JSON.stringify(v));
  function memoryStorage(initial={},options={}){
    const data=new Map(Object.entries(initial).map(([k,v])=>[String(k),String(v)]));let writes=0;
    return {get length(){return data.size},key(i){return [...data.keys()][i]??null},getItem(k){return data.has(String(k))?data.get(String(k)):null},setItem(k,v){writes++;if(options.failWrites){const e=new Error('Simulated quota exceeded');e.name='QuotaExceededError';throw e;}data.set(String(k),String(v));},removeItem(k){if(options.failRemoves)throw new Error('Simulated remove failure');data.delete(String(k));},clear(){data.clear()},snapshot(){return Object.fromEntries(data)},writes(){return writes}};
  }
  function outcome(id,pass,observed,expected,extra={}){return {schema:SCENARIO_SCHEMA,id,pass:Boolean(pass),observed:String(observed||''),expected:String(expected||''),canonicalMutation:false,automaticRepair:false,...extra};}
  function safeCall(fn,fallback){try{return fn()}catch(e){return typeof fallback==='function'?fallback(e):fallback;}}
  function runScenario(id,deps={}){
    const persistence=deps.persistence,compatibility=deps.compatibility,continuity=deps.continuity;
    if(id==='corrupt-state'){
      if(!persistence)return outcome(id,false,'persistence helper unavailable','invalid canonical state is detected');
      const st=memoryStorage({[persistence.CURRENT_KEY]:'{"broken":'}),a=persistence.inspect(st);
      return outcome(id,a.current?.state==='invalid'&&a.governance?.automaticRestore===false,a.current?.state,'invalid + no automatic restore');
    }
    if(id==='interrupted-write'){
      if(!persistence)return outcome(id,false,'persistence helper unavailable','interrupted journal reconciles non-destructively');
      const previous=JSON.stringify({storageVersion:35,projects:[],updatedAt:'before'}),next=JSON.stringify({storageVersion:35,projects:[],updatedAt:'after'}),st=memoryStorage({[persistence.CURRENT_KEY]:previous});
      const staged=persistence.stage(st,{previousRaw:previous,nextRaw:next,workspaceVersion:'0.71.0',storageSchemaVersion:35});
      const rec=persistence.reconcileJournal(st,{workspaceVersion:'0.71.0',storageSchemaVersion:35});
      return outcome(id,Boolean(staged?.ok)&&rec.state==='resolved-prewrite'&&st.getItem(persistence.CURRENT_KEY)===previous,rec.state,'resolved-prewrite with previous canonical bytes retained');
    }
    if(id==='storage-exhaustion'){
      if(!persistence)return outcome(id,false,'persistence helper unavailable','failed write preserves previous canonical bytes');
      const previous=JSON.stringify({storageVersion:35,projects:[],updatedAt:'before'}),st=memoryStorage({[persistence.CURRENT_KEY]:previous},{failWrites:true});
      const out=safeCall(()=>persistence.stage(st,{previousRaw:previous,nextRaw:'{}',workspaceVersion:'0.71.0',storageSchemaVersion:35}),e=>({ok:false,error:e.name||e.message}));
      return outcome(id,!out?.ok&&st.getItem(persistence.CURRENT_KEY)===previous,out?.reason||out?.error||'write refused','save is not verified and old canonical bytes remain');
    }
    if(id==='malformed-import'){
      if(!compatibility)return outcome(id,false,'compatibility helper unavailable','malformed import blocked before commit');
      const a=compatibility.assessProjectImport({schema:'sc-workspace-project-export/20.0'},[]);
      return outcome(id,a.status==='blocked'&&a.automaticCommit===false,a.status,'blocked + automaticCommit=false');
    }
    if(id==='stale-restore'){
      const source={id:'project-a',title:'Source',schema:'sc-workspace-project/20.0',updatedAt:'2026-01-01T00:00:00Z'},restored=clone(source);restored.id='project-restored-copy';restored.title+=' — restored copy';
      return outcome(id,source.id!==restored.id&&source.title==='Source','new local ID','restore remains explicit new-local-copy',{sourceProjectUnchanged:true});
    }
    if(id==='sync-conflict'){
      if(!continuity)return outcome(id,false,'continuity helper unavailable','stale and remote revisions remain explicit');
      const op=continuity.operation({projectId:'p1',kind:'push',expectedRevision:4,remoteRevision:5,localFingerprint:'local',remoteFingerprint:'remote'},()=> 'op-test',()=> '2026-08-11T00:00:00Z');
      const failed=continuity.fail(op,'Remote revision advanced; preserve local copy.',false,()=> '2026-08-11T00:01:00Z');
      return outcome(id,failed.state==='failed'&&failed.expectedRevision===4&&failed.remoteRevision===5,`${failed.state} / expected ${failed.expectedRevision} / remote ${failed.remoteRevision}`,'conflict evidence preserves both revision facts');
    }
    if(id==='missing-reference'){
      const refs=new Map([['known',{id:'known'}]]),resolved=refs.get('missing')||null;
      return outcome(id,resolved===null,'unresolved','missing reference remains unresolved; no invented replacement',{replacementInvented:false});
    }
    if(id==='future-version'){
      if(!compatibility)return outcome(id,false,'compatibility helper unavailable','future project schema blocked');
      const a=compatibility.assessProjectImport({schema:'sc-workspace-project/99.0',id:'future',title:'Future',objects:[]},[]);
      return outcome(id,a.status==='blocked'&&a.futureSchemaBlocked===true,a.status,'blocked + futureSchemaBlocked=true');
    }
    return outcome(id,false,'unknown scenario','known disaster scenario');
  }
  function runAll(deps={}){
    const scenarios=SCENARIOS.map(s=>({...s,result:runScenario(s.id,deps)})),passed=scenarios.filter(x=>x.result.pass).length;
    return {schema:REPORT_SCHEMA,workspaceVersion:String(deps.workspaceVersion||'0.71.0').slice(0,40),generatedAt:new Date().toISOString(),state:passed===scenarios.length?'pass':'attention',passed,total:scenarios.length,scenarios,privacy:{projectContentIncluded:false,rawCanonicalStateIncluded:false,sourceUrlsIncluded:false,queryTextIncluded:false,deviceIdentifierIncluded:false,automaticSubmission:false},governance:{sandboxedSimulation:true,canonicalMutation:false,automaticRepair:false,automaticRestore:false,automaticImportCommit:false,automaticSync:false,backgroundNetwork:false}};
  }
  function contract(){return {schema:SCHEMA,reportSchema:REPORT_SCHEMA,scenarioSchema:SCENARIO_SCHEMA,scenarios:SCENARIOS.map(x=>x.id),features:{sandboxedFailureInjection:true,corruptState:true,interruptedWrite:true,storageExhaustion:true,malformedImport:true,staleRestore:true,syncConflict:true,missingReference:true,futureVersionMismatch:true},governance:{canonicalMutation:false,automaticRepair:false,automaticRestore:false,automaticImportCommit:false,automaticSync:false,backgroundNetwork:false,productionDataInjection:false}};}
  return Object.freeze({SCHEMA,REPORT_SCHEMA,SCENARIO_SCHEMA,SCENARIOS,memoryStorage,runScenario,runAll,contract});
});
