const assert=require('assert');
const S=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-knowledge-search-v1.js');
assert.equal(S.SCHEMA,'sc-workspace-knowledge-search/1.0');
assert.equal(S.SAVED_SEARCH_SCHEMA,'sc-workspace-saved-search/1.0');
const entries=[
 {key:'object:p1:o1',kind:'object',subtype:'evidence',projectId:'p1',projectTitle:'Energy',projectArchived:false,id:'o1',title:'Grid resilience evidence',summary:'Transmission redundancy',content:'N-1 reliability planning',tags:['grid','reliability'],updatedAt:'2026-08-09T12:00:00Z',origin:'Personal Knowledge / Workspace Object',provenance:{sourceTitle:'NERC report',sourceUrl:'https://example.test/nerc'}},
 {key:'object:p1:o2',kind:'object',subtype:'source',projectId:'p1',projectTitle:'Energy',projectArchived:false,id:'o2',title:'Transmission source',summary:'A source about the grid',content:'grid planning',tags:['grid'],updatedAt:'2026-08-08T12:00:00Z',origin:'Personal Knowledge / Workspace Object',provenance:{sourceTitle:'NERC report',sourceUrl:'https://example.test/nerc'}},
 {key:'notebook-block:p2:n1:b1',kind:'notebook-block',subtype:'note',projectId:'p2',projectTitle:'Climate',projectArchived:false,id:'b1',title:'Heat note',summary:'Urban heat',content:'cooling access',tags:['heat'],updatedAt:'2026-08-07T12:00:00Z',origin:'Research Notebook',notebookId:'n1',sectionId:'s1',provenance:{}}
];
const state={projects:[{id:'p1',notebooks:{links:[],promotions:[]},research:{evidenceLinks:[{id:'el1',sourceObjectId:'o2',evidenceObjectId:'o1'}],claims:[]}},{id:'p2',notebooks:{links:[],promotions:[]},research:{evidenceLinks:[],claims:[]}}]};
let p=S.normalizePrefs({query:'"grid resilience"',kind:'object',provenance:'documented',sort:'relevance'});
assert.equal(p.schema,S.SCHEMA);assert.equal(p.kind,'object');assert.deepEqual(S.tokenize(p.query),['grid resilience']);
let rows=S.search(entries,p,state);assert.equal(rows.length,1);assert.equal(rows[0].entry.id,'o1');assert(rows[0].rank.score>0);assert(rows[0].rank.reasons.some(x=>x.includes('title matches')));
p=S.normalizePrefs({query:'grid',project:'all',sort:'relevance'});rows=S.search(entries,p,state);assert.equal(rows.length,2);assert.equal(rows[0].entry.id,'o1');
const facts=S.provenanceFacts(entries[0],state);assert.equal(facts.documented,true);assert.equal(facts.linked,true);
const related=S.related(entries[0],entries,state);assert(related.some(x=>x.entry.id==='o2'));assert(related.some(x=>x.reason==='same recorded source'||x.reason==='evidence relationship'));
const saved=S.savedSearch({name:'Grid evidence',preferences:p,createdAt:'2026-08-09T00:00:00Z',updatedAt:'2026-08-09T00:00:00Z'},()=> 'ss1');assert.equal(saved.id,'ss1');assert.equal(saved.preferences.schema,S.SCHEMA);assert.equal(S.normalizeSavedSearches([saved]).length,1);
const facets=S.facets(entries);assert(facets.kinds.includes('object'));assert(facets.subtypes.includes('evidence'));assert(facets.origins.includes('Research Notebook'));
console.log('PASS - v0.42.0 Knowledge Search & Advanced Retrieval runtime');
