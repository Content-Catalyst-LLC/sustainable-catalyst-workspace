const assert=require('assert');
const S=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-knowledge-search-v1.js');
const C=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-collections-v1.js');
assert.equal(C.COLLECTION_SCHEMA,'sc-workspace-research-collection/1.0');
assert.equal(C.VIEW_SCHEMA,'sc-workspace-research-view/1.0');
const entries=[
 {key:'object:p1:s1',kind:'object',subtype:'source',projectId:'p1',projectTitle:'Energy',projectArchived:false,id:'s1',title:'Grid source',summary:'Transmission source',content:'grid',tags:['grid'],updatedAt:'2026-08-10T01:00:00Z',origin:'Personal Knowledge / Workspace Object',provenance:{sourceTitle:'NERC',sourceUrl:'https://example.test/nerc'}},
 {key:'object:p1:e1',kind:'object',subtype:'evidence',projectId:'p1',projectTitle:'Energy',projectArchived:false,id:'e1',title:'Grid evidence',summary:'Evidence',content:'reliability',tags:['grid'],updatedAt:'2026-08-10T02:00:00Z',origin:'Personal Knowledge / Workspace Object',provenance:{sourceTitle:'NERC',sourceUrl:'https://example.test/nerc'}},
 {key:'object:p1:d1',kind:'object',subtype:'decision',projectId:'p1',projectTitle:'Energy',projectArchived:false,id:'d1',title:'Grid decision',summary:'Decision',content:'choose',tags:['grid'],updatedAt:'2026-08-10T03:00:00Z',origin:'Personal Knowledge / Workspace Object',provenance:{}},
 {key:'notebook:p2:n1',kind:'notebook',subtype:'notebook',projectId:'p2',projectTitle:'Climate',projectArchived:false,id:'n1',title:'Heat notebook',summary:'Heat',content:'',tags:['heat'],updatedAt:'2026-08-09T03:00:00Z',origin:'Research Notebook',provenance:{}}
];
const state={projects:[{id:'p1',notebooks:{links:[],promotions:[]},research:{evidenceLinks:[],claims:[]}},{id:'p2',notebooks:{links:[],promotions:[]},research:{evidenceLinks:[],claims:[]}}]};
const collection=C.smartCollection({name:'Grid evidence',criteria:{query:'grid',kind:'object',subtype:'evidence',project:'p1'}},()=> 'rc1',S);
assert.equal(collection.id,'rc1');assert.equal(collection.criteria.subtype,'evidence');
let rows=C.evaluate(entries,collection,state,S);assert.equal(rows.length,1);assert.equal(rows[0].entry.id,'e1');
const sourceCriteria=C.builtinCriteria('sources',{project:'p1',scope:'active'},S);assert.equal(sourceCriteria.project,'p1');assert.equal(sourceCriteria.subtype,'source');
rows=S.search(entries,sourceCriteria,state);assert.equal(rows.length,1);assert.equal(rows[0].entry.id,'s1');
const view=C.researchView({name:'By project',criteria:{scope:'active'},presentation:{groupBy:'project',density:'compact',limit:50}},()=> 'rv1',S);assert.equal(view.presentation.groupBy,'project');assert.equal(view.presentation.density,'compact');
const grouped=C.group(S.search(entries,{scope:'active',sort:'updated-desc'},state),'project');assert.equal(grouped.length,2);assert(grouped.some(g=>g.label==='Energy'&&g.rows.length===3));
const dash=C.dashboard(entries,state,S,{project:'p1',scope:'active'});assert.deepEqual({sources:dash.sources,evidence:dash.evidence,decisions:dash.decisions,projects:dash.projects,records:dash.records},{sources:1,evidence:1,decisions:1,projects:1,records:3});assert.equal(dash.documented,2);
assert.equal(C.normalizeCollections([collection],S).length,1);assert.equal(C.normalizeViews([view],S).length,1);assert(C.BUILTINS.some(v=>v.id==='documented'));
console.log('PASS - v0.43.0 Research Collections & Dynamic Views runtime');
