'use strict';
const assert=require('assert');
const H=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-persistence-integrity-v1.js');
class Store{constructor(init={}){this.m=new Map(Object.entries(init));this.failSetKey='';}getItem(k){return this.m.has(k)?this.m.get(k):null;}setItem(k,v){if(this.failSetKey===k)throw new Error('simulated storage failure');this.m.set(k,String(v));}removeItem(k){this.m.delete(k);}}
const a=JSON.stringify({schemaVersion:35,projects:[{id:'p1',title:'A'}]});
const b=JSON.stringify({schemaVersion:35,projects:[{id:'p1',title:'B'}]});
const s=new Store({sc_workspace:a});
assert.strictEqual(H.SCHEMA,'sc-workspace-persistence-integrity/1.0');
assert.strictEqual(H.ALGORITHM,'fnv1a32');
assert.strictEqual(H.readableWorkspace(a),true);
assert.strictEqual(H.fingerprint(a).checksum.length,8);
let staged=H.stage(s,{previousRaw:a,nextRaw:b,workspaceVersion:'0.63.0',storageSchemaVersion:35});
assert.strictEqual(staged.ok,true);assert.strictEqual(staged.lastGoodCaptured,true);assert.ok(s.getItem(H.TRANSACTION_KEY));
const last=H.lastGoodState(s);assert.strictEqual(last.available,true);assert.strictEqual(last.state,'verified');
s.setItem(H.CURRENT_KEY,b);
let committed=H.commit(s,b,{workspaceVersion:'0.63.0',storageSchemaVersion:35});
assert.strictEqual(committed.ok,true);assert.strictEqual(s.getItem(H.TRANSACTION_KEY),null);assert.strictEqual(H.metadataState(s,b).state,'verified');
// A readable out-of-band mutation is detected but never repaired automatically.
const drift=JSON.stringify({schemaVersion:35,projects:[{id:'p1',title:'Changed elsewhere'}]});s.setItem(H.CURRENT_KEY,drift);
let audit=H.inspect(s);assert.strictEqual(audit.state,'attention');assert.strictEqual(audit.metadata.state,'integrity-drift');assert.strictEqual(s.getItem(H.CURRENT_KEY),drift);assert.strictEqual(audit.governance.automaticRepair,false);
// Failed transaction remains diagnosable.
staged=H.stage(s,{previousRaw:drift,nextRaw:b,workspaceVersion:'0.63.0',storageSchemaVersion:35});H.fail(s,new Error('quota'));audit=H.inspect(s);assert.strictEqual(audit.transaction.state,'failed');
const currentCandidate=H.recoveryCandidate(s,'current','0.63.0');assert.strictEqual(currentCandidate.schema,H.RECOVERY_SCHEMA);assert.strictEqual(currentCandidate.privacy.containsCanonicalWorkspaceContent,true);assert.strictEqual(currentCandidate.governance.automaticRestore,false);
const diag=H.diagnosticSnapshot(s,'0.63.0');assert.strictEqual(diag.privacy.projectContentIncluded,false);assert.strictEqual(diag.privacy.rawStateIncluded,false);assert.ok(!Object.prototype.hasOwnProperty.call(diag,'raw'));
// Prepared transaction that never wrote target can reconcile against previous bytes without mutating canonical content.
s.setItem(H.CURRENT_KEY,drift);H.stage(s,{previousRaw:drift,nextRaw:b,workspaceVersion:'0.63.0',storageSchemaVersion:35});const before=s.getItem(H.CURRENT_KEY);const rec=H.reconcileJournal(s,{workspaceVersion:'0.63.0',storageSchemaVersion:35});assert.strictEqual(rec.state,'resolved-prewrite');assert.strictEqual(s.getItem(H.CURRENT_KEY),before);assert.strictEqual(s.getItem(H.TRANSACTION_KEY),null);

// Checksum-bound last-known-good snapshots refuse to verify after envelope drift.
const integrityDamaged=new Store({sc_workspace:a});H.stage(integrityDamaged,{previousRaw:a,nextRaw:b,workspaceVersion:'0.63.0',storageSchemaVersion:35});
const damagedEnvelope=JSON.parse(integrityDamaged.getItem(H.LAST_GOOD_KEY));damagedEnvelope.raw=damagedEnvelope.raw.replace('\"A\"','\"Damaged\"');integrityDamaged.setItem(H.LAST_GOOD_KEY,JSON.stringify(damagedEnvelope));
assert.strictEqual(H.lastGoodState(integrityDamaged).state,'integrity-drift');
// A failed integrity-receipt write does not clear the transaction journal or claim success.
const receiptFailure=new Store({sc_workspace:a});H.stage(receiptFailure,{previousRaw:a,nextRaw:b,workspaceVersion:'0.63.0',storageSchemaVersion:35});receiptFailure.setItem(H.CURRENT_KEY,b);receiptFailure.failSetKey=H.METADATA_KEY;
const failedCommit=H.commit(receiptFailure,b,{workspaceVersion:'0.63.0',storageSchemaVersion:35});assert.strictEqual(failedCommit.ok,false);assert.strictEqual(failedCommit.reason,'integrity-metadata-write-failed');assert.ok(receiptFailure.getItem(H.TRANSACTION_KEY));

console.log('PASS - Workspace v0.63.0 Product Hardening II persistence integrity runtime');
