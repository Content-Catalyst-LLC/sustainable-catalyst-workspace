'use strict';
const assert = require('assert');
const Capture = require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-source-capture-v1.js');
const Notebook = require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v2.js');

const memory = (() => {
  const data = new Map();
  return {getItem:k=>data.has(k)?data.get(k):null,setItem:(k,v)=>data.set(k,String(v)),removeItem:k=>data.delete(k)};
})();

const req = Capture.request({
  blockType:'excerpt',
  title:'Grid Reliability Finding',
  content:'A selected passage about reliability.',
  sourceTitle:'Reliability Assessment',
  sourceUrl:'https://example.org/report#page=12',
  sourceSurface:'knowledge-library',
  sourceId:'article-42',
  sourceKind:'article',
  selectionKind:'selected-text',
  authors:'A. Researcher; B. Analyst',
  publisher:'Example Institute',
  publicationDate:'2026',
  doi:'10.1000/example',
  locator:'p. 12',
  tags:'grid, reliability'
});
assert.equal(req.schema, Capture.REQUEST_SCHEMA);
assert.equal(req.capture.sourceSurface, 'knowledge-library');
assert.deepEqual(req.bibliography.authors, ['A. Researcher','B. Analyst']);
assert.equal(req.bibliography.doi, '10.1000/example');
assert.deepEqual(req.tags, ['grid','reliability']);

Capture.stage(req, memory);
const consumed = Capture.consumeStaged(memory);
assert.equal(consumed.length, 1);
assert.equal(consumed[0].id, req.id);
assert.equal(memory.getItem(Capture.SESSION_KEY), null);

let posted = null;
Capture.post(req, {postMessage:(data,origin)=>{posted={data,origin};}}, 'https://sustainablecatalyst.com');
assert.equal(posted.data.type, Capture.MESSAGE_TYPE);
assert.equal(posted.origin, 'https://sustainablecatalyst.com');
assert.equal(posted.data.payload.content, req.content);

const selected = Capture.fromPageSelection({
  selection:'Quoted research text',
  title:'External Research',
  sourceUrl:'https://example.org/paper#section-2',
  sourceSurface:'external-web'
});
assert.equal(selected.blockType, 'excerpt');
assert.equal(selected.sourceUrl, 'https://example.org/paper#section-2');
assert.equal(selected.capture.selectionKind, 'selected-text');

const block = Notebook.blockFromCapture(req, ()=>'block-1', ()=>'2026-08-09T23:30:00.000Z');
assert.equal(block.schema, Notebook.BLOCK_SCHEMA);
assert.equal(block.capture.sourceSurface, 'knowledge-library');
assert.equal(block.bibliography.publisher, 'Example Institute');
assert(Notebook.citationLine(block).includes('A. Researcher; B. Analyst'));
assert(Notebook.citationLine(block).includes('DOI 10.1000/example'));

const notebook = Notebook.createNotebook('Captured Research','',()=> 'notebook-1',()=> '2026-08-09T23:30:00.000Z');
notebook.sections[0].blocks.push(block);
const exported = Notebook.exportNotebook(notebook,{id:'project-1',title:'Project'},'0.33.0');
assert.equal(exported.schema, Notebook.EXPORT_SCHEMA);
assert.equal(exported.notebook.sections[0].blocks[0].capture.sourceSurface,'knowledge-library');
assert.equal(exported.governance.automaticMetadataFetch,false);
assert.equal(exported.governance.automaticAi,false);

console.log('PASS - Source Capture & Research Clipping runtime');
