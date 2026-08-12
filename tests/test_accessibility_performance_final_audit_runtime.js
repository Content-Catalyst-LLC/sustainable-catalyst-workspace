const assert=require('assert');
const A=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-performance-final-audit-v1.js');
function rootFixture({nodes=100,interactive=4,duplicate=false,unnamed=false}={}){
 const doc={documentElement:{getAttribute:(k)=>k==='lang'?'en-US':''},getElementById:()=>null,querySelector:()=>null};
 const controls=Array.from({length:interactive},(_,i)=>({hidden:false,disabled:false,tagName:'BUTTON',id:'',textContent:unnamed&&i===0?'':`Action ${i+1}`,getAttribute:()=>'',closest:()=>null}));
 const ids=duplicate?[{id:'dup'},{id:'dup'}]:[{id:'one'},{id:'two'}];
 return {ownerDocument:doc,querySelectorAll(sel){if(sel==='*')return Array.from({length:nodes},()=>({}));if(sel==='[id]')return ids;if(sel.includes('button,a[href],input:not'))return controls;if(sel.includes('button,a[href],input,select'))return controls;return [];}};
}
const readyEngine={audit(){return{findings:[{id:'skip-link',state:'ready',label:'Skip',detail:'ready'},{id:'screen-reader',state:'manual',label:'Screen reader',detail:'manual',manual:true}]}}};
const perf={render:{p95Ms:10},index:{p95Ms:40},counters:{longTaskCount:0},memory:{supported:false}};
let r=A.run(rootFixture(),{accessibilityEngine:readyEngine,performanceSummary:perf});
assert.equal(r.schema,A.SCHEMA);assert.equal(r.automatedReleaseGate,true);assert.equal(r.summary.blocked,0);assert(r.summary.manual>=2);assert.equal(r.governance.automatedCertification,false);assert.equal(r.governance.canonicalMutation,false);
let blocked=A.run(rootFixture(),{accessibilityEngine:{audit(){return{findings:[{id:'labels',state:'attention',label:'Labels',detail:'missing'}]}}},performanceSummary:perf});assert.equal(blocked.automatedReleaseGate,false);assert(blocked.findings.some(x=>x.id==='a11y-labels'&&x.state==='blocked'));
let slow=A.run(rootFixture(),{accessibilityEngine:readyEngine,performanceSummary:{render:{p95Ms:125},index:{p95Ms:30},counters:{longTaskCount:0},memory:{supported:true,ratio:.2}}});assert.equal(slow.automatedReleaseGate,false);assert(slow.findings.some(x=>x.id==='render-p95'&&x.state==='blocked'));
let huge=A.run(rootFixture({nodes:12000}),{accessibilityEngine:readyEngine,performanceSummary:perf});assert(huge.findings.some(x=>x.id==='dom-size'&&x.state==='blocked'));
let unnamed=A.run(rootFixture({unnamed:true}),{accessibilityEngine:readyEngine,performanceSummary:perf});assert(unnamed.findings.some(x=>x.id==='interactive-names'&&x.state==='blocked'));
const report=A.report('0.78.0',r);assert.equal(report.workspaceVersion,'0.78.0');assert.equal(report.privacy.projectContentIncluded,false);assert.equal(report.privacy.sourceUrlsIncluded,false);assert.equal(report.privacy.deviceIdentifierIncluded,false);assert.equal(report.governance.telemetry,false);
const checklist=A.checklist();assert.equal(checklist.schema,A.CHECKLIST_SCHEMA);assert(checklist.requiredManualChecks.length>=14);assert(checklist.requiredManualChecks.some(x=>x.id==='screen-reader-voiceover'));assert(checklist.requiredManualChecks.some(x=>x.id==='long-session-4h'));assert.equal(checklist.governance.automatedCertification,false);
const c=A.contract();assert.equal(c.governance.schemaMigrationRequired,false);assert.equal(c.governance.automaticOptimization,false);assert.equal(c.features.criticalAutomatedGate,true);
console.log('PASS - v0.78.0 Accessibility & Performance Final Audit runtime');
