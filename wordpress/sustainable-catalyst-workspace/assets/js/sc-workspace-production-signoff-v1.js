(function(global){
  'use strict';
  const RELEASE_VERSION='0.83.0';
  const PREVIOUS_RELEASE='0.82.1';
  const ROLLBACK_RELEASE='0.82.1';
  const SCHEMA='sc-workspace-production-signoff/1.0';
  const CERTIFICATE_SCHEMA='sc-workspace-production-signoff-certificate/1.0';
  const STORAGE_KEY='sc_workspace_production_signoff_v1';
  const REQUIREMENTS=[
    {id:'public-page-smoke',label:'Public page smoke',description:'The live Workspace page loads without a PHP critical error or blocking JavaScript failure.'},
    {id:'rest-identity',label:'REST release identity',description:'Workspace health and release endpoints identify the live runtime as v0.83.0.'},
    {id:'anonymous-use',label:'Anonymous use',description:'A signed-out visitor can open Workspace and create/use a local project.'},
    {id:'authenticated-use',label:'Authenticated use',description:'A signed-in account can use Workspace and optional account persistence remains explicit.'},
    {id:'cache-coherence',label:'Cache and asset coherence',description:'Browser/CDN delivery uses the current v0.83.0 cumulative assets without mixed-version residue.'},
    {id:'project-preservation',label:'Representative project preservation',description:'A representative pre-upgrade local project remains present and unchanged after deployment.'},
    {id:'rollback-rehearsal',label:'v0.82.1 rollback rehearsal',description:'The bundled v0.82.1 WordPress rollback package is installed and verified as the recovery baseline.'},
    {id:'reinstall-current-release',label:'v0.83.0 reinstall',description:'The current v0.83.0 package is reinstalled after rollback and returns to the expected live identity.'},
    {id:'assistive-technology',label:'Assistive technology',description:'Keyboard-only operation and the required screen-reader field check are completed.'},
    {id:'zoom-reflow-touch',label:'Zoom, reflow and touch',description:'Measured zoom/reflow and physical touch interaction checks are completed on representative devices.'},
    {id:'long-session-large-project',label:'Long-session / large-project use',description:'A representative multi-hour session with a large project completes without unacceptable degradation or corruption.'},
    {id:'two-device-continuity',label:'Two-device continuity',description:'A real two-device backup/sync or migration continuity exercise is completed with explicit conflict safeguards.'},
    {id:'shared-review-handoff',label:'Shared review handoff',description:'A real portable/shared review handoff round trip is completed and matched to its source project.'},
    {id:'institutional-handoff',label:'Institutional handoff',description:'A real institutional handoff/receipt flow is completed without mutating the source Workspace project.'}
  ];
  function now(){return new Date().toISOString();}
  function blank(){const checks={};REQUIREMENTS.forEach(r=>checks[r.id]=false);return {schema:SCHEMA,releaseVersion:RELEASE_VERSION,previousRelease:PREVIOUS_RELEASE,rollbackRelease:ROLLBACK_RELEASE,reviewerLabel:'',productionUrl:'https://sustainablecatalyst.com/platform/',checks,attestation:false,signedAt:'',updatedAt:now()};}
  function normalize(input){const src=(input&&typeof input==='object')?input:{};const out=blank();out.reviewerLabel=String(src.reviewerLabel||'').trim();out.productionUrl=String(src.productionUrl||out.productionUrl).trim();out.attestation=src.attestation===true;out.signedAt=String(src.signedAt||'');out.updatedAt=String(src.updatedAt||now());REQUIREMENTS.forEach(r=>{out.checks[r.id]=!!(src.checks&&src.checks[r.id]);});return out;}
  function validUrl(value){try{const u=new URL(value);return u.protocol==='https:'||u.protocol==='http:';}catch(e){return false;}}
  function evaluate(input){const r=normalize(input);const missing=REQUIREMENTS.filter(x=>!r.checks[x.id]).map(x=>x.id);const reviewerOk=r.reviewerLabel.length>0;const urlOk=validUrl(r.productionUrl);const attestationOk=r.attestation===true;const complete=missing.length===0&&reviewerOk&&urlOk&&attestationOk;return {complete,missing,reviewerOk,urlOk,attestationOk,completedCount:REQUIREMENTS.length-missing.length,requiredCount:REQUIREMENTS.length};}
  function complete(input,at){const r=normalize(input);const e=evaluate(r);r.updatedAt=at||now();r.signedAt=e.complete?(at||now()):'';return {record:r,evaluation:e};}
  function certificate(input){const r=normalize(input);const e=evaluate(r);return {schema:CERTIFICATE_SCHEMA,workspaceVersion:RELEASE_VERSION,previousRelease:PREVIOUS_RELEASE,rollbackRelease:ROLLBACK_RELEASE,release:'Live Production Certification & Release Sign-Off',status:e.complete?'signed-off':'pending',signedOff:e.complete,reviewerLabel:r.reviewerLabel,productionUrl:r.productionUrl,signedAt:e.complete?r.signedAt:'',requiredCheckCount:REQUIREMENTS.length,attestedCheckCount:e.completedCount,checks:REQUIREMENTS.map(x=>({id:x.id,label:x.label,attested:!!r.checks[x.id]})),humanAttestation:r.attestation===true,automaticCertification:false,automaticRollback:false,automaticCachePurge:false,projectContentIncluded:false,telemetry:false};}
  function load(storage){try{const s=storage||global.localStorage;if(!s)return blank();const raw=s.getItem(STORAGE_KEY);return raw?normalize(JSON.parse(raw)):blank();}catch(e){return blank();}}
  function save(input,storage){const r=normalize(input);r.updatedAt=now();try{const s=storage||global.localStorage;if(s)s.setItem(STORAGE_KEY,JSON.stringify(r));}catch(e){}return r;}
  function clear(storage){try{const s=storage||global.localStorage;if(s)s.removeItem(STORAGE_KEY);}catch(e){}return blank();}
  const api={RELEASE_VERSION,PREVIOUS_RELEASE,ROLLBACK_RELEASE,SCHEMA,CERTIFICATE_SCHEMA,STORAGE_KEY,REQUIREMENTS,blank,normalize,evaluate,complete,certificate,load,save,clear};
  global.SCWorkspaceProductionSignoff=api;
  if(typeof module!=='undefined'&&module.exports){module.exports=api;}
})(typeof window!=='undefined'?window:globalThis);
