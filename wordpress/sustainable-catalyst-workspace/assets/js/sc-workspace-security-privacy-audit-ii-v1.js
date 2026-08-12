(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.SCWorkspaceSecurityPrivacyAuditII=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-security-privacy-audit-ii/1.0';
  const REPORT_SCHEMA='sc-workspace-security-privacy-audit-ii-report/1.0';
  const POLICY_SCHEMA='sc-workspace-security-privacy-audit-ii-policy/1.0';
  const PREFIX='sc_workspace';
  const CLASSIFIERS=[
    [/^sc_workspace(?:_v0_1)?$/,'canonical-projects'],
    [/^sc_workspace_(?:project|object|canvas|handoff|handoff_v2|intent|origin|return)$/,'canonical-workspace'],
    [/^sc_workspace_(?:last_good|recovery|persistence|route_state)/,'recovery-integrity'],
    [/^sc_workspace_(?:shared_review|institutional|api_embed)/,'disclosure-handoff'],
    [/^sc_workspace_(?:ai_|notebook_assistance)/,'assistance-exchange'],
    [/^sc_workspace_(?:device|public_beta|research_surface|experience)/,'session-diagnostics'],
    [/^sc_workspace_(?:reference_library|research_|citation_|composition_|cross_project|grounded_)/,'research-derived'],
    [/^sc_workspace_/,'workspace-unclassified']
  ];
  function bytes(v){try{return new TextEncoder().encode(String(v||'')).length;}catch(_){return String(v||'').length*2;}}
  function keys(storage){const out=[];if(!storage)return out;try{for(let i=0;i<storage.length;i++){const k=storage.key(i);if(typeof k==='string'&&k.startsWith(PREFIX))out.push(k);}}catch(_){}return out.sort();}
  function classify(key){for(const [rx,name] of CLASSIFIERS){if(rx.test(key))return name;}return 'other';}
  function summarize(storage,surface){
    const totals={surface,count:0,bytes:0,unknown:0,classes:{}};
    for(const key of keys(storage)){
      let value='';try{value=storage.getItem(key)||'';}catch(_){}
      const cls=classify(key),size=bytes(value);totals.count+=1;totals.bytes+=size;if(cls==='workspace-unclassified')totals.unknown+=1;
      if(!totals.classes[cls])totals.classes[cls]={count:0,bytes:0};totals.classes[cls].count+=1;totals.classes[cls].bytes+=size;
    }
    return totals;
  }
  function cookieSummary(cookieString){
    const names=String(cookieString||'').split(';').map(x=>x.trim().split('=')[0]).filter(Boolean);
    const workspace=names.filter(n=>/^sc[_-]?workspace|^scw[_-]/i.test(n));
    return {accessibleCookieCount:names.length,accessibleWorkspaceCookieCount:workspace.length,cookieNamesIncluded:false,cookieValuesIncluded:false};
  }
  function environment(env={}){
    const protocol=String(env.protocol||'');
    return {
      secureContext:env.isSecureContext===true,
      https:protocol==='https:',
      embedded:env.topEqualsSelf===false,
      cookieEnabled:env.cookieEnabled!==false,
      crossOriginIsolated:env.crossOriginIsolated===true,
      referrerPresent:env.referrerPresent===true,
      locationIncluded:false,
      referrerIncluded:false,
      userAgentIncluded:false,
      deviceIdentifierIncluded:false
    };
  }
  function buildReport(localStorage,sessionStorage,env={},options={}){
    const local=summarize(localStorage,'localStorage'),session=summarize(sessionStorage,'sessionStorage'),browser=environment(env),cookies=cookieSummary(options.cookieString||'');
    const findings=[];
    function add(code,severity,message){findings.push({code,severity,message});}
    if(!browser.secureContext||!browser.https)add('insecure-context','attention','Workspace is not running in a fully secure HTTPS browser context.');
    if(browser.embedded)add('embedded-context','info','Workspace is running inside an embedded browsing context; origin and framing boundaries should remain explicit.');
    if(local.unknown+session.unknown)add('unclassified-workspace-storage','attention',`${local.unknown+session.unknown} Workspace-owned storage key${local.unknown+session.unknown===1?' is':'s are'} not mapped to a declared data class.`);
    if(cookies.accessibleWorkspaceCookieCount)add('workspace-cookie-surface','attention','A script-readable Workspace-like cookie name is present; review whether a cookie is necessary and whether HttpOnly is appropriate for server-managed state.');
    if(!findings.length)add('declared-browser-boundaries','ok','No runtime attention conditions were detected by the privacy-minimized browser audit.');
    return {
      schema:REPORT_SCHEMA,
      generatedAt:options.now||new Date().toISOString(),
      workspaceVersion:options.workspaceVersion||'',
      scope:'privacy-minimized-browser-security-audit',
      storage:{local,session},browser,cookies,findings,
      releaseGates:{restPermissionSplit:true,publicRestRoutesGetMetadataOnly:true,cloudNonceHeader:true,cloudSameOriginCredentials:true,dynamicCodePrimitivesBlocked:true,secretLiteralScan:true,externalNetworkLiteralScan:true,wordpressHeaderWindow:true,dependencyCycleCheck:true},
      exclusions:{projectContent:true,sourceUrls:true,queryText:true,storageValues:true,storageKeyNames:true,cookieNames:true,cookieValues:true,accountIdentity:true,deviceIdentity:true,userAgent:true,referrer:true},
      governance:{automaticDeletion:false,automaticUpload:false,automaticDisclosure:false,automaticRepair:false,canonicalMutation:false,telemetry:false}
    };
  }
  function contract(){return {schema:SCHEMA,reportSchema:REPORT_SCHEMA,policySchema:POLICY_SCHEMA,storageSchemaVersion:35,projectSchema:'sc-workspace-project/20.0',runtime:{localStorageMetadataOnly:true,sessionStorageMetadataOnly:true,accessibleCookieCountOnly:true,secureContextCheck:true,embeddedContextCheck:true,unknownWorkspaceStoreDetection:true},releaseGates:{restPermissionSplit:true,publicRestRoutesGetMetadataOnly:true,cloudNonceHeader:true,cloudSameOriginCredentials:true,dynamicCodePrimitivesBlocked:true,secretLiteralScan:true,externalNetworkLiteralScan:true,wordpressHeaderWindow:true,dependencyCycleCheck:true},nonClaims:{localStorageEncryption:false,cookieAuditSeesHttpOnly:false,sourceAuditIsPenetrationTest:false,integrityFingerprintIsAuthentication:false},governance:{automaticDeletion:false,automaticUpload:false,automaticDisclosure:false,automaticRepair:false,canonicalMutation:false,telemetry:false,schemaMigrationRequired:false}};}
  return {SCHEMA,REPORT_SCHEMA,POLICY_SCHEMA,PREFIX,bytes,keys,classify,summarize,cookieSummary,environment,buildReport,contract};
});
