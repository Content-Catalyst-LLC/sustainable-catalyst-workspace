(function(global){
  'use strict';
  const RELEASE_VERSION='0.84.0';
  const PREVIOUS_RELEASE='0.83.0';
  const ROLLBACK_RELEASE='0.83.0';
  const PRODUCTION_SIGNOFF_RELEASE='0.83.0';
  const PRODUCTION_SIGNOFF_SCHEMA='sc-workspace-production-signoff-certificate/1.0';
  const SCHEMA='sc-workspace-ga-readiness/1.0';
  const DOSSIER_SCHEMA='sc-workspace-ga-readiness-dossier/1.0';
  const STORAGE_KEY='sc_workspace_ga_readiness_v1';
  const SIGNOFF_STORAGE_KEY='sc_workspace_production_signoff_v1';
  const REQUIREMENTS=[
    {id:'production-signoff-certificate',label:'Signed v0.83.0 production certificate',description:'The prior live-production sign-off record must be complete and signed before 1.0 readiness can become READY.'},
    {id:'current-release-identity',label:'Current v0.84.0 release identity',description:'The deployed WordPress plugin and health endpoint identify the current release as v0.84.0.'},
    {id:'release-lineage',label:'Release lineage',description:'Source, manifest, registry, cumulative assets, staged tree, and committed tree identify v0.84.0 with predecessor v0.83.0.'},
    {id:'package-integrity',label:'Package integrity',description:'The repository, WordPress artifact, manifest, release notes, validation report, installer, and verifier match the published checksum set.'},
    {id:'rollback-artifact',label:'v0.83.0 rollback artifact',description:'The exact v0.83.0 WordPress rollback package is retained and schema-compatible.'},
    {id:'current-wordpress-smoke',label:'Current WordPress smoke',description:'The live v0.84.0 page, REST identity, and cumulative assets are coherent after deployment.'},
    {id:'release-notes-review',label:'Release notes and scope review',description:'The release owner reviewed the v0.84.0 notes and confirmed no new product subsystem or schema migration entered the freeze.'},
    {id:'support-recovery-review',label:'Support and recovery readiness',description:'Operator recovery instructions, rollback path, and preserved local project boundary are understood before a future 1.0 release.'},
    {id:'no-known-blocking-defects',label:'No known blocking defects',description:'The release owner attests that any known blocking defect would keep this dossier on HOLD rather than be waived silently.'}
  ];
  function now(){return new Date().toISOString();}
  function blank(){const checks={};REQUIREMENTS.forEach(r=>checks[r.id]=false);return {schema:SCHEMA,releaseVersion:RELEASE_VERSION,previousRelease:PREVIOUS_RELEASE,rollbackRelease:ROLLBACK_RELEASE,releaseOwner:'',productionUrl:'https://sustainablecatalyst.com/platform/',checks,attestation:false,recordedAt:'',updatedAt:now()};}
  function normalize(input){const src=(input&&typeof input==='object')?input:{};const out=blank();out.releaseOwner=String(src.releaseOwner||'').trim();out.productionUrl=String(src.productionUrl||out.productionUrl).trim();out.attestation=src.attestation===true;out.recordedAt=String(src.recordedAt||'');out.updatedAt=String(src.updatedAt||now());REQUIREMENTS.forEach(r=>out.checks[r.id]=!!(src.checks&&src.checks[r.id]));return out;}
  function validUrl(value){try{const u=new URL(value);return u.protocol==='https:'||u.protocol==='http:';}catch(e){return false;}}
  function productionCertificate(storage){try{const s=storage||global.localStorage;if(!s)return null;const raw=s.getItem(SIGNOFF_STORAGE_KEY);if(!raw)return null;const record=JSON.parse(raw);const signoff=global.SCWorkspaceProductionSignoff;if(signoff&&typeof signoff.certificate==='function')return signoff.certificate(record);return null;}catch(e){return null;}}
  function validProductionCertificate(cert){return !!(cert&&cert.schema===PRODUCTION_SIGNOFF_SCHEMA&&cert.workspaceVersion===PRODUCTION_SIGNOFF_RELEASE&&cert.signedOff===true&&cert.status==='signed-off'&&cert.humanAttestation===true&&cert.requiredCheckCount===cert.attestedCheckCount);}
  function evaluate(input,cert){const r=normalize(input);const certificate=cert===undefined?productionCertificate():cert;const productionSigned=validProductionCertificate(certificate);const missing=REQUIREMENTS.filter(x=>x.id==='production-signoff-certificate'?!productionSigned:!r.checks[x.id]).map(x=>x.id);const ownerOk=r.releaseOwner.length>0;const urlOk=validUrl(r.productionUrl);const attestationOk=r.attestation===true;const ready=missing.length===0&&ownerOk&&urlOk&&attestationOk;return {ready,missing,ownerOk,urlOk,attestationOk,productionSigned,completedCount:REQUIREMENTS.length-missing.length,requiredCount:REQUIREMENTS.length};}
  function complete(input,cert,at){const r=normalize(input);const e=evaluate(r,cert);r.updatedAt=at||now();r.recordedAt=e.ready?(at||now()):'';return {record:r,evaluation:e};}
  function dossier(input,cert){const r=normalize(input);const certificate=cert===undefined?productionCertificate():cert;const e=evaluate(r,certificate);return {schema:DOSSIER_SCHEMA,workspaceVersion:RELEASE_VERSION,previousRelease:PREVIOUS_RELEASE,rollbackRelease:ROLLBACK_RELEASE,release:'Production Sign-Off Closure & 1.0 Release Readiness',status:e.ready?'ready-for-1.0-decision':'hold',readyForOneDotZeroDecision:e.ready,automaticPromotionToOneDotZero:false,productionSignoffRelease:PRODUCTION_SIGNOFF_RELEASE,productionSignoffSchema:PRODUCTION_SIGNOFF_SCHEMA,productionSignoffValid:e.productionSigned,productionSignoffSignedAt:(certificate&&certificate.signedAt)||'',releaseOwner:r.releaseOwner,productionUrl:r.productionUrl,recordedAt:e.ready?r.recordedAt:'',requiredCheckCount:REQUIREMENTS.length,completedCheckCount:e.completedCount,checks:REQUIREMENTS.map(x=>({id:x.id,label:x.label,complete:x.id==='production-signoff-certificate'?e.productionSigned:!!r.checks[x.id]})),humanAttestation:r.attestation===true,projectContentIncluded:false,automaticRollback:false,automaticCachePurge:false,telemetry:false};}
  function load(storage){try{const s=storage||global.localStorage;if(!s)return blank();const raw=s.getItem(STORAGE_KEY);return raw?normalize(JSON.parse(raw)):blank();}catch(e){return blank();}}
  function save(input,storage){const r=normalize(input);r.updatedAt=now();try{const s=storage||global.localStorage;if(s)s.setItem(STORAGE_KEY,JSON.stringify(r));}catch(e){}return r;}
  function clear(storage){try{const s=storage||global.localStorage;if(s)s.removeItem(STORAGE_KEY);}catch(e){}return blank();}
  const api={RELEASE_VERSION,PREVIOUS_RELEASE,ROLLBACK_RELEASE,PRODUCTION_SIGNOFF_RELEASE,PRODUCTION_SIGNOFF_SCHEMA,SCHEMA,DOSSIER_SCHEMA,STORAGE_KEY,SIGNOFF_STORAGE_KEY,REQUIREMENTS,blank,normalize,productionCertificate,validProductionCertificate,evaluate,complete,dossier,load,save,clear};
  global.SCWorkspaceGAReadiness=api;
  if(typeof module!=='undefined'&&module.exports){module.exports=api;}
})(typeof window!=='undefined'?window:globalThis);
