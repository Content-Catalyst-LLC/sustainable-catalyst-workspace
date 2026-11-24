'use strict';
// SC-PUB-TIPTAP-01 adapter test (offline); Tiptap source model has its own
// independent Node test suite in backend/reporting_tiptap/tests.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');

const source=fs.readFileSync(path.resolve(__dirname,'../backend/app/reporting_publication_visual.js'),'utf8');
new vm.Script(source,{filename:'reporting_publication_visual.js'});
function mockElement(){
 return {
  value:'',hidden:false,disabled:false,attributes:{},onclick:null,listeners:{},selectionStart:0,selectionEnd:0,
  setAttribute(k,v){this.attributes[k]=v},
  setSelectionRange(start,end){this.selectionStart=start;this.selectionEnd=end},
  setRangeText(text,start,end){this.value=this.value.slice(0,start)+text+this.value.slice(end);this.selectionStart=this.selectionEnd=start+text.length},
  addEventListener(type,fn){(this.listeners[type]=this.listeners[type]||[]).push(fn)},
  fire(type){for(const fn of this.listeners[type]||[])fn()},
  focus(){},
 };
}
const elements=new Map();
const E=id=>{
 if(!elements.has(id))elements.set(id,mockElement());
 return elements.get(id);
};
let dirty=0, previews=0, renders=0, destroys=0;
const window={};
const ctx={E,window,status(){},markDirty(){dirty++},preview:async()=>{previews++}};
vm.createContext(ctx);
vm.runInContext(source+'\nglobalThis.__test={setEditorMode};',ctx);
const manuscript=E('manuscript');
const original='## Wexford Results\n\n$$\nCO_2 + basalt\n$$\n';
manuscript.value=original;
assert.equal(E('visualMode').disabled,true);
assert.equal(manuscript.hidden,false);
assert.equal(typeof window.SCStudioRegisterTiptap,'function');
window.SCStudioRegisterTiptap({
 render(){renders++},destroy(){destroys++}
});
assert.equal(E('visualMode').disabled,false);
assert.equal(manuscript.hidden,true);
assert.equal(renders,1);
// SC-FIG-PLACE-01: without a cursor the researcher placed, nothing is inserted (no append at the end).
E('addHeading').onclick();
assert.equal(manuscript.hidden,false,'falls back to Markdown source when the visual editor cannot insert');
assert.equal(destroys,1);
assert.equal(manuscript.value,original,'unknown position: manuscript unchanged');
assert.equal(dirty,0);
// The researcher puts the cursor inside the heading: the block goes after it, never inside the equation.
manuscript.setSelectionRange(5,5);manuscript.fire('keyup');
E('addHeading').onclick();
assert.equal(manuscript.value,'## Wexford Results\n\n## New section\n\n$$\nCO_2 + basalt\n$$\n');
assert.equal(dirty,1);
// A cursor from before a programmatic change is not reused.
manuscript.value=original;
E('addParagraph').onclick();
assert.equal(manuscript.value,original);
assert.equal(dirty,1);

const ui=fs.readFileSync(path.resolve(__dirname,'../backend/app/reporting_publication_ui.html'),'utf8');
const controller=fs.readFileSync(path.resolve(__dirname,'../backend/app/reporting_publication_ui.js'),'utf8');
assert.match(controller,/publicationType:E\('publicationType'\)\.value/);
for(const id of ['visualBlocks','publicationType','html','pdf','docx'])
 assert.ok(ui.includes('id="'+id+'"'),id);
console.log('SC-PUB-TIPTAP-01: editor adapter and existing Workspace export wiring PASS');
