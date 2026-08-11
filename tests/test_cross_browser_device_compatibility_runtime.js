'use strict';
const assert=require('assert');
const C=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-browser-compatibility-v1.js');
class Store{constructor(){this.m=new Map();}getItem(k){return this.m.has(k)?this.m.get(k):null;}setItem(k,v){this.m.set(k,String(v));}removeItem(k){this.m.delete(k);}}
function docMock(){
  const clicked=[];
  return {clicked,body:{appendChild(a){a._attached=true;}},createElement(tag){assert.strictEqual(tag,'a');return {href:'',download:'',rel:'',click(){clicked.push(this.href);},remove(){this._attached=false;}};},documentElement:{clientWidth:1200,clientHeight:800}};
}
function baseEnv(){
  const document=docMock();
  const env={document,innerWidth:1200,innerHeight:800,localStorage:new Store(),sessionStorage:new Store(),navigator:{userAgent:'Mozilla/5.0 Chrome/140.0 Safari/537.36',platform:'MacIntel',maxTouchPoints:0,onLine:true,language:'en-US'},history:{state:{},pushState(){this.pushed=true;},replaceState(){this.replaced=true;}},File:function(){},FileReader:function(){},Blob:global.Blob,URL:{createObjectURL(){return 'blob:compat';},revokeObjectURL(){}},setTimeout(fn){fn();},addEventListener(){},removeEventListener(){},self:null,top:null,crypto:global.crypto||{},CSS:{supports(){return true;}},PointerEvent:function(){}};
  env.self=env;env.top=env;env.File.prototype={text(){}};
  return env;
}
assert.strictEqual(C.SCHEMA,'sc-workspace-browser-compatibility/1.0');
assert.strictEqual(C.MATRIX_SCHEMA,'sc-workspace-browser-compatibility-matrix/1.0');
assert.strictEqual(C.REPORT_SCHEMA,'sc-workspace-browser-compatibility-report/1.0');
// Modern path.
const modern=baseEnv();let caps=C.capability(modern);assert.strictEqual(caps.storage.local.writable,true);assert.strictEqual(caps.import.mode,'file-text');assert.strictEqual(caps.export.mode,'object-url');assert.strictEqual(caps.navigation.mode,'history-api');assert.strictEqual(caps.viewport.deviceClass,'desktop');
let matrix=C.assess(caps);assert.strictEqual(matrix.state,'ready');assert.strictEqual(matrix.governance.userAgentGating,false);
// FileReader fallback path.
const fallback=baseEnv();fallback.File.prototype={};fallback.FileReader=function(){this.readAsText=()=>{this.result='reader-value';this.onload();};};
caps=C.capability(fallback);assert.strictEqual(caps.import.mode,'file-reader');
// Sandboxed/blocked storage getters are treated as unavailable rather than crashing compatibility detection.
const blockedStorage=baseEnv();Object.defineProperty(blockedStorage,'localStorage',{get(){throw new Error('SecurityError');}});caps=C.capability(blockedStorage);assert.strictEqual(caps.storage.local.writable,false);assert.strictEqual(caps.storage.local.reason,'unavailable');
C.readFileText({name:'x'},fallback).then(v=>assert.strictEqual(v,'reader-value'));
// Native file.text path.
C.readFileText({text:()=>Promise.resolve('native-value')},modern).then(v=>assert.strictEqual(v,'native-value'));
// History API failure does not throw.
const badHistory=baseEnv();badHistory.history.pushState=()=>{throw new Error('blocked');};const hist=C.safeHistory(badHistory,'push',{x:1});assert.strictEqual(hist.ok,false);assert.strictEqual(hist.mode,'in-app-only');
// Object URL export.
let out=C.downloadText('a.txt','hello','text/plain',modern);assert.strictEqual(out.ok,true);assert.strictEqual(out.mode,'object-url');assert.strictEqual(modern.document.clicked.length,1);
// Bounded data URI fallback.
const dataUri=baseEnv();dataUri.URL={};out=C.downloadText('b.txt','small','text/plain',dataUri);assert.strictEqual(out.ok,true);assert.strictEqual(out.mode,'data-uri-fallback');
out=C.downloadText('big.txt','x'.repeat(C.MAX_DATA_URI_BYTES+1),'text/plain',dataUri);assert.strictEqual(out.ok,false);assert.strictEqual(out.reason,'no-download-path-for-payload-size');
// Browser labels are diagnostic, not feature gates.
assert.strictEqual(C.browserFamily('Mozilla/5.0 Version/18.0 Safari/605.1.15'),'Safari');assert.strictEqual(C.browserFamily('Mozilla/5.0 Edg/140.0'),'Edge');assert.strictEqual(C.platformFamily({userAgent:'',platform:'Win32',maxTouchPoints:0}),'Windows');
// Privacy-minimized report and explicit manual-QA target matrix.
const report=C.report('0.64.0',C.capability(modern),C.assess(C.capability(modern)));assert.strictEqual(report.privacy.rawUserAgentIncluded,false);assert.strictEqual(report.privacy.deviceIdentifierIncluded,false);assert.strictEqual(report.governance.userAgentUsedForDisplayLabelOnly,true);
const targets=C.targetMatrix();assert.strictEqual(targets.schema,C.TARGET_SCHEMA);assert.ok(targets.browserFamilies.includes('Safari / WebKit'));assert.ok(targets.claimBoundary.includes('do not replace manual browser/device QA'));
console.log('PASS - Workspace v0.64.0 Accessibility & Keyboard-First Product Audit runtime');
