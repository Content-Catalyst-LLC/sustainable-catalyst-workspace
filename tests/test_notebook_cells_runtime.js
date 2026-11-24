'use strict';
// SC-NB-01: the editor helper preserves executable cells verbatim and emits schema-complete notebooks.
const assert = require('assert');
const nb = require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js');
let n = 0;
const id = prefix => `${prefix}-${++n}`;
const now = () => '2026-11-10T00:00:00.000Z';

const cells = [
  {id:'fit', type:'code', language:'r', source:'fit <- lm(y ~ x, data = rows)',
   execution:{operation:'workspace.polyglot.r.linear-model', modelRef:{modelId:'m-r'},
              payload:{datasetInput:{datasetId:'ds', datasetRevision:1}, outcome:'y', predictors:['x']}}},
  {id:'scenario', type:'decision-studio', source:'',
   execution:{operation:'workspace.decision.minimax-regret', dependsOnCellIds:['fit'],
              payload:{upstreamInput:{cells:[{cellId:'fit', role:'primary'}], transform:{kind:'linear-scenario-scores', rates:[10]}}}}},
];

const out = nb.notebook({title:'Executable', cells}, id, now);
assert.strictEqual(out.schema, 'sc-workspace-notebook/3.0');
assert.deepStrictEqual(out.cells, cells, 'cells are preserved verbatim');
assert.notStrictEqual(out.cells, cells, 'cells are copied, not aliased');
for (const key of ['id','title','description','sections','activeSectionId','createdAt','updatedAt']) assert.ok(key in out, key);

// Round trip through the workspace normaliser keeps cells; notebooks without cells gain no field.
const ws = nb.workspace({notebooks:[out], activeNotebookId:out.id}, id, now);
assert.deepStrictEqual(ws.notebooks[0].cells, cells);
assert.ok(!('cells' in nb.notebook({title:'Plain'}, id, now)));
assert.ok(!('cells' in nb.createNotebook('Plain', '', id, now)));
console.log('notebook cells runtime: ok');
