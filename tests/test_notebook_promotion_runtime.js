'use strict';
const assert = require('assert');
const nb = require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v4.js');

let seq = 0;
const id = prefix => `${prefix}-${++seq}`;
const now = () => '2026-08-09T21:30:00.000Z';

assert.strictEqual(nb.WORKSPACE_SCHEMA, 'sc-workspace-notebook-workspace/4.0');
assert.strictEqual(nb.NOTEBOOK_SCHEMA, 'sc-workspace-notebook/3.0');
assert.strictEqual(nb.BLOCK_SCHEMA, 'sc-workspace-notebook-block/3.0');
assert.strictEqual(nb.EXPORT_SCHEMA, 'sc-workspace-notebook-export/4.0');
assert.strictEqual(nb.PROMOTION_SCHEMA, 'sc-workspace-notebook-promotion/1.0');
assert.deepStrictEqual(nb.PROMOTABLE_TYPES, ['source','evidence','dataset','analysis','decision','document','canvas']);

const excerpt = nb.createBlock('excerpt', {title:'Observed change', content:'Measured change in the source.', tags:['evidence']}, id, now);
const question = nb.createBlock('question', {title:'What changed?', content:'Compare the alternatives.'}, id, now);
const note = nb.createBlock('note', {title:'Working synthesis', content:'Draft synthesis.'}, id, now);
assert.deepStrictEqual(nb.promotionDestinations('excerpt'), nb.PROMOTABLE_TYPES);
assert.deepStrictEqual(nb.promotionDestinations('divider'), []);
assert.strictEqual(nb.suggestedPromotionType('excerpt'), 'evidence');
assert.strictEqual(nb.suggestedPromotionType('question'), 'analysis');
assert.strictEqual(nb.suggestedPromotionType('note'), 'document');
assert.strictEqual(nb.canvasNodeType('question'), 'question');

const notebook = nb.notebook({
  id:'nb-1', title:'Field Notebook',
  sections:[{id:'sec-1', title:'Evidence', blocks:[excerpt, question, note]}]
}, id, now);
let ws = nb.workspace({notebooks:[notebook], activeNotebookId:'nb-1', collections:[], links:[]}, id, now);
const sourceRef = {schema:nb.REF_SCHEMA, kind:'block', id:excerpt.id, notebookId:'nb-1', sectionId:'sec-1', label:excerpt.title};
const p1 = nb.createPromotion(sourceRef, 'evidence', 'object', 'obj-evidence-1', 'Observed change', id, now);
const p2 = nb.createPromotion(sourceRef, 'canvas', 'canvas-node', 'canvas-node-1', 'Observed change', id, now);
assert.ok(p1 && p2);
ws.promotions.push(p1, p2);
assert.strictEqual(nb.promotionsForRef(ws, sourceRef).length, 2);
assert.strictEqual(nb.promotionsForRef(ws, sourceRef)[0].targetType, 'evidence');
assert.strictEqual(nb.promotionsForRef(ws, sourceRef)[1].targetType, 'canvas');

const exported = nb.exportNotebook(ws.notebooks[0], {id:'project-1', title:'Research Project'}, ws, '0.35.0');
// Correct call signature is (notebook, project, workspaceVersion, notebookWorkspace).
const portable = nb.exportNotebook(ws.notebooks[0], {id:'project-1', title:'Research Project'}, '0.35.0', ws);
assert.strictEqual(portable.schema, 'sc-workspace-notebook-export/4.0');
assert.strictEqual(portable.promotions.length, 2);
assert.strictEqual(portable.governance.automaticPromotion, false);
assert.strictEqual(portable.governance.promotionRequiresExplicitDestination, true);
assert.strictEqual(portable.governance.originalNotebookMaterialPreserved, true);
assert.strictEqual(portable.notebook.sections[0].blocks[0].content, 'Measured change in the source.');

const migrated = nb.workspace({
  schema:'sc-workspace-notebook-workspace/3.0',
  notebooks:[{schema:'sc-workspace-notebook/2.0', id:'legacy', title:'Legacy', sections:[{id:'s',title:'Notes',blocks:[{schema:'sc-workspace-notebook-block/2.0',id:'b',type:'excerpt',title:'Legacy excerpt',content:'Preserve me',promotion:{status:'promoted',targetKind:'object',targetId:'old-object',promotedAt:now()}}]}]}],
  collections:[], links:[]
}, id, now);
assert.strictEqual(migrated.schema, 'sc-workspace-notebook-workspace/4.0');
assert.deepStrictEqual(migrated.promotions, []);
assert.strictEqual(migrated.notebooks[0].sections[0].blocks[0].content, 'Preserve me');
assert.strictEqual(migrated.notebooks[0].sections[0].blocks[0].promotion.status, 'promoted');

console.log('PASS - v0.35.0 notebook promotion runtime');
