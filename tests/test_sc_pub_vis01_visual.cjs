'use strict';
// SC-PUB-VIS-01 isolated visual editor tests; no application server required.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');

const target=path.resolve(__dirname,'../backend/app/reporting_publication_visual.js');
const source=fs.readFileSync(target,'utf8');
new vm.Script(source,{filename:'reporting_publication_visual.js'});

function mockElement(){
 return {
  value:'',hidden:false,attributes:{},onclick:null,children:[],
  setAttribute(k,v){this.attributes[k]=v},
  replaceChildren(...items){this.children=items},
  append(v){this.children.push(v)},
 };
}
const nodes=new Map();
const document={
 getElementById(id){if(!nodes.has(id))nodes.set(id,mockElement());return nodes.get(id)},
 createElement(){return mockElement()},
};
const ctx={document,E:(id)=>document.getElementById(id),markDirty(){},preview:async()=>({}),
 status(){},setTimeout,clearTimeout,console};
vm.createContext(ctx);
vm.runInContext(source+'\nglobalThis.__api={parseVisualParts,classifyVisual,blockMarkdown,renderVisualBlocks,setEditorMode};',ctx);
const {parseVisualParts,classifyVisual,blockMarkdown,renderVisualBlocks,setEditorMode}=ctx.__api;

const text='# Wexford ERW\n\nEvidence [@beerling2020] remains source text.\n\n$$\n\nCO_2 + basalt\n\n$$\n\n![Verified figure](asset:fig01)\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n';
const parsed=parseVisualParts(text);
assert.equal(parsed.prefix+parsed.parts.map(p=>p.raw+p.sep).join(''),text);
assert.equal(parsed.parts[0].raw,'# Wexford ERW\n');
assert.equal(classifyVisual(parsed.parts[0].raw).type,'heading1');
assert.equal(classifyVisual(parsed.parts[1].raw).type,'paragraph');
assert.equal(classifyVisual(parsed.parts[2].raw).type,'technical');
assert.equal(classifyVisual(parsed.parts[3].raw).type,'technical');
assert.equal(classifyVisual(parsed.parts[4].raw).type,'technical');
assert.equal(blockMarkdown('heading2','Methods','# Old heading\n'),'## Methods\n');
assert.equal(blockMarkdown('list','First\nSecond','- Original\n'),'- First\n- Second\n');

document.getElementById('manuscript').value=text;
setEditorMode('visual');
assert.equal(document.getElementById('manuscript').hidden,true);
assert.equal(document.getElementById('visualBlocks').children.length,5);
// Viewing / switching modes must not change source Markdown.
setEditorMode('source');
assert.equal(document.getElementById('manuscript').value,text);
assert.equal(document.getElementById('manuscript').hidden,false);

const runtime=fs.readFileSync(path.resolve(__dirname,'../backend/app/reporting_publication_ui.js'),'utf8');
const ui=fs.readFileSync(path.resolve(__dirname,'../backend/app/reporting_publication_ui.html'),'utf8');
assert.match(runtime,/publicationType:E\('publicationType'\)\.value/);
assert.match(ui,/id="visualBlocks"/);
assert.match(ui,/id="publicationType"/);
assert.match(ui,/id="html"/);
assert.match(ui,/id="pdf"/);
assert.match(ui,/id="docx"/);
console.log('SC-PUB-VIS-01: visual authoring/source preservation/export wiring PASS');
