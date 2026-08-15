const assert=require('assert');
const A=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-production-smoke-cache-rollback-v1.js');
function node(url,attr){return {getAttribute:(k)=>k===attr?url:''};}
function doc(script='https://example.test/workspace-v1.11.0.js?ver=1.11.0',style='https://example.test/workspace-v1.11.0.css?ver=1.11.0',extras=[]){return {querySelectorAll(sel){if(sel==='script[src]')return [node(script,'src'),...extras.map(x=>node(x,'src'))];if(sel==='link[rel="stylesheet"][href]')return [node(style,'href')];return [];}}}
const root={dataset:{version:'1.11.0',releaseStage:'developer-api',scwDeploymentServerState:'server-ready'}};
const env={SCWorkspaceIdentity:{workspaceVersion:'1.11.0'},SCWorkspaceWordPressDeploymentHardening:{},SCWorkspaceReleaseCandidateI:{},document:doc()};
let r=A.assess(root,{env,document:env.document}); assert.equal(r.packageAutomatedGate,true); assert.equal(r.productionCertified,false); assert.equal(r.knownAutomatedBlockerCount,0); assert.equal(r.manualFieldItems.length,6);
let staleDoc=doc(undefined,undefined,['https://example.test/workspace-v0.84.0.js?ver=0.84.0']); let stale=A.assess(root,{env:{...env,document:staleDoc},document:staleDoc}); assert.equal(stale.packageAutomatedGate,false); assert(stale.checks.some(x=>x.id==='script'&&x.state==='blocked'));
let bad=A.assess({dataset:{version:'0.84.0',releaseStage:'ga-stabilization',scwDeploymentServerState:'server-ready'}},{env,document:env.document}); assert.equal(bad.packageAutomatedGate,false);
const rep=A.report('1.11.0',r); assert.equal(rep.productionCertified,false); assert.equal(rep.rollbackRelease,'1.10.0'); assert.equal(rep.privacy.projectContentIncluded,false); assert.equal(rep.governance.automaticRollback,false);
const list=A.checklist('1.11.0'); assert.equal(list.rollbackRelease,'1.10.0'); assert.equal(list.items.length,6); assert.equal(list.governance.automaticCompletion,false);
const c=A.contract(); assert.equal(c.releaseVersion,'1.11.0'); assert.equal(c.previousRelease,'1.10.0'); assert.equal(c.liveProductionChecksManual,true); assert.equal(c.automaticProductionCertification,false);
console.log('PASS - current inherited Production Smoke, Cache & Rollback Certification runtime');
