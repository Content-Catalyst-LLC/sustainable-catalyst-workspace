(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspacePersistenceIntegrity=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-persistence-integrity/1.0';
  const TRANSACTION_SCHEMA='sc-workspace-persistence-transaction/1.0';
  const REPORT_SCHEMA='sc-workspace-persistence-integrity-report/1.0';
  const RECOVERY_SCHEMA='sc-workspace-recovery-candidate/1.0';
  const CURRENT_KEY='sc_workspace';
  const LAST_GOOD_KEY='sc_workspace_last_good_v1';
  const QUARANTINE_KEY='sc_workspace_recovery_v0_8_2';
  const METADATA_KEY='sc_workspace_persistence_integrity_v0620';
  const TRANSACTION_KEY='sc_workspace_persistence_txn_v0620';
  const ALGORITHM='fnv1a32';
  const text=(v,max=240)=>String(v==null?'':v).trim().slice(0,max);
  const now=()=>new Date().toISOString();
  function bytes(raw){
    const s=String(raw==null?'':raw);
    try{return typeof TextEncoder!=='undefined'?new TextEncoder().encode(s).length:s.length*2;}catch(_){return s.length*2;}
  }
  function checksum(raw){
    const s=String(raw==null?'':raw);let h=0x811c9dc5;
    for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}
    return h.toString(16).padStart(8,'0');
  }
  function fingerprint(raw){return {algorithm:ALGORITHM,checksum:checksum(raw),bytes:bytes(raw)};}
  function readableWorkspace(raw){
    if(typeof raw!=='string'||!raw)return false;
    try{const parsed=JSON.parse(raw);return Boolean(parsed&&typeof parsed==='object'&&Array.isArray(parsed.projects));}catch(_){return false;}
  }
  function getJson(storage,key){try{return JSON.parse(storage?.getItem(key)||'null');}catch(_){return null;}}
  function setJson(storage,key,value){try{storage?.setItem(key,JSON.stringify(value));return true;}catch(_){return false;}}
  function remove(storage,key){try{storage?.removeItem(key);return true;}catch(_){return false;}}
  function lastGoodState(storage){
    const env=getJson(storage,LAST_GOOD_KEY);
    if(!env||env.schema!=='sc-workspace-last-known-good/1.0'||!readableWorkspace(env.raw))return {state:'missing-or-invalid',available:false,verified:false,envelope:env||null};
    const fp=fingerprint(env.raw);const recorded=env.integrity&&env.integrity.algorithm===ALGORITHM?env.integrity:null;
    const verified=!recorded||(recorded.checksum===fp.checksum&&Number(recorded.bytes)===fp.bytes);
    return {state:recorded?(verified?'verified':'integrity-drift'):'legacy',available:true,verified,legacy:!recorded,envelope:env,fingerprint:fp};
  }
  function metadataState(storage,currentRaw){
    const meta=getJson(storage,METADATA_KEY);
    if(!meta||meta.schema!==SCHEMA)return {state:'untracked',available:false,metadata:meta||null};
    if(!currentRaw)return {state:'metadata-without-current',available:true,metadata:meta};
    const fp=fingerprint(currentRaw);const matches=meta.algorithm===ALGORITHM&&meta.currentChecksum===fp.checksum&&Number(meta.currentBytes)===fp.bytes;
    return {state:matches?'verified':'integrity-drift',available:true,verified:matches,metadata:meta,fingerprint:fp};
  }
  function transactionState(storage,currentRaw){
    const tx=getJson(storage,TRANSACTION_KEY);
    if(!tx||tx.schema!==TRANSACTION_SCHEMA)return {state:'clean',available:false,transaction:tx||null};
    const fp=currentRaw?fingerprint(currentRaw):null;
    const targetMatches=Boolean(fp&&fp.checksum===tx.targetChecksum&&fp.bytes===Number(tx.targetBytes));
    const previousMatches=Boolean(fp&&tx.previousChecksum&&fp.checksum===tx.previousChecksum&&fp.bytes===Number(tx.previousBytes));
    let state=tx.status==='failed'?'failed':targetMatches?'commit-visible':previousMatches?'prewrite-visible':'interrupted';
    return {state,available:true,targetMatches,previousMatches,transaction:tx,currentFingerprint:fp};
  }
  function captureLastGood(storage,previousRaw,storageSchemaVersion){
    if(!readableWorkspace(previousRaw))return false;
    const fp=fingerprint(previousRaw);
    return setJson(storage,LAST_GOOD_KEY,{schema:'sc-workspace-last-known-good/1.0',capturedAt:now(),storageSchemaVersion:Number(storageSchemaVersion)||0,raw:previousRaw,integrity:fp});
  }
  function stage(storage,{previousRaw='',nextRaw='',workspaceVersion='',storageSchemaVersion=0}={}){
    const nextFp=fingerprint(nextRaw),previousFp=previousRaw?fingerprint(previousRaw):null;
    const lastGoodCaptured=captureLastGood(storage,previousRaw,storageSchemaVersion);
    const tx={schema:TRANSACTION_SCHEMA,transactionId:`txn_${Date.now()}_${Math.random().toString(36).slice(2,9)}`,startedAt:now(),workspaceVersion:text(workspaceVersion,40),storageSchemaVersion:Number(storageSchemaVersion)||0,status:'prepared',algorithm:ALGORITHM,previousChecksum:previousFp?.checksum||'',previousBytes:previousFp?.bytes||0,targetChecksum:nextFp.checksum,targetBytes:nextFp.bytes,lastGoodCaptured};
    const journalWritten=setJson(storage,TRANSACTION_KEY,tx);
    return {ok:journalWritten,transaction:tx,lastGoodCaptured};
  }
  function writeMetadata(storage,raw,workspaceVersion='',storageSchemaVersion=0,transactionId=''){
    const fp=fingerprint(raw),lastGood=lastGoodState(storage);
    return setJson(storage,METADATA_KEY,{schema:SCHEMA,verifiedAt:now(),workspaceVersion:text(workspaceVersion,40),storageSchemaVersion:Number(storageSchemaVersion)||0,algorithm:ALGORITHM,currentChecksum:fp.checksum,currentBytes:fp.bytes,lastGoodChecksum:lastGood.available?lastGood.fingerprint.checksum:'',transactionId:text(transactionId,120),canonicalKey:CURRENT_KEY,integrityPurpose:'corruption-detection-not-security'});
  }
  function commit(storage,raw,{workspaceVersion='',storageSchemaVersion=0}={}){
    const tx=getJson(storage,TRANSACTION_KEY);const current=storage?.getItem(CURRENT_KEY)||'';
    if(current!==String(raw))return {ok:false,reason:'read-after-write-mismatch',metadataWritten:false,journalCleared:false};
    const metadataWritten=writeMetadata(storage,current,workspaceVersion,storageSchemaVersion,tx?.transactionId||'');
    if(!metadataWritten)return {ok:false,reason:'integrity-metadata-write-failed',metadataWritten:false,journalCleared:false,fingerprint:fingerprint(current)};
    const journalCleared=remove(storage,TRANSACTION_KEY);
    if(!journalCleared)return {ok:false,reason:'transaction-journal-clear-failed',metadataWritten:true,journalCleared:false,fingerprint:fingerprint(current)};
    return {ok:true,metadataWritten:true,journalCleared:true,fingerprint:fingerprint(current)};
  }
  function fail(storage,error){
    const tx=getJson(storage,TRANSACTION_KEY);
    if(!tx||tx.schema!==TRANSACTION_SCHEMA)return false;
    tx.status='failed';tx.failedAt=now();tx.error=text(error?.message||error||'write-failed',180);
    return setJson(storage,TRANSACTION_KEY,tx);
  }
  function reconcileJournal(storage,{workspaceVersion='',storageSchemaVersion=0}={}){
    const current=storage?.getItem(CURRENT_KEY)||'';const t=transactionState(storage,current);
    if(!t.available)return {state:'clean',canonicalMutation:false};
    if(t.targetMatches){
      const metadataWritten=writeMetadata(storage,current,workspaceVersion,storageSchemaVersion,t.transaction?.transactionId||'');
      const journalCleared=metadataWritten?remove(storage,TRANSACTION_KEY):false;
      return metadataWritten&&journalCleared?{state:'resolved-committed',canonicalMutation:false}:{state:'interrupted',reason:metadataWritten?'transaction-journal-clear-failed':'integrity-metadata-write-failed',canonicalMutation:false,transaction:t.transaction};
    }
    if(t.previousMatches){
      const metadataWritten=writeMetadata(storage,current,workspaceVersion,storageSchemaVersion,'');
      const journalCleared=metadataWritten?remove(storage,TRANSACTION_KEY):false;
      return metadataWritten&&journalCleared?{state:'resolved-prewrite',canonicalMutation:false}:{state:'interrupted',reason:metadataWritten?'transaction-journal-clear-failed':'integrity-metadata-write-failed',canonicalMutation:false,transaction:t.transaction};
    }
    return {state:t.state,canonicalMutation:false,transaction:t.transaction};
  }
  function inspect(storage){
    let currentRaw='';try{currentRaw=storage?.getItem(CURRENT_KEY)||'';}catch(_){}
    const current={state:currentRaw?(readableWorkspace(currentRaw)?'readable':'invalid'):'missing',fingerprint:currentRaw?fingerprint(currentRaw):null};
    const metadata=metadataState(storage,currentRaw),lastGood=lastGoodState(storage),transaction=transactionState(storage,currentRaw);
    let quarantine=false;try{quarantine=Boolean(storage?.getItem(QUARANTINE_KEY));}catch(_){}
    const attention=current.state==='invalid'||metadata.state==='integrity-drift'||lastGood.state==='integrity-drift'||['failed','interrupted'].includes(transaction.state);
    const limited=!attention&&(metadata.state==='untracked'||lastGood.state==='legacy'||current.state==='missing');
    return {schema:REPORT_SCHEMA,generatedAt:now(),state:attention?'attention':limited?'limited':'ready',current,metadata,lastGood,transaction,quarantine,governance:{canonicalMutation:false,automaticRepair:false,automaticRestore:false,automaticUpload:false,telemetry:false,checksumSecurityClaim:false}};
  }
  function recoveryCandidate(storage,kind='current',workspaceVersion=''){
    const selected=kind==='last-known-good'?'last-known-good':'current';let raw='',capturedAt=now(),source='';
    if(selected==='last-known-good'){
      const last=lastGoodState(storage);if(!last.available)return null;raw=last.envelope.raw;capturedAt=last.envelope.capturedAt||capturedAt;source=LAST_GOOD_KEY;
    }else{try{raw=storage?.getItem(CURRENT_KEY)||'';}catch(_){} if(!raw)return null;source=CURRENT_KEY;}
    return {schema:RECOVERY_SCHEMA,exportedAt:now(),workspaceVersion:text(workspaceVersion,40),candidateType:selected,sourceKey:source,capturedAt,integrity:fingerprint(raw),readableWorkspace:readableWorkspace(raw),raw,privacy:{containsCanonicalWorkspaceContent:true,automaticUpload:false,automaticSubmission:false},governance:{applyMode:'manual-review-only',automaticRestore:false,canonicalMutation:false}};
  }
  function diagnosticSnapshot(storage,workspaceVersion=''){
    const a=inspect(storage);return {schema:REPORT_SCHEMA,generatedAt:a.generatedAt,workspaceVersion:text(workspaceVersion,40),state:a.state,current:{state:a.current.state,fingerprint:a.current.fingerprint},metadata:{state:a.metadata.state,available:a.metadata.available},lastGood:{state:a.lastGood.state,available:a.lastGood.available,verified:a.lastGood.verified||false},transaction:{state:a.transaction.state,available:a.transaction.available},quarantine:a.quarantine,privacy:{projectContentIncluded:false,rawStateIncluded:false,automaticTelemetry:false,automaticSubmission:false},governance:a.governance};
  }
  return Object.freeze({SCHEMA,TRANSACTION_SCHEMA,REPORT_SCHEMA,RECOVERY_SCHEMA,CURRENT_KEY,LAST_GOOD_KEY,QUARANTINE_KEY,METADATA_KEY,TRANSACTION_KEY,ALGORITHM,bytes,checksum,fingerprint,readableWorkspace,lastGoodState,metadataState,transactionState,captureLastGood,stage,commit,fail,reconcileJournal,inspect,recoveryCandidate,diagnosticSnapshot});
});
