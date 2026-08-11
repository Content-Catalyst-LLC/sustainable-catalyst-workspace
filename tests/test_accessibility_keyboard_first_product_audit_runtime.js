'use strict';
const assert=require('assert');
const A=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-v1.js');
assert.strictEqual(A.SCHEMA,'sc-workspace-accessibility/1.0');
assert.strictEqual(A.REPORT_SCHEMA,'sc-workspace-accessibility-report/1.0');
assert.strictEqual(A.CHECKLIST_SCHEMA,'sc-workspace-accessibility-checklist/1.0');
assert.strictEqual(A.TARGET,'WCAG 2.2 AA');
assert.strictEqual(A.nextIndex(4,0,'ArrowRight'),1);assert.strictEqual(A.nextIndex(4,3,'ArrowRight'),0);assert.strictEqual(A.nextIndex(4,0,'ArrowLeft'),3);assert.strictEqual(A.nextIndex(4,2,'Home'),0);assert.strictEqual(A.nextIndex(4,1,'End'),3);
const doc={querySelector(sel){if(sel==='meta[name="viewport"]')return{getAttribute(){return 'width=device-width, initial-scale=1';}};return null;}};
assert.strictEqual(A.viewportAllowsZoom(doc).state,'ready');
const blocked={querySelector(){return{getAttribute(){return 'width=device-width,user-scalable=no';}};}};assert.strictEqual(A.viewportAllowsZoom(blocked).state,'attention');
const env={matchMedia(q){return{matches:q.includes('prefers-reduced-motion')};}};assert.strictEqual(A.reducedMotion(env),true);assert.strictEqual(A.forcedColors(env),false);
const check=A.checklist();assert.strictEqual(check.schema,A.CHECKLIST_SCHEMA);assert.ok(check.requiredManualChecks.length>=10);assert.strictEqual(check.governance.automaticCertification,false);
const result={schema:A.SCHEMA,summary:{ready:3,attention:0,manual:2,total:5},findings:[]};const report=A.report('0.64.0',result);assert.strictEqual(report.workspaceVersion,'0.64.0');assert.strictEqual(report.privacy.projectContentIncluded,false);assert.strictEqual(report.privacy.rawUserAgentIncluded,false);assert.strictEqual(report.governance.automatedCertification,false);
// Focus containment wraps at both ends.
function item(name){return{name,hidden:false,disabled:false,closest(){return null;},matches(){return true;},focus(){focusState=this;}};}let focusState=null;const a=item('a'),b=item('b');const fakeDoc={activeElement:b};const dialog={ownerDocument:fakeDoc,hidden:false,getAttribute(){return null;},querySelectorAll(){return[a,b];},hasAttribute(){return true;},contains(x){return x===a||x===b;}};let prevented=false;A.containTab(dialog,{shiftKey:false,preventDefault(){prevented=true;}});assert.strictEqual(prevented,true);assert.strictEqual(focusState,a);fakeDoc.activeElement=a;prevented=false;A.containTab(dialog,{shiftKey:true,preventDefault(){prevented=true;}});assert.strictEqual(prevented,true);assert.strictEqual(focusState,b);
console.log('PASS - Workspace v0.64.0 Accessibility & Keyboard-First Product Audit runtime');
