'use strict';
const assert=require('assert');
const api=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-long-session-performance-v1.js');
assert.strictEqual(api.SCHEMA,'sc-workspace-long-session-performance/1.0');
assert.strictEqual(api.BUDGETS.maxSamples,120);
let t=0;
const env={performance:{now:()=>t,memory:{usedJSHeapSize:20,totalJSHeapSize:30,jsHeapSizeLimit:100}},setTimeout:(fn)=>fn()};
const monitor=api.createSessionMonitor({env});
monitor.markRoute('start'); monitor.markRoute('start'); monitor.markRoute('projects');
for(let i=0;i<150;i++){t+=1;monitor.markRender(i%10===0?40:8,'render');}
for(let i=0;i<130;i++){t+=1;monitor.markIndex(i===129?300:20,'index',1000+i);}
monitor.markLongTask(60); monitor.markYield(4);
let s=monitor.summary();
assert.strictEqual(s.counters.routeTransitions,2);
assert.strictEqual(s.counters.renderCount,150); assert.strictEqual(s.counters.indexCount,130); assert.strictEqual(s.counters.longTaskCount,1); assert.strictEqual(s.counters.yieldCount,4);
assert.strictEqual(s.boundedSamples.render,120); assert.strictEqual(s.boundedSamples.index,120); assert.ok(s.findings.includes('render-attention')); assert.ok(s.findings.includes('index-attention')); assert.ok(s.findings.includes('long-task-observed'));
assert.strictEqual(s.memory.supported,true); assert.strictEqual(s.memory.ratio,.2);
const report=monitor.report('0.68.0');
assert.strictEqual(report.schema,'sc-workspace-performance-session-report/1.0'); assert.strictEqual(report.workspaceVersion,'0.68.0');
assert.strictEqual(report.privacy.projectContentIncluded,false); assert.strictEqual(report.privacy.automaticTelemetry,false); assert.strictEqual(report.privacy.persisted,false); assert.strictEqual(report.governance.canonicalMutation,false);
const memo=api.createRevisionMemo(x=>x.projects.map(p=>p.id));
const state={updatedAt:'a',projects:[{id:'p1',updatedAt:'a',objects:[],notebooks:{notebooks:[]}}]};
const a=memo.get(state),b=memo.get(state); assert.strictEqual(a,b); assert.deepStrictEqual(memo.stats().hits,1); state.projects[0].updatedAt='b'; memo.get(state); assert.deepStrictEqual(memo.stats().misses,2);
const largeList=new Array(50000).fill(0).map((_,i)=>i); const win=api.boundedWindow(largeList,120,120); assert.strictEqual(win.visible,120); assert.strictEqual(win.total,50000); assert.strictEqual(win.nextOffset,240); assert.strictEqual(win.hasMore,true); const capped=api.boundedWindow(largeList,0,50000); assert.strictEqual(capped.visible,api.BUDGETS.maxWindow);
(async()=>{const result=await api.chunkedMap([1,2,3,4,5,6,7],x=>x*2,{chunkSize:3,env});assert.deepStrictEqual(result.items,[2,4,6,8,10,12,14]);assert.strictEqual(result.yields,2);const largeResult=await api.chunkedMap(largeList.slice(0,5000),x=>x+1,{chunkSize:500,env});assert.strictEqual(largeResult.total,5000);assert.strictEqual(largeResult.yields,9);assert.strictEqual(largeResult.items[4999],5000);t+=api.BUDGETS.sessionAttentionMinutes*60000;s=monitor.summary();assert.ok(s.findings.includes('long-session'));monitor.reset();s=monitor.summary();assert.strictEqual(s.counters.renderCount,0);monitor.dispose();assert.strictEqual(monitor.isDisposed(),true);console.log('PASS - Workspace v0.68.0 long-session performance runtime');})().catch(err=>{console.error(err);process.exit(1);});
