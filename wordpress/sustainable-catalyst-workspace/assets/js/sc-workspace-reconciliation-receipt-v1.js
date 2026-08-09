(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  if(root) root.SCWorkspaceReconciliationReceipt=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-reconciliation-receipt/1.0';
  const EXPORT_SCHEMA='sc-workspace-reconciliation-receipt-export/1.0';
  const clone=v=>JSON.parse(JSON.stringify(v));
  function cleanChange(item){return {key:String(item?.key||''),category:String(item?.category||''),kind:String(item?.kind||'content'),change:String(item?.change||''),id:String(item?.id||''),label:String(item?.label||''),fields:Array.isArray(item?.fields)?item.fields.map(String):[]};}
  function buildReceipt(input={}){
    const available=(input.availableChanges||[]).map(cleanChange), selectedKeys=new Set((input.selectedChanges||[]).map(x=>String(x?.key||x)));
    const accepted=available.filter(x=>selectedKeys.has(x.key)), declined=available.filter(x=>!selectedKeys.has(x.key));
    return {schema:SCHEMA,id:String(input.id||''),createdAt:String(input.createdAt||new Date().toISOString()),sourceProjectId:String(input.sourceProjectId||''),sourceProjectTitle:String(input.sourceProjectTitle||'Workspace project'),outputProjectId:String(input.outputProjectId||''),outputProjectTitle:String(input.outputProjectTitle||'Reconciled project'),receiptDocumentObjectId:String(input.receiptDocumentObjectId||''),reviewerLabel:String(input.reviewerLabel||'Workspace owner').slice(0,160),rationale:String(input.rationale||'').slice(0,4000),base:clone(input.base||{}),target:clone(input.target||{}),changeReviewSummary:clone(input.changeReviewSummary||{}),decision:{accepted,declined,blocked:Array.isArray(input.blockedChanges)?input.blockedChanges.map(cleanChange):[],acceptedCount:accepted.length,declinedCount:declined.length,blockedCount:Array.isArray(input.blockedChanges)?input.blockedChanges.length:0,dependencyValidation:String(input.dependencyValidation||'passed'),humanAcknowledged:Boolean(input.humanAcknowledged)},governance:{explicitHumanDecision:true,automaticSelection:false,automaticMerge:false,automaticOverwrite:false,sourceStatesMutated:false,receiptEditableInWorkspace:false,accountIdentityInferred:false},integrity:{algorithm:'SHA-256',fingerprint:''}};
  }
  function fingerprintPayload(receipt){const copy=clone(receipt);if(copy.integrity)copy.integrity.fingerprint='';return JSON.stringify(copy);}
  function withFingerprint(receipt,fingerprint){const copy=clone(receipt);copy.integrity={algorithm:'SHA-256',fingerprint:String(fingerprint||'')};return copy;}
  function exportPackage(receipt){return {schema:EXPORT_SCHEMA,exportedAt:new Date().toISOString(),receipt:clone(receipt),governance:{portableCopy:true,sourceProjectMutation:false,automaticApply:false}};}
  function toMarkdown(receipt){const d=receipt.decision||{},lines=[`# Reconciliation Decision Receipt`,``,`Receipt ID: ${receipt.id}`,`Created: ${receipt.createdAt}`,`Decision maker / reviewer: ${receipt.reviewerLabel}`,`Source project: ${receipt.sourceProjectTitle}`,`Reconciled project: ${receipt.outputProjectTitle}`,`Base: ${receipt.base?.label||'Base state'}`,`Target: ${receipt.target?.label||'Target state'}`,``,`## Decision rationale`,receipt.rationale||'(No rationale recorded.)',``,`## Decision summary`,`Accepted changes: ${d.acceptedCount||0}`,`Declined changes: ${d.declinedCount||0}`,`Blocked changes: ${d.blockedCount||0}`,`Dependency validation: ${d.dependencyValidation||'unknown'}`,`Human acknowledgement: ${d.humanAcknowledged?'yes':'no'}`,``,`## Accepted changes`];(d.accepted||[]).forEach(x=>lines.push(`- ${x.category} — ${x.change}: ${x.label}`));lines.push('', '## Declined changes');(d.declined||[]).forEach(x=>lines.push(`- ${x.category} — ${x.change}: ${x.label}`));lines.push('', '## Integrity',`SHA-256: ${receipt.integrity?.fingerprint||'unavailable'}`,'','This document summarizes the authoritative browser-local reconciliation receipt. Editing this Document object does not alter the receipt ledger.');return lines.join('\n');}
  return {SCHEMA,EXPORT_SCHEMA,cleanChange,buildReceipt,fingerprintPayload,withFingerprint,exportPackage,toMarkdown};
});
