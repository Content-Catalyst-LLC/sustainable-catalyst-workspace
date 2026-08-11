const assert=require('assert');
const A=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-v1.js');
class Store{
  constructor(seed={}){this.m=new Map(Object.entries(seed));}
  get length(){return this.m.size;} key(i){return [...this.m.keys()][i]??null;} getItem(k){return this.m.has(k)?this.m.get(k):null;} setItem(k,v){this.m.set(k,String(v));} removeItem(k){this.m.delete(k);}
}
const s=new Store({
  sc_workspace:JSON.stringify({projects:[{id:'p1',title:'Private'}]}),
  sc_workspace_reference_library_v1:'{"references":[]}',
  sc_workspace_future_private_v9:'future',
  sc_workspace_api_embed_v1:'{"projections":[{"id":"x"}]}',
  unrelated_app_key:'leave-me-alone'
});
let inv=A.inventory(s);assert.equal(inv.length,4);assert(inv.find(x=>x.key==='sc_workspace'&&x.known));assert(inv.find(x=>x.key==='sc_workspace_future_private_v9'&&!x.known));
const audit=A.audit(s,{storageAvailable:true,serverBackupsKnown:true,now:'2026-08-10T20:20:00-05:00'});assert.equal(audit.counts.unknown,1);assert.equal(audit.counts.disclosureArtifacts,1);assert(audit.findings.some(x=>x.code==='localstorage-plaintext-boundary'));assert.equal(audit.threatModel.nonClaims.localStorageEncryption,false);
const bundle=A.buildPortabilityBundle(s,{workspaceVersion:'0.59.0',now:'2026-08-10T20:20:00-05:00'});assert.equal(bundle.schema,A.PORTABILITY_SCHEMA);assert.equal(Object.keys(bundle.stores).length,4);assert(!('unrelated_app_key' in bundle.stores));assert(A.verifyPortabilityBundle(bundle).ok);const tampered=JSON.parse(JSON.stringify(bundle));tampered.stores.sc_workspace='changed';assert(!A.verifyPortabilityBundle(tampered).ok);
const plan=A.deletionPlan(s);assert.equal(plan.count,4);let bad=A.executeDeletion(s,'DELETE EVERYTHING');assert(!bad.ok);assert.equal(s.getItem('sc_workspace')!==null,true);
const receipt=A.executeDeletion(s,A.CONFIRM_PHRASE,{now:'2026-08-10T20:21:00-05:00'});assert(receipt.ok);assert(receipt.verified);assert.equal(receipt.remaining.length,0);assert.equal(s.getItem('unrelated_app_key'),'leave-me-alone');assert.equal(receipt.serverBackupsDeleted,false);assert.equal(receipt.unrelatedLocalStorageTouched,false);
console.log('PASS - Workspace v0.59.0 Security, Privacy & Data-Portability Audit runtime');
