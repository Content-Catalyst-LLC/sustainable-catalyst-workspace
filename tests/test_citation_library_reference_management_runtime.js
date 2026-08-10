const assert=require('assert');
const R=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-reference-library-v1.js');
assert.equal(R.REFERENCE_SCHEMA,'sc-workspace-reference/1.0');
assert.equal(R.LIBRARY_SCHEMA,'sc-workspace-reference-library/1.0');
assert.equal(R.PREFERENCES_SCHEMA,'sc-workspace-citation-preferences/1.0');
assert.equal(R.EXPORT_SCHEMA,'sc-workspace-reference-library-export/1.0');
const a=R.normalizeReference({title:'Grid Reliability',authors:'Jane Smith; John Doe',publicationDate:'2025-04-01',doi:'https://doi.org/10.1000/ABC',containerTitle:'Energy Journal',tags:['grid']},()=> 'r1');
const b=R.normalizeReference({title:'Grid Reliability',authors:['Jane Smith'],publicationDate:'2025',doi:'doi:10.1000/abc'},()=> 'r2');
assert.equal(a.doi,'10.1000/abc');assert.equal(R.fingerprint(a),'doi:10.1000/abc');assert.equal(R.fingerprint(b),'doi:10.1000/abc');
assert.equal(R.duplicateGroups([a,b]).length,1);
a.citationKey=R.uniqueCitationKey(a,[]);assert.equal(a.citationKey,'smith2025grid');b.citationKey=R.uniqueCitationKey(b,[a]);assert.equal(b.citationKey,'smith2025grid2');
for(const style of ['apa7','chicago-author-date','mla9','ieee']){const text=R.format(a,style,1);assert(text.includes('Grid Reliability'));}
const entry={key:'object:p1:s1',kind:'object',subtype:'source',projectId:'p1',id:'s1',title:'Fallback title',tags:['grid'],provenance:{sourceTitle:'Recorded Source',sourceUrl:'https://example.test/source',bibliography:{authors:['A. Author'],publicationDate:'2024',containerTitle:'Journal',doi:'10.1234/test'}}};
const from=R.referenceFromEntry(entry,()=> 'r3');assert.equal(from.title,'Recorded Source');assert.equal(from.origins[0].key,'object:p1:s1');assert.equal(from.doi,'10.1234/test');
const lib=R.normalizeLibrary({references:[a,b,from]});assert.equal(lib.references.length,3);const pkg=R.exportPackage(lib,{style:'mla9'});assert.equal(pkg.preferences.style,'mla9');assert.equal(pkg.integrity.fingerprints.length,3);
console.log('PASS - v0.44.0 Citation Library & Reference Management runtime');
