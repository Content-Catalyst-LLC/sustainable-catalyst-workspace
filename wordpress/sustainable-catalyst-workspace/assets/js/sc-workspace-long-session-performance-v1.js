(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceLongSessionPerformance=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-long-session-performance/1.0';
  const SESSION_SCHEMA='sc-workspace-performance-session/1.0';
  const REPORT_SCHEMA='sc-workspace-performance-session-report/1.0';
  const BUDGETS=Object.freeze({
    maxSamples:120,
    longTaskMs:50,
    renderAttentionMs:32,
    renderCriticalMs:100,
    indexAttentionMs:250,
    indexCriticalMs:1000,
    routeTransitionsAttention:300,
    sessionAttentionMinutes:240,
    heapAttentionRatio:0.72,
    defaultChunkSize:250,
    maxChunkSize:2000,
    defaultWindow:120,
    maxWindow:600
  });
  const finite=v=>Number.isFinite(Number(v))?Number(v):0;
  const clamp=(v,min,max)=>Math.max(min,Math.min(max,finite(v)));
  const stamp=()=>new Date().toISOString();
  const clock=env=>{try{return typeof env?.performance?.now==='function'?()=>env.performance.now():()=>Date.now();}catch(_){return()=>Date.now();}};
  function boundedPush(list,item,max=BUDGETS.maxSamples){list.push(item);if(list.length>max)list.splice(0,list.length-max);return list;}
  function average(list){return list.length?list.reduce((n,v)=>n+finite(v),0)/list.length:0;}
  function percentile(list,p=0.95){if(!list.length)return 0;const a=list.map(finite).sort((x,y)=>x-y),i=Math.min(a.length-1,Math.max(0,Math.ceil(a.length*clamp(p,0,1))-1));return a[i];}
  function revisionSignature(state){
    const projects=Array.isArray(state&&state.projects)?state.projects:[];
    return [state&&state.updatedAt||'',projects.length,...projects.flatMap(p=>[p&&p.id||'',p&&p.updatedAt||'',p&&p.archivedAt||'',Array.isArray(p&&p.objects)?p.objects.length:0,p&&p.notebooks&&Array.isArray(p.notebooks.notebooks)?p.notebooks.notebooks.length:0])].join('|');
  }
  function createRevisionMemo(compute,signatureFn=revisionSignature){
    let sig=null,value,has=false,hits=0,misses=0;
    return Object.freeze({
      get(input){const next=signatureFn(input);if(has&&next===sig){hits++;return value;}value=compute(input);sig=next;has=true;misses++;return value;},
      clear(){sig=null;value=undefined;has=false;},
      stats(){return {hits,misses,hasValue:has,signature:sig||''};}
    });
  }
  function boundedWindow(items,offset=0,limit=BUDGETS.defaultWindow){
    const list=Array.isArray(items)?items:[],start=Math.max(0,Math.floor(finite(offset))),size=Math.max(1,Math.min(BUDGETS.maxWindow,Math.floor(finite(limit)||BUDGETS.defaultWindow))),end=Math.min(list.length,start+size);
    return {items:list.slice(start,end),offset:start,visible:end-start,total:list.length,hasPrevious:start>0,hasMore:end<list.length,nextOffset:end,previousOffset:Math.max(0,start-size),limit:size};
  }
  function cooperativeYield(env=globalThis){
    const win=env&&env.window||env;
    return new Promise(resolve=>{try{if(typeof win.requestIdleCallback==='function'){win.requestIdleCallback(()=>resolve(),{timeout:50});return;}if(typeof win.requestAnimationFrame==='function'){win.requestAnimationFrame(()=>resolve());return;}win.setTimeout(resolve,0);}catch(_){setTimeout(resolve,0);}});
  }
  async function chunkedMap(items,mapper,options={}){
    const list=Array.isArray(items)?items:[],chunk=Math.max(1,Math.min(BUDGETS.maxChunkSize,Math.floor(finite(options.chunkSize)||BUDGETS.defaultChunkSize))),out=[];let yields=0;
    for(let i=0;i<list.length;i++){out.push(await mapper(list[i],i));if(i+1<list.length&&(i+1)%chunk===0){yields++;await cooperativeYield(options.env||globalThis);}}
    return {items:out,yields,chunkSize:chunk,total:list.length};
  }
  function memorySnapshot(env=globalThis){
    try{const m=env?.performance?.memory;if(!m)return {supported:false};const used=finite(m.usedJSHeapSize),limit=finite(m.jsHeapSizeLimit),total=finite(m.totalJSHeapSize);return {supported:Boolean(limit),usedJSHeapSize:used,totalJSHeapSize:total,jsHeapSizeLimit:limit,ratio:limit?used/limit:0};}catch(_){return {supported:false};}
  }
  function createSessionMonitor(options={}){
    const env=options.env||globalThis,now=clock(env),started=now(),startedAt=stamp();
    let disposed=false,lastRoute='',routeTransitions=0,renderCount=0,indexCount=0,longTaskCount=0,yieldCount=0,observer=null;
    const renderSamples=[],indexSamples=[],longTaskSamples=[],routeSamples=[];
    function markRoute(route){if(disposed)return;const next=String(route||'');if(next&&next!==lastRoute){routeTransitions++;lastRoute=next;boundedPush(routeSamples,{at:now(),route:next});}}
    function markRender(duration,label='workspace'){if(disposed)return;const ms=Math.max(0,finite(duration));renderCount++;boundedPush(renderSamples,{ms,label:String(label||'workspace').slice(0,80),at:now()});}
    function markIndex(duration,label='derived-index',entries=0){if(disposed)return;const ms=Math.max(0,finite(duration));indexCount++;boundedPush(indexSamples,{ms,label:String(label||'derived-index').slice(0,80),entries:Math.max(0,Math.floor(finite(entries))),at:now()});}
    function markYield(count=1){if(!disposed)yieldCount+=Math.max(0,Math.floor(finite(count)||0));}
    function markLongTask(duration){if(disposed)return;const ms=Math.max(0,finite(duration));if(ms<BUDGETS.longTaskMs)return;longTaskCount++;boundedPush(longTaskSamples,{ms,at:now()});}
    function startLongTaskObserver(){if(disposed||observer)return false;try{const P=env.PerformanceObserver;if(typeof P!=='function')return false;const supported=Array.isArray(P.supportedEntryTypes)&&P.supportedEntryTypes.includes('longtask');if(!supported)return false;observer=new P(list=>{for(const e of list.getEntries())markLongTask(e.duration);});observer.observe({entryTypes:['longtask']});return true;}catch(_){observer=null;return false;}}
    function summary(){
      const ageMs=Math.max(0,now()-started),renders=renderSamples.map(x=>x.ms),indexes=indexSamples.map(x=>x.ms),longs=longTaskSamples.map(x=>x.ms),memory=memorySnapshot(env),findings=[];
      const maxRender=renders.length?Math.max(...renders):0,maxIndex=indexes.length?Math.max(...indexes):0;
      if(maxRender>=BUDGETS.renderCriticalMs)findings.push('render-critical');else if(maxRender>=BUDGETS.renderAttentionMs)findings.push('render-attention');
      if(maxIndex>=BUDGETS.indexCriticalMs)findings.push('index-critical');else if(maxIndex>=BUDGETS.indexAttentionMs)findings.push('index-attention');
      if(longTaskCount)findings.push('long-task-observed');
      if(routeTransitions>=BUDGETS.routeTransitionsAttention)findings.push('route-transition-volume');
      if(ageMs>=BUDGETS.sessionAttentionMinutes*60000)findings.push('long-session');
      if(memory.supported&&memory.ratio>=BUDGETS.heapAttentionRatio)findings.push('heap-pressure');
      const state=findings.some(x=>x.endsWith('critical')||x==='heap-pressure')?'critical':findings.length?'attention':'ready';
      return {schema:SESSION_SCHEMA,generatedAt:stamp(),startedAt,ageMs,state,findings,counters:{routeTransitions,renderCount,indexCount,longTaskCount,yieldCount},render:{samples:renders.length,averageMs:average(renders),p95Ms:percentile(renders,.95),maxMs:maxRender},index:{samples:indexes.length,averageMs:average(indexes),p95Ms:percentile(indexes,.95),maxMs:maxIndex,lastEntries:indexSamples.length?indexSamples[indexSamples.length-1].entries:0},longTasks:{samples:longs.length,p95Ms:percentile(longs,.95),maxMs:longs.length?Math.max(...longs):0},memory,boundedSamples:{max:BUDGETS.maxSamples,render:renderSamples.length,index:indexSamples.length,longTask:longTaskSamples.length,route:routeSamples.length}};
    }
    function report(workspaceVersion=''){return {schema:REPORT_SCHEMA,workspaceVersion:String(workspaceVersion||'').slice(0,40),generatedAt:stamp(),session:summary(),privacy:{projectContentIncluded:false,objectContentIncluded:false,sourceUrlsIncluded:false,queryTextIncluded:false,deviceIdentifierIncluded:false,automaticTelemetry:false,automaticSubmission:false,persisted:false},governance:{advisoryOnly:true,canonicalMutation:false,automaticDeletion:false,automaticCompaction:false,automaticArchival:false,automaticMigration:false,backgroundProfilingUpload:false}};}
    function reset(){routeTransitions=0;renderCount=0;indexCount=0;longTaskCount=0;yieldCount=0;lastRoute='';renderSamples.length=indexSamples.length=longTaskSamples.length=routeSamples.length=0;}
    function dispose(){disposed=true;try{observer?.disconnect?.();}catch(_){}observer=null;renderSamples.length=indexSamples.length=longTaskSamples.length=routeSamples.length=0;}
    return Object.freeze({markRoute,markRender,markIndex,markYield,markLongTask,startLongTaskObserver,summary,report,reset,dispose,isDisposed:()=>disposed});
  }
  function contract(){return {schema:SCHEMA,sessionSchema:SESSION_SCHEMA,reportSchema:REPORT_SCHEMA,budgets:{...BUDGETS},features:{boundedInMemorySampling:true,longTaskObserverOptional:true,revisionMemoization:true,cooperativeChunkYield:true,boundedWindows:true,sessionReportExport:true},governance:{advisoryOnly:true,canonicalMutation:false,automaticDeletion:false,automaticCompaction:false,automaticArchival:false,automaticMigration:false,automaticTelemetry:false,persistentProfiling:false}};}
  return Object.freeze({SCHEMA,SESSION_SCHEMA,REPORT_SCHEMA,BUDGETS,boundedPush,average,percentile,revisionSignature,createRevisionMemo,boundedWindow,cooperativeYield,chunkedMap,memorySnapshot,createSessionMonitor,contract});
});
