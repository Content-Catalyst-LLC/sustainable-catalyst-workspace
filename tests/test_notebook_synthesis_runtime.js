'use strict';
const assert=require('assert');
const nb=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v7.js');
let seq=0;const id=p=>`${p}-${++seq}`;const now=()=> '2026-08-09T21:45:00.000Z';
assert.strictEqual(nb.WORKSPACE_SCHEMA,'sc-workspace-notebook-workspace/7.0');
assert.strictEqual(nb.EXPORT_SCHEMA,'sc-workspace-notebook-export/7.0');
assert.strictEqual(nb.SYNTHESIS_SCHEMA,'sc-workspace-notebook-synthesis/1.0');
assert.deepStrictEqual(nb.SYNTHESIS_KINDS,['outline','citation-pack','source-matrix','evidence-summary','research-synthesis']);
const excerpt=nb.createBlock('excerpt',{title:'Measured result',content:'The measured result changed by ten units.',sourceTitle:'Study A',sourceUrl:'https://example.org/study-a',bibliography:{authors:['A. Researcher'],publisher:'Open Institute',publicationDate:'2026'}},id,now);
const note=nb.createBlock('note',{title:'Interpretation note',content:'Review the mechanism before drawing a conclusion.'},id,now);
const notebook=nb.notebook({id:'nb-1',title:'Field Notebook',sections:[{id:'sec-1',title:'Evidence',blocks:[excerpt,note]}]},id,now);
let ws=nb.workspace({schema:'sc-workspace-notebook-workspace/4.0',notebooks:[notebook],activeNotebookId:'nb-1',collections:[],links:[],promotions:[]},id,now);
assert.strictEqual(ws.schema,'sc-workspace-notebook-workspace/7.0');assert.deepStrictEqual(ws.syntheses,[]);
const refs=[nb.nodeRef({kind:'block',id:excerpt.id,notebookId:'nb-1',sectionId:'sec-1'}),nb.nodeRef({kind:'block',id:note.id,notebookId:'nb-1',sectionId:'sec-1'})];
for(const kind of nb.SYNTHESIS_KINDS){const syn=nb.generateSynthesis(kind,`Test ${kind}`,refs,ws,[],id,now);assert.strictEqual(syn.schema,nb.SYNTHESIS_SCHEMA);assert.strictEqual(syn.selectedRefs.length,2);assert.strictEqual(syn.citations.length,1);assert.ok(syn.content.includes('Test'));if(kind==='citation-pack')assert.ok(syn.content.includes('A. Researcher'));if(kind==='source-matrix')assert.ok(syn.content.includes('| # | Type | Material | Source | Excerpt |'));if(kind==='evidence-summary')assert.ok(syn.content.includes('does not infer evidentiary strength'));if(kind==='research-synthesis')assert.ok(syn.content.includes('no unstated conclusions or citations are generated'));}
const syn=nb.generateSynthesis('research-synthesis','Review draft',refs,ws,[],id,now);ws.syntheses.unshift(syn);assert.strictEqual(nb.synthesesForRef(ws,refs[0]).length,1);
const exp=nb.exportSynthesis(syn,{id:'p1',title:'Project'},'0.36.0',ws,[]);assert.strictEqual(exp.schema,'sc-workspace-notebook-synthesis-export/1.0');assert.strictEqual(exp.governance.citationGuessing,false);assert.strictEqual(exp.governance.explicitSelectionRequired,true);
const nbexp=nb.exportNotebook(ws.notebooks[0],{id:'p1',title:'Project'},'0.36.0',ws);assert.strictEqual(nbexp.schema,'sc-workspace-notebook-export/7.0');assert.strictEqual(nbexp.syntheses.length,1);assert.strictEqual(nbexp.governance.automaticSynthesis,false);
console.log('PASS - v0.36.0 notebook synthesis runtime');
