const assert=require('assert');
const api=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-release-candidate-i-v1.js');
assert.equal(api.SCHEMA,'sc-workspace-release-candidate/1.0');
assert.equal(api.RELEASE_VERSION,'0.81.0');
assert.equal(api.MANUAL_FIELD_ITEMS.length,7);
const selectors=new Set(['beta-closure','security','final-audit','recovery-drills','compatibility','integrity','help','collaboration','api-embed','institutional']);
const root={dataset:{version:'0.81.0',releaseStage:'release-candidate',storageVersion:'35',projectSchema:'sc-workspace-project/20.0'},querySelector:(q)=>{const m=q.match(/data-scw-workspace-section="([^"]+)"/);return m&&selectors.has(m[1])?{}:null;}};
const env={
 SCWorkspacePublicBetaIIIDefectClosure:{contract:()=>({governance:{knownAutomatedBlockerCountAtRelease:0}})},
 SCWorkspacePersistenceIntegrity:{},SCWorkspaceBrowserCompatibility:{},SCWorkspaceSecurityPrivacyAuditII:{},SCWorkspaceAccessibility:{},
 SCWorkspacePerformanceSession:{summary:()=>({render:{p95Ms:10},index:{p95Ms:20},counters:{longTaskCount:0},memory:{supported:false}})},
 SCWorkspaceRecoveryDisasterSimulation:{runAll:()=>({passed:8,total:8})},
 SCWorkspaceAccessibilityPerformanceFinalAudit:{run:()=>({automatedReleaseGate:true,summary:{blocked:0}})},
 SCWorkspaceImportExportCompatibility:{},SCWorkspaceCrossDeviceContinuity:{}
};
const result=api.assess(root,{env});
assert.equal(result.automatedReleaseCandidateGate,true);assert.equal(result.knownAutomatedBlockerCount,0);assert.equal(result.state,'rc-automated-ready');assert.equal(result.featureFreeze.active,true);assert.equal(result.featureFreeze.newProductSubsystemsAllowed,false);assert.equal(result.governance.automaticPromotion,false);
const badVersion=api.assess({...root,dataset:{...root.dataset,version:'0.79.0'}},{env});assert.equal(badVersion.automatedReleaseCandidateGate,false);
const badStage=api.assess({...root,dataset:{...root.dataset,releaseStage:'public-beta'}},{env});assert.equal(badStage.automatedReleaseCandidateGate,false);
const report=api.report('0.81.0',result);assert.equal(report.workspaceVersion,'0.81.0');assert.equal(report.privacy.projectContentIncluded,false);assert.equal(report.governance.featureFreeze,true);
const checklist=api.checklist('0.81.0');assert.equal(checklist.items.length,7);assert.equal(checklist.governance.automaticCompletion,false);
const contract=api.contract();assert.equal(contract.releaseCandidate,true);assert.equal(contract.featureFreeze,true);assert.equal(contract.storageSchemaVersion,35);assert.equal(contract.projectSchema,'sc-workspace-project/20.0');assert.equal(contract.governance.schemaMigrationRequired,false);
console.log('PASS - v0.80.0 Workspace Release Candidate I runtime');
