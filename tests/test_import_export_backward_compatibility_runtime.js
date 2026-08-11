const assert=require('assert');
const fs=require('fs');
const path=require('path');
const C=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js');
assert.equal(C.SCHEMA,'sc-workspace-import-export-compatibility/1.0');
assert.equal(C.CURRENT_PROJECT_SCHEMA,'sc-workspace-project/20.0');
assert.equal(C.CURRENT_EXPORT_SCHEMA,'sc-workspace-project-export/20.0');
assert.equal(C.CURRENT_STORAGE_SCHEMA,35);
assert.equal(C.PROJECT_SCHEMAS.length,21);
assert.equal(C.EXPORT_SCHEMAS.length,21);
assert(C.PROJECT_SCHEMAS.includes('sc-workspace-project/3.1'));
assert(C.EXPORT_SCHEMAS.includes('sc-workspace-project-export/3.1'));
for(const schema of C.PROJECT_SCHEMAS){const p={schema,id:'p',title:'P',objects:[]};const c=C.classifyProjectPayload(p);assert.equal(c.ok,true,schema);assert.equal(c.projectSchema,schema);}
for(const schema of C.EXPORT_SCHEMAS){const version=schema.split('/')[1];const p={schema,project:{schema:`sc-workspace-project/${version}`,id:'p',title:'P',objects:[]}};const c=C.classifyProjectPayload(p);assert.equal(c.ok,true,schema);}
const fixture=n=>JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/import-export-compatibility',n),'utf8'));
for(const name of ['project-export-v1.json','project-export-v3-1.json','project-export-v10.json','project-export-v20.json']){const a=C.assessProjectImport(fixture(name),['legacy-v1']);assert.equal(a.status,'ready',name);assert.equal(a.reviewRequired,true);assert.equal(a.automaticCommit,false);assert.equal(a.automaticOverwrite,false);}
const collision=C.assessProjectImport(fixture('project-export-v1.json'),['legacy-v1']);assert.equal(collision.idCollision,true);assert(collision.warnings.some(x=>x.includes('new local project ID')));
const future=C.assessProjectImport(fixture('project-export-future-v21.json'),[]);assert.equal(future.status,'blocked');assert.equal(future.futureSchemaBlocked,true);assert(future.errors[0].includes('newer Workspace'));
const malformed=C.assessProjectImport(fixture('malformed-project-export.json'),[]);assert.equal(malformed.status,'blocked');
const portable=C.classifyProjectPayload({schema:C.PORTABLE_PROJECT_SCHEMA,manifest:{},project:{}});assert.equal(portable.ok,false);assert(portable.error.includes('Share & portable projects'));
const matrix=C.compatibilityMatrix();assert.equal(matrix.projectImport.mode,'stage-review-import-as-new-local-copy');assert.equal(matrix.projectImport.automaticOverwrite,false);assert.equal(matrix.browserStorage.supportedStorageVersions.length,35);assert.equal(matrix.projectImport.futureProjectSchemas,'blocked-no-downgrade');
const current={schema:C.CURRENT_PROJECT_SCHEMA,id:'p1',title:'Round Trip',description:'Stable',status:'active',objects:[{id:'o1',type:'source',title:'Source',content:'Body',tags:['x']}],research:{questions:[]}};
const identity=x=>JSON.parse(JSON.stringify(x));
const receipt=C.roundTripCheck(current,identity);assert.equal(receipt.ok,true);assert.equal(receipt.equivalent,true);assert.equal(receipt.beforeFingerprint,receipt.afterFingerprint);assert.equal(receipt.checksumPurpose,'drift-detection-only-not-security');
const drift=C.roundTripCheck(current,x=>({...JSON.parse(JSON.stringify(x)),title:'Changed'}));assert.equal(drift.ok,true);assert.equal(drift.equivalent,false);
const prepared=C.currentProjectExport(current,'0.66.0',identity);assert.equal(prepared.ok,true);assert.equal(prepared.payload.schema,C.CURRENT_EXPORT_SCHEMA);assert.equal(prepared.payload.compatibility.importMode,'stage-review-new-local-copy');assert.equal(prepared.payload.compatibility.futureSchemaDowngrade,false);
console.log('PASS - v0.66.0 import/export backward compatibility runtime');
