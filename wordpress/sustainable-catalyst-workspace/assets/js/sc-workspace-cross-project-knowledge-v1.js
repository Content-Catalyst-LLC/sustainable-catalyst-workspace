(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceCrossProjectKnowledge=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-cross-project-knowledge/1.0';
  const REFERENCE_SCHEMA='sc-workspace-cross-project-reference/1.0';
  const EXPORT_SCHEMA='sc-workspace-cross-project-knowledge-export/1.0';
  const STORAGE_KEY='sc_workspace_cross_project_knowledge_v1';
  const MAX_REFERENCES=500;
  const RELATIONS=new Set(['references','supports','contrasts','extends','related','informs']);
  const KINDS=new Set(['object','notebook','notebook-block','research-question','research-claim']);
  const text=(v,n=4000)=>String(v==null?'':v).trim().slice(0,n);
  const validIso=v=>Boolean(v&&typeof v==='string'&&!Number.isNaN(Date.parse(v)));
  const stamp=()=>new Date().toISOString();
  function token(value){let h=2166136261,s=String(value||'');for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return(h>>>0).toString(16).padStart(8,'0');}
  function sourceRef(raw={}){
    const kind=KINDS.has(raw.kind)?raw.kind:'object';
    return {kind,projectId:text(raw.projectId,160),id:text(raw.id,160),notebookId:text(raw.notebookId,160),sectionId:text(raw.sectionId,160)};
  }
  function normalizeReference(raw={},idFn){
    const createdAt=validIso(raw.createdAt)?raw.createdAt:stamp(),source=sourceRef(raw.source||raw.ref||{});
    if(!source.projectId||!source.id)return null;
    const targetProjectId=text(raw.targetProjectId,160);
    if(!targetProjectId||targetProjectId===source.projectId)return null;
    return {schema:REFERENCE_SCHEMA,id:text(raw.id,160)||(typeof idFn==='function'?idFn():`xpk-${token(`${targetProjectId}|${source.kind}|${source.projectId}|${source.id}|${createdAt}`)}`),targetProjectId,source,relation:RELATIONS.has(raw.relation)?raw.relation:'references',note:text(raw.note,3000),createdAt,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:createdAt};
  }
  function normalizeLedger(raw={},idFn){
    const refs=[],seen=new Set();
    for(const item of (Array.isArray(raw.references)?raw.references:[])){
      const ref=normalizeReference(item,idFn);if(!ref)continue;
      const key=`${ref.targetProjectId}|${ref.source.kind}|${ref.source.projectId}|${ref.source.id}|${ref.relation}`;
      if(seen.has(key)||refs.length>=MAX_REFERENCES)continue;seen.add(key);refs.push(ref);
    }
    return {schema:SCHEMA,references:refs,createdAt:validIso(raw.createdAt)?raw.createdAt:stamp(),updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp()};
  }
  function addReference(ledger,input,idFn){
    const next=normalizeLedger(ledger,idFn),ref=normalizeReference(input,idFn);if(!ref)return{ledger:next,reference:null,added:false,reason:'invalid'};
    const dupe=next.references.find(x=>x.targetProjectId===ref.targetProjectId&&x.source.kind===ref.source.kind&&x.source.projectId===ref.source.projectId&&x.source.id===ref.source.id&&x.relation===ref.relation);
    if(dupe)return{ledger:next,reference:dupe,added:false,reason:'duplicate'};
    if(next.references.length>=MAX_REFERENCES)return{ledger:next,reference:null,added:false,reason:'limit'};
    next.references.unshift(ref);next.updatedAt=stamp();return{ledger:next,reference:ref,added:true,reason:'added'};
  }
  function removeReference(ledger,id){const next=normalizeLedger(ledger),before=next.references.length;next.references=next.references.filter(x=>x.id!==id);if(next.references.length!==before)next.updatedAt=stamp();return next;}
  function integratedKey(source){if(!source)return'';if(source.kind==='notebook-block')return`notebook-block:${source.projectId}:${source.notebookId}:${source.id}`;return`${source.kind}:${source.projectId}:${source.id}`;}
  function resolve(ref,entries=[],projects=[]){
    const source=(Array.isArray(entries)?entries:[]).find(e=>e.key===integratedKey(ref.source))||null;
    const target=(Array.isArray(projects)?projects:[]).find(p=>p.id===ref.targetProjectId)||null;
    return {reference:ref,source,target,resolved:Boolean(source&&target),sourceMissing:!source,targetMissing:!target,crossProject:Boolean(source&&target&&source.projectId!==target.id)};
  }
  function resolvedRows(ledger,entries=[],projects=[]){return normalizeLedger(ledger).references.map(r=>resolve(r,entries,projects));}
  function stats(ledger,entries=[],projects=[]){const rows=resolvedRows(ledger,entries,projects);return{references:rows.length,resolved:rows.filter(r=>r.resolved).length,unresolved:rows.filter(r=>!r.resolved).length,targetProjects:new Set(rows.map(r=>r.reference.targetProjectId)).size,sourceProjects:new Set(rows.map(r=>r.reference.source.projectId)).size};}
  function forTarget(ledger,projectId){return normalizeLedger(ledger).references.filter(r=>r.targetProjectId===projectId);}
  function forSource(ledger,source){const key=integratedKey(source);return normalizeLedger(ledger).references.filter(r=>integratedKey(r.source)===key);}
  function fingerprint(ref){const r=normalizeReference(ref);return r?token(JSON.stringify({targetProjectId:r.targetProjectId,source:r.source,relation:r.relation,note:r.note,createdAt:r.createdAt})):'';}
  function exportPackage(ledger){const normalized=normalizeLedger(ledger);return{schema:EXPORT_SCHEMA,exportedAt:stamp(),ledger:normalized,integrity:{algorithm:'fnv1a32-cross-project-reference',references:normalized.references.map(r=>({id:r.id,fingerprint:fingerprint(r)}))}};}
  function verifyPackage(pkg){if(!pkg||pkg.schema!==EXPORT_SCHEMA)return{ok:false,reason:'schema'};const ledger=normalizeLedger(pkg.ledger),expected=new Map((pkg.integrity?.references||[]).map(x=>[String(x.id),String(x.fingerprint)]));for(const ref of ledger.references){if(expected.has(ref.id)&&expected.get(ref.id)!==fingerprint(ref))return{ok:false,reason:'fingerprint',ledger};}return{ok:true,reason:'verified',ledger};}
  function governance(){return{browserLocalLedger:true,canonicalSourcePointersOnly:true,copiesCanonicalContent:false,explicitTargetProjectRequired:true,sameProjectReferencesRejected:true,automaticRelationshipInference:false,automaticContentCopy:false,automaticCanonicalMutation:false,unresolvedReferencesRemainVisible:true,localFirst:true};}
  return {SCHEMA,REFERENCE_SCHEMA,EXPORT_SCHEMA,STORAGE_KEY,MAX_REFERENCES,RELATIONS,KINDS,sourceRef,normalizeReference,normalizeLedger,addReference,removeReference,integratedKey,resolve,resolvedRows,stats,forTarget,forSource,fingerprint,exportPackage,verifyPackage,governance};
});
