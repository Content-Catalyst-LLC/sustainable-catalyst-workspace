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
  value:'',hidden:false,disabled:false,attributes:{},onclick:null,
  setAttribute(k,v){this.attributes[k]=v},
  setSelectionRange(start,end){this.selectionStart=start;this.selectionEnd=end},
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
vm.runInContext(source+'\nglobalThis.__test={setEditorMode,prepareSourceInsertion};',ctx);
const manuscript=E('manuscript');
const original='## Wexford Results\n\n$$\nCO_2 + basalt\n$$\n';
manuscript.value=original;
assert.equal(E('visualMode').disabled,true);
assert.equal(manuscript.hidden,false);
assert.equal(window.SCStudioRegisterTiptap instanceof Function,true);
window.SCStudioRegisterTiptap({
 render(){renders++},destroy(){destroys++}
});
assert.equal(E('visualMode').disabled,false);
assert.equal(manuscript.hidden,true);
assert.equal(renders,1);
ctx.__test.prepareSourceInsertion();
assert.equal(manuscript.hidden,false);
assert.equal(manuscript.value,original);
assert.equal(manuscript.selectionStart,original.length);
assert.equal(destroys,1);
E('addHeading').onclick();
assert.match(manuscript.value,/## New section/);
assert.equal(dirty,1);

const ui=fs.readFileSync(path.resolve(__dirname,'../backend/app/reporting_publication_ui.html'),'utf8');
const controller=fs.readFileSync(path.resolve(__dirname,'../backend/app/reporting_publication_ui.js'),'utf8');
assert.match(controller,/publicationType:E\('publicationType'\)\.value/);
for(const id of ['visualBlocks','publicationType','html','pdf','docx'])
 assert.ok(ui.includes('id="'+id+'"'),id);
console.log('SC-PUB-TIPTAP-01: editor adapter and existing Workspace export wiring PASS');
