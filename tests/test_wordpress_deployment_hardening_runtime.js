const assert=require('assert');
const A=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-wordpress-deployment-hardening-v1.js');
function node(url,attr){return {getAttribute:(k)=>k===attr?url:''};}
function doc(script='https://example.test/wp-content/plugins/workspace/assets/js/workspace-v2.0.1.js?ver=2.0.1',style='https://example.test/wp-content/plugins/workspace/assets/css/workspace-v2.0.1.css?ver=2.0.1',extraScripts=[]){return {querySelectorAll(sel){if(sel==='script[src]')return [node(script,'src'),...extraScripts.map(x=>node(x,'src'))];if(sel==='link[rel="stylesheet"][href]')return [node(style,'href')];return [];}}}
const root={dataset:{version:'2.0.1',releaseStage:'button-system-repair',scwDeploymentServerState:'server-ready'}};
const env={SCWorkspaceIdentity:{workspaceVersion:'2.0.1'},SCWorkspaceReleaseCandidateI:{},document:doc()};
let r=A.assess(root,{env,document:env.document});
assert.equal(r.automatedDeploymentGate,true);assert.equal(r.knownAutomatedBlockerCount,0);assert.equal(r.assets.staleScriptCount,0);
let stale=A.assess(root,{env:{...env,document:doc(undefined,undefined,['https://example.test/workspace-v0.84.0.js?ver=0.84.0'])},document:doc(undefined,undefined,['https://example.test/workspace-v0.84.0.js?ver=0.84.0'])});
assert.equal(stale.automatedDeploymentGate,false);assert(stale.checks.some(x=>x.id==='current-script'&&x.state==='blocked'));
let wrongRoot=A.assess({dataset:{version:'0.84.0',releaseStage:'ga-stabilization',scwDeploymentServerState:'server-ready'}},{env,document:env.document});
assert.equal(wrongRoot.automatedDeploymentGate,false);
let wrongServer=A.assess({dataset:{version:'2.0.1',releaseStage:'button-system-repair',scwDeploymentServerState:'attention'}},{env,document:env.document});
assert.equal(wrongServer.automatedDeploymentGate,false);
const report=A.report('2.0.1',r);assert.equal(report.schema,'sc-workspace-wordpress-deployment-report/1.0');assert.equal(report.privacy.projectContentIncluded,false);assert.equal(report.governance.automaticCachePurge,false);
const checklist=A.checklist('2.0.1');assert.equal(checklist.rollbackRelease,'2.0.0');assert(checklist.items.length>=7);assert.equal(checklist.governance.automaticCompletion,false);
const c=A.contract();assert.equal(c.releaseVersion,'2.0.1');assert.equal(c.schemaMigrationRequired,false);assert.equal(c.projectDataMutation,false);assert.equal(c.automaticRollback,false);
console.log('PASS - current inherited WordPress & Deployment Hardening runtime');
