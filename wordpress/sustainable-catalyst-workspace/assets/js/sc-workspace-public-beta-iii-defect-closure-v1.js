(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspacePublicBetaIIIDefectClosure=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-public-beta-iii-defect-closure/1.0';
  const REPORT_SCHEMA='sc-workspace-public-beta-iii-defect-closure-report/1.0';
  const RELEASE_VERSION='0.79.0';
  const CLOSED_DEFECT_CLASSES=Object.freeze([
    ['wordpress-plugin-header-window-overflow','WordPress plugin metadata window','Required plugin metadata remains inside WordPress’s bounded header read.'],
    ['accessibility-script-dependency-cycle','Accessibility runtime dependency cycle','The accessibility runtime cannot depend on itself and the enqueue graph remains acyclic.'],
    ['desktop-grid-min-content-collapse','Desktop grid/min-content collapse','The hardened desktop and focused-research grids remain bounded and reflow safely.'],
    ['unsafe-direct-import-commit','Unsafe direct import commit','Project imports remain stage → review → explicit commit and never silently overwrite an existing project.'],
    ['cross-device-stale-revision-overwrite','Cross-device stale revision overwrite','Sync keeps revision preconditions and conflict evidence instead of silent last-write-wins.'],
    ['shared-review-stale-response-reconciliation','Stale shared-review reconciliation','Stale/unverifiable review responses require explicit owner acknowledgement and duplicates are blocked.'],
    ['api-embed-invalid-payload-render','Invalid API/embed payload render','Read-only integrations fail closed when payload, integrity, or origin checks fail.'],
    ['institutional-handoff-unvalidated-export','Unvalidated institutional export','Institutional packages and receipts must pass explicit validation before transfer/commit.'],
    ['security-privacy-release-gate-gaps','Security/privacy release-gate gaps','REST permission, nonce, dynamic-code, secret-literal, and network-boundary source gates remain release blockers.'],
    ['accessibility-performance-critical-regression','Critical accessibility/performance regression','Structural accessibility and critical performance regressions remain blocking conditions in the final audit.']
  ].map(([id,label,detail])=>Object.freeze({id,label,detail})));
  const MANUAL_FIELD_ITEMS=Object.freeze([
    ['production-wordpress','Production WordPress smoke test','Verify the deployed page reaches the site footer without PHP/JavaScript critical errors.'],
    ['assistive-technology','Assistive-technology field test','Complete representative workflows with VoiceOver/Safari and a Windows screen reader.'],
    ['zoom-contrast-touch','Zoom, measured contrast, and physical touch','Verify 200% zoom, 400%/320 CSS px reflow, measured contrast, forced colors, and a physical tablet/touch device.'],
    ['long-session','Representative multi-hour session','Run a representative large project for at least four hours and inspect responsiveness, memory trend, and long-task behavior.'],
    ['two-device-sync','Real two-device continuity test','Exercise explicit sync/backup continuity, stale-revision conflict handling, and device migration using two real browser/device contexts.'],
    ['real-handoff','Real shared/institutional handoff test','Exchange an actual review or institutional package end to end and verify the source Workspace remains independent.']
  ].map(([id,label,procedure])=>Object.freeze({id,label,procedure})));
  const stamp=()=>new Date().toISOString();
  const check=(id,label,pass,detail)=>({id,label,state:pass?'pass':'blocked',detail:String(detail||'')});
  function runtimeSignals(root,env=globalThis){
    const doc=root?.ownerDocument||env?.document;
    const sections=['journey','integrity','compatibility','accessibility','final-audit','recovery-drills','security','collaboration','api-embed','institutional','help'];
    const surfaces={}; for(const id of sections)surfaces[id]=Boolean(root?.querySelector?.(`[data-scw-workspace-section="${id}"]`));
    const modules={
      betaIII:Boolean(env.SCWorkspacePublicBetaIII),persistence:Boolean(env.SCWorkspacePersistenceIntegrity),compatibility:Boolean(env.SCWorkspaceBrowserCompatibility),accessibility:Boolean(env.SCWorkspaceAccessibility),performance:Boolean(env.SCWorkspacePerformanceSession),recovery:Boolean(env.SCWorkspaceRecoveryDisasterSimulation),securityAuditII:Boolean(env.SCWorkspaceSecurityPrivacyAuditII),finalAudit:Boolean(env.SCWorkspaceAccessibilityPerformanceFinalAudit)
    };
    return {workspaceVersion:String(root?.dataset?.version||''),documentLanguage:String(doc?.documentElement?.getAttribute?.('lang')||''),surfaces,modules};
  }
  function assess(root,options={}){
    const env=options.env||globalThis,signals=runtimeSignals(root,env),checks=[];
    checks.push(check('release-version','Current release identity',signals.workspaceVersion===RELEASE_VERSION,`Workspace root reports ${signals.workspaceVersion||'no version'}; expected ${RELEASE_VERSION}.`));
    checks.push(check('required-surfaces','Beta III hardening surfaces',Object.values(signals.surfaces).every(Boolean),Object.entries(signals.surfaces).filter(([,v])=>!v).map(([k])=>k).join(', ')||'All required hardening/product-fit surfaces are present.'));
    checks.push(check('required-modules','Required hardening runtimes',Object.values(signals.modules).every(Boolean),Object.entries(signals.modules).filter(([,v])=>!v).map(([k])=>k).join(', ')||'All required runtime modules are available.'));
    let topology=null;
    try{topology=env.SCWorkspacePublicBetaIII?.assess?.(root)||null;}catch(_){topology=null;}
    checks.push(check('beta-iii-topology','Public Beta III product topology',Boolean(topology&&topology.ready===topology.total),topology?`${topology.ready}/${topology.total} product-journey checkpoints are reachable.`:'Beta III topology engine is unavailable.'));
    let recovery=null;
    try{recovery=env.SCWorkspaceRecoveryDisasterSimulation?.runAll?.({workspaceVersion:RELEASE_VERSION,persistence:env.SCWorkspacePersistenceIntegrity,compatibility:env.SCWorkspaceImportExportCompatibility,continuity:env.SCWorkspaceCrossDeviceContinuity})||null;}catch(_){recovery=null;}
    checks.push(check('recovery-drills','Recovery/disaster simulations',Boolean(recovery&&recovery.passed===recovery.total),recovery?`${recovery.passed}/${recovery.total} sandboxed disaster scenarios pass.`:'Recovery simulation engine could not run.'));
    let finalAudit=null;
    try{finalAudit=env.SCWorkspaceAccessibilityPerformanceFinalAudit?.run?.(root,{env,accessibilityEngine:env.SCWorkspaceAccessibility,performanceSummary:env.SCWorkspacePerformanceSession?.summary?.()||null})||null;}catch(_){finalAudit=null;}
    checks.push(check('final-audit','Accessibility/performance automated gate',Boolean(finalAudit&&finalAudit.automatedReleaseGate),finalAudit?`${finalAudit.summary?.blocked||0} blocking final-audit finding(s).`:'Final audit engine could not run.'));
    const blocked=checks.filter(x=>x.state==='blocked').length;
    return {schema:SCHEMA,generatedAt:stamp(),workspaceVersion:RELEASE_VERSION,state:blocked?'blocked':'automated-closure-pass',automatedGate:blocked===0,knownAutomatedBlockerCount:blocked,checks,closedDefectClasses:CLOSED_DEFECT_CLASSES.map(x=>({...x})),manualFieldItems:MANUAL_FIELD_ITEMS.map(x=>({...x,state:'manual'})),claimBoundary:'Automated defect closure does not certify production browsers, assistive technology, real multi-hour sessions, two-device continuity, or real external handoffs. Those field validations remain explicit and unresolved until a human performs them.',governance:{noNewProductSubsystem:true,manualFieldValidationOutstanding:true,manualItemsSilentlyClosed:false,hiddenScore:false,automaticRepair:false,automaticMutation:false,automaticUpload:false,telemetry:false}};
  }
  function report(workspaceVersion,result){const r=result||{};return{schema:REPORT_SCHEMA,generatedAt:stamp(),workspaceVersion:String(workspaceVersion||RELEASE_VERSION).slice(0,40),assessment:r,privacy:{projectContentIncluded:false,objectContentIncluded:false,sourceContentIncluded:false,sourceUrlsIncluded:false,queryTextIncluded:false,accountIdentityIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,automaticSubmission:false},governance:{automatedClosureOnly:true,manualFieldValidationOutstanding:true,canonicalMutation:false,automaticRepair:false,automaticUpload:false,telemetry:false,hiddenScore:false}};}
  function contract(){return{schema:SCHEMA,reportSchema:REPORT_SCHEMA,releaseVersion:RELEASE_VERSION,closedDefectClassCount:CLOSED_DEFECT_CLASSES.length,manualFieldItemCount:MANUAL_FIELD_ITEMS.length,features:{automatedDefectGate:true,currentReleaseConsistency:true,betaIIIProductTopology:true,recoveryDisasterGate:true,accessibilityPerformanceGate:true,manualFieldValidationSeparation:true},governance:{knownAutomatedBlockerCountAtRelease:0,noNewProductSubsystem:true,manualFieldValidationOutstanding:true,manualItemsSilentlyClosed:false,canonicalMutation:false,automaticRepair:false,automaticUpload:false,telemetry:false,schemaMigrationRequired:false,storageSchemaVersion:35,projectSchema:'sc-workspace-project/20.0'}};}
  return Object.freeze({SCHEMA,REPORT_SCHEMA,RELEASE_VERSION,CLOSED_DEFECT_CLASSES,MANUAL_FIELD_ITEMS,runtimeSignals,assess,report,contract});
});
