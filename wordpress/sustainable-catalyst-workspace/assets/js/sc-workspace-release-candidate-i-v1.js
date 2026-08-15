(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceReleaseCandidateI=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-release-candidate/1.0';
  const REPORT_SCHEMA='sc-workspace-release-candidate-report/1.0';
  const CHECKLIST_SCHEMA='sc-workspace-release-candidate-checklist/1.0';
  const RELEASE_VERSION='0.82.1';
  const STORAGE_VERSION='35';
  const PROJECT_SCHEMA='sc-workspace-project/20.0';
  const EXPORT_SCHEMA='sc-workspace-project-export/20.0';
  const FEATURE_FREEZE_POLICY='defect-fixes-certification-deployment-only';
  const AUTOMATED_GATES=Object.freeze([
    ['release-identity','Release identity','The running Workspace must identify itself as the current v0.82.1 Release Candidate runtime.'],
    ['release-stage','Release Candidate stage','The application root must declare the release-candidate stage.'],
    ['schema-freeze','Canonical schema freeze','Storage 35 and Project 20.0 remain unchanged at the RC boundary.'],
    ['required-surfaces','Required certification surfaces','Beta Closure, Security & Privacy, Final Audit, Recovery Drills, Help, and the integration/handoff surfaces remain reachable.'],
    ['required-runtimes','Required hardening runtimes','The inherited closure, security, final-audit, recovery, compatibility, and persistence runtimes remain loaded.'],
    ['beta-closure','Public Beta III automated closure','The frozen v0.79 closure contract still reports zero known automated blockers.'],
    ['recovery-drills','Recovery/disaster simulations','All sandboxed recovery/disaster scenarios must continue to pass.'],
    ['final-audit','Accessibility/performance gate','The inherited final automated accessibility/performance audit must have no blocking finding.'],
    ['feature-freeze','Feature-freeze policy','RC I permits defect fixes, certification, deployment, compatibility, recovery, documentation, and rollback work only.']
  ].map(([id,label,detail])=>Object.freeze({id,label,detail})));
  const MANUAL_FIELD_ITEMS=Object.freeze([
    ['production-wordpress','Production WordPress smoke test','Deploy the RC plugin on the real site and verify the Workspace page reaches the site footer without PHP or JavaScript critical errors.'],
    ['rollback-rehearsal','WordPress rollback rehearsal','Verify the prior v0.79.0 WordPress artifact can be restored without losing browser-local Workspace projects.'],
    ['assistive-technology','Assistive-technology field test','Complete representative workflows with VoiceOver/Safari and a Windows screen reader.'],
    ['zoom-contrast-touch','Zoom, contrast, and physical touch','Verify 200% zoom, 400%/320 CSS px reflow, measured contrast, forced colors, and a physical tablet/touch device.'],
    ['long-session','Representative multi-hour large-project session','Run a representative large project for at least four hours and inspect responsiveness, memory trend, and long-task behavior.'],
    ['two-device-sync','Real two-device continuity test','Exercise explicit sync/backup continuity, stale-revision conflict handling, and device migration with two real browser/device contexts.'],
    ['real-review-handoff','Real shared review and institutional handoff','Exchange actual review and institutional packages end to end and verify the personal source Workspace remains independent.']
  ].map(([id,label,procedure])=>Object.freeze({id,label,procedure})));
  const stamp=()=>new Date().toISOString();
  const finding=(id,label,pass,detail)=>({id,label,state:pass?'pass':'blocked',detail:String(detail||'')});
  function signals(root,env=globalThis){
    const required=['beta-closure','security','final-audit','recovery-drills','compatibility','integrity','help','collaboration','api-embed','institutional'];
    const surfaces={}; for(const id of required)surfaces[id]=Boolean(root?.querySelector?.(`[data-scw-workspace-section="${id}"]`));
    return {
      workspaceVersion:String(root?.dataset?.version||''),
      releaseStage:String(root?.dataset?.releaseStage||''),
      storageVersion:String(root?.dataset?.storageVersion||''),
      projectSchema:String(root?.dataset?.projectSchema||''),
      surfaces,
      modules:{
        betaClosure:Boolean(env.SCWorkspacePublicBetaIIIDefectClosure),
        persistence:Boolean(env.SCWorkspacePersistenceIntegrity),
        compatibility:Boolean(env.SCWorkspaceBrowserCompatibility),
        recovery:Boolean(env.SCWorkspaceRecoveryDisasterSimulation),
        securityAuditII:Boolean(env.SCWorkspaceSecurityPrivacyAuditII),
        accessibility:Boolean(env.SCWorkspaceAccessibility),
        performance:Boolean(env.SCWorkspacePerformanceSession),
        finalAudit:Boolean(env.SCWorkspaceAccessibilityPerformanceFinalAudit)
      }
    };
  }
  function assess(root,options={}){
    const env=options.env||globalThis,s=signals(root,env),checks=[];
    checks.push(finding('release-identity','Release identity',s.workspaceVersion===RELEASE_VERSION,`Workspace root reports ${s.workspaceVersion||'no version'}; expected ${RELEASE_VERSION}.`));
    checks.push(finding('release-stage','Release Candidate stage',s.releaseStage==='release-candidate',`Workspace stage is ${s.releaseStage||'unset'}; expected release-candidate.`));
    checks.push(finding('schema-freeze','Canonical schema freeze',s.storageVersion===STORAGE_VERSION&&s.projectSchema===PROJECT_SCHEMA,`Storage ${s.storageVersion||'unset'} / Project ${s.projectSchema||'unset'}; expected Storage ${STORAGE_VERSION} / ${PROJECT_SCHEMA}.`));
    checks.push(finding('required-surfaces','Required certification surfaces',Object.values(s.surfaces).every(Boolean),Object.entries(s.surfaces).filter(([,v])=>!v).map(([k])=>k).join(', ')||'All required certification and hardening surfaces are present.'));
    checks.push(finding('required-runtimes','Required hardening runtimes',Object.values(s.modules).every(Boolean),Object.entries(s.modules).filter(([,v])=>!v).map(([k])=>k).join(', ')||'All required inherited hardening runtimes are available.'));
    let closure=null; try{closure=env.SCWorkspacePublicBetaIIIDefectClosure?.contract?.()||null;}catch(_){closure=null;}
    checks.push(finding('beta-closure','Public Beta III automated closure',Boolean(closure&&closure.governance?.knownAutomatedBlockerCountAtRelease===0),closure?'The v0.79 closure contract records zero known automated blockers.':'Beta Closure contract is unavailable.'));
    let recovery=null; try{recovery=env.SCWorkspaceRecoveryDisasterSimulation?.runAll?.({workspaceVersion:RELEASE_VERSION,persistence:env.SCWorkspacePersistenceIntegrity,compatibility:env.SCWorkspaceImportExportCompatibility,continuity:env.SCWorkspaceCrossDeviceContinuity})||null;}catch(_){recovery=null;}
    checks.push(finding('recovery-drills','Recovery/disaster simulations',Boolean(recovery&&recovery.passed===recovery.total),recovery?`${recovery.passed}/${recovery.total} sandboxed disaster scenarios pass.`:'Recovery simulation engine could not run.'));
    let finalAudit=null; try{finalAudit=env.SCWorkspaceAccessibilityPerformanceFinalAudit?.run?.(root,{env,accessibilityEngine:env.SCWorkspaceAccessibility,performanceSummary:env.SCWorkspacePerformanceSession?.summary?.()||null})||null;}catch(_){finalAudit=null;}
    checks.push(finding('final-audit','Accessibility/performance automated gate',Boolean(finalAudit&&finalAudit.automatedReleaseGate),finalAudit?`${finalAudit.summary?.blocked||0} blocking final-audit finding(s).`:'Final Audit engine could not run.'));
    checks.push(finding('feature-freeze','Feature-freeze policy',true,'RC I is governed by defect-fixes, certification, deployment, compatibility, recovery, documentation, and rollback work only.'));
    const blocked=checks.filter(x=>x.state==='blocked').length;
    return {schema:SCHEMA,generatedAt:stamp(),workspaceVersion:RELEASE_VERSION,state:blocked?'blocked':'rc-automated-ready',automatedReleaseCandidateGate:blocked===0,knownAutomatedBlockerCount:blocked,checks,manualFieldItems:MANUAL_FIELD_ITEMS.map(x=>({...x,state:'manual'})),featureFreeze:{active:true,policy:FEATURE_FREEZE_POLICY,newProductSubsystemsAllowed:false,canonicalSchemaChangesAllowed:false,automaticPromotionToStable:false},claimBoundary:'Release Candidate I automated readiness is not production certification. Human field validation and deployment/rollback rehearsal remain explicit until performed.',governance:{featureFreeze:true,manualFieldValidationOutstanding:true,manualItemsSilentlyClosed:false,hiddenScore:false,canonicalMutation:false,automaticRepair:false,automaticPromotion:false,automaticUpload:false,telemetry:false}};
  }
  function report(workspaceVersion,result){return{schema:REPORT_SCHEMA,generatedAt:stamp(),workspaceVersion:String(workspaceVersion||RELEASE_VERSION).slice(0,40),assessment:result||null,privacy:{projectContentIncluded:false,objectContentIncluded:false,sourceContentIncluded:false,sourceUrlsIncluded:false,queryTextIncluded:false,accountIdentityIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,automaticSubmission:false},governance:{releaseCandidate:true,featureFreeze:true,manualFieldValidationOutstanding:true,canonicalMutation:false,automaticRepair:false,automaticPromotion:false,automaticUpload:false,telemetry:false,hiddenScore:false}};}
  function checklist(workspaceVersion){return{schema:CHECKLIST_SCHEMA,generatedAt:stamp(),workspaceVersion:String(workspaceVersion||RELEASE_VERSION).slice(0,40),items:MANUAL_FIELD_ITEMS.map(x=>({...x,state:'not-verified'})),instructions:'Complete these checks on the deployed Release Candidate. Record evidence outside Workspace as appropriate. Do not infer completion from the automated gate.',governance:{manual:true,automaticCompletion:false,automaticSubmission:false,canonicalMutation:false}};}
  function contract(){return{schema:SCHEMA,reportSchema:REPORT_SCHEMA,checklistSchema:CHECKLIST_SCHEMA,releaseVersion:RELEASE_VERSION,releaseCandidate:true,featureFreeze:true,featureFreezePolicy:FEATURE_FREEZE_POLICY,storageSchemaVersion:35,projectSchema:PROJECT_SCHEMA,projectExportSchema:EXPORT_SCHEMA,knownAutomatedBlockerCountAtRelease:0,manualFieldValidationOutstanding:true,rollbackArtifactRequired:true,packageIntegrityRequired:true,features:{betaClosureRequired:true,securityPrivacyGateRequired:true,accessibilityPerformanceGateRequired:true,recoveryDisasterGateRequired:true,wordpressHeaderWindowRequired:true,dependencyCycleGateRequired:true,packageIntegrityRequired:true,rollbackArtifactRequired:true},governance:{newProductSubsystemsAllowed:false,canonicalSchemaChangesAllowed:false,automaticPromotionToStable:false,automaticRepair:false,canonicalMutation:false,telemetry:false,schemaMigrationRequired:false}};}
  return Object.freeze({SCHEMA,REPORT_SCHEMA,CHECKLIST_SCHEMA,RELEASE_VERSION,STORAGE_VERSION,PROJECT_SCHEMA,EXPORT_SCHEMA,FEATURE_FREEZE_POLICY,AUTOMATED_GATES,MANUAL_FIELD_ITEMS,signals,assess,report,checklist,contract});
});
