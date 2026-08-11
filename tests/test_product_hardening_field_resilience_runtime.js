const assert=require('assert');const H=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-resilience-v1.js');
class Store{constructor(init={}){this.m=new Map(Object.entries(init));}getItem(k){return this.m.has(k)?this.m.get(k):null;}setItem(k,v){this.m.set(k,String(v));}removeItem(k){this.m.delete(k);}}
const routes=['start','projects','research','reliability'];
let s=H.sanitizeRouteState({schema:H.ROUTE_SCHEMA,view:'research',researchSurface:'tasks',version:'0.62.0',at:new Date().toISOString()},routes,'0.62.0');assert.equal(s.view,'research');assert.equal(s.researchSurface,'tasks');assert.equal(s.sanitized,false);
s=H.sanitizeRouteState({schema:H.ROUTE_SCHEMA,view:'missing',researchSurface:'search',version:'0.62.0',at:new Date().toISOString()},routes,'0.62.0');assert.equal(s.view,'start');assert.equal(s.reason,'invalid-route');
const st=new Store();const w=H.writeRouteState(st,{view:'projects',researchSurface:'overview'},routes,'0.62.0');assert.equal(w.view,'projects');assert.equal(H.readRouteState(st,routes,'0.62.0').view,'projects');
st.setItem(H.LEGACY_RESEARCH_KEY,'search');const cleared=H.clearUiState(st);assert(cleared.removed.includes(H.STORAGE_KEY));assert(cleared.removed.includes(H.LEGACY_RESEARCH_KEY));assert.equal(cleared.canonicalDataTouched,false);
const local=new Store({'sc_workspace':JSON.stringify({projects:[],versionHistory:{restorePoints:[]}})});const session=new Store();const env={window:{localStorage:local,sessionStorage:session,history:{pushState(){},replaceState(){}},File:function(){},FileReader:function(){},Blob:function(){},navigator:{onLine:true}},crypto:{subtle:{digest(){}}}};
const caps=H.capabilities(env);assert.equal(caps.localStorage,true);assert.equal(caps.sessionStorage,true);assert.equal(caps.historyApi,true);
const recovery=H.recoveryState(env);assert.equal(recovery.state,'healthy');
const assessment=H.assess({caps,recovery,routeState:H.readRouteState(session,routes,'0.62.0'),visibleSections:1});assert(['ready','limited'].includes(assessment.state));assert.equal(assessment.governance.canonicalMutation,false);assert.equal(assessment.governance.telemetry,false);
const snap=H.snapshot('0.62.0',assessment,caps,recovery,{view:'start',researchSurface:'overview',sanitized:false,reason:'current'});assert.equal(snap.schema,H.SNAPSHOT_SCHEMA);assert.equal(snap.privacy.projectContentIncluded,false);assert.equal(snap.privacy.deviceIdentifierIncluded,false);
console.log('PASS - Workspace v0.62.0 Product Hardening I runtime');
