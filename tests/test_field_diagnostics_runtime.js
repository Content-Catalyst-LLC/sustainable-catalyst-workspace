'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');
const src=fs.readFileSync(path.join(__dirname,'../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-diagnostics-v1.js'),'utf8');
let tick=0;
const memory={
  sc_workspace:JSON.stringify({projects:[{id:'p1',objects:[{id:'o1'}]}]}),
  sc_workspace_last_good_v1:JSON.stringify({schema:'sc-workspace-last-known-good/1.0',raw:'{"ok":true}'})
};
const localStorage={getItem:k=>Object.prototype.hasOwnProperty.call(memory,k)?memory[k]:null,setItem:(k,v)=>{memory[k]=String(v)},removeItem:k=>{delete memory[k]}};
const env={
  localStorage,sessionStorage:{},File:function(){},FileReader:function(){},Blob:function(){},postMessage(){},isSecureContext:true,
  matchMedia:q=>({matches:q.includes('reduced-motion')}),location:{pathname:'/platform/',search:'?secret=1',hash:'#x'},document:{readyState:'complete'},
  navigator:{onLine:true},crypto:{subtle:{digest(){}}},performance:{now:()=>++tick,getEntriesByType:()=>[{name:'/wp-content/plugins/sustainable-catalyst-workspace/a.js',duration:12.4}]}
};
env.window=env;
const sandbox={console,globalThis:{},TextEncoder,Date};
sandbox.globalThis=sandbox; sandbox.window=env; sandbox.navigator=env.navigator; sandbox.crypto=env.crypto; sandbox.performance=env.performance; sandbox.TextEncoder=TextEncoder;
vm.createContext(sandbox); vm.runInContext(src,sandbox);
const h=sandbox.SCWorkspaceFieldDiagnostics;
assert(h,'helper exported');
assert.strictEqual(h.FIELD_SCHEMA,'sc-workspace-field-diagnostic/1.0');
const root={dataset:{version:'0.33.0',storageVersion:'27',projectSchema:'sc-workspace-project/12.0',releaseStage:'public-beta'},querySelectorAll:()=>new Array(42)};
const diag=h.diagnostic(root,env);
assert.strictEqual(diag.deployment.workspaceVersion,'0.33.0');
assert.strictEqual(diag.deployment.path,'/platform/');
assert.strictEqual(diag.counts.projects,1); assert.strictEqual(diag.counts.objects,1);
assert.strictEqual(diag.recovery.lastKnownGoodSnapshotAvailable,true);
assert.strictEqual(diag.privacy.projectContentIncluded,false); assert.strictEqual(diag.privacy.deviceIdentifierIncluded,false); assert.strictEqual(diag.privacy.queryStringIncluded,false);
assert.ok(!JSON.stringify(diag).includes('secret=1'));
const report=h.issueReport(diag,{type:'performance',impact:'blocks-task',observed:'Slow save',expected:'Fast save',steps:'Create project',reviewed:true});
assert.strictEqual(report.schema,'sc-workspace-field-report/1.0'); assert.strictEqual(report.governance.automaticSubmission,false); assert.strictEqual(report.issue.observed,'Slow save');
assert.ok(h.supportSummary(report).includes('Slow save'));
console.log('PASS - Workspace v0.31.0 field diagnostics runtime');
