(function(w){
  'use strict';
  const version='3.11.0';
  function api(){ return w.SCWorkspaceApi || null; }
  function invoke(name,args){ const c=api(); if(!c || typeof c[name] !== 'function') return Promise.reject(new Error('Workspace typed API method unavailable: '+name)); return c[name](...(Array.isArray(args)?args:[args])); }
  w.SustainableCatalystDocumentaryEvidence=Object.freeze({
    version,
    profile:()=>api().documentaryEvidenceWorkspace(),
    documents:(projectId,documentType,limit)=>api().documents(projectId||'',documentType||'',limit||500),
    document:(documentId)=>api().document(documentId),
    storeDocument:(request)=>api().storeDocument(request),
    revisions:(documentId,limit)=>api().documentRevisions(documentId,limit||100),
    addExcerpt:(request)=>api().createDocumentExcerpt(request),
    excerpts:(projectId,documentId,limit)=>api().documentExcerpts(projectId||'',documentId||'',limit||1000),
    testimonies:(projectId,speakerEntityId,limit)=>api().testimonies(projectId||'',speakerEntityId||'',limit||500),
    testimony:(testimonyId)=>api().testimony(testimonyId),
    storeTestimony:(request)=>api().storeTestimony(request),
    testimonyRevisions:(testimonyId,limit)=>api().testimonyRevisions(testimonyId,limit||100),
    linkContext:(request)=>api().createDocumentaryContextLink(request),
    contextLinks:(projectId,sourceId,targetRef,limit)=>api().documentaryContextLinks(projectId||'',sourceId||'',targetRef||'',limit||1000),
    relateTestimony:(request)=>api().createTestimonyRelation(request),
    testimonyRelations:(projectId,testimonyId,limit)=>api().testimonyRelations(projectId||'',testimonyId||'',limit||1000),
    graph:(projectId,includeEntityGraph)=>api().documentaryGraph(projectId,includeEntityGraph!==false),
    analysis:(projectId)=>api().documentaryAnalysis(projectId),
    createSnapshot:(projectId,request)=>api().createDocumentarySnapshot(projectId,request||{schema:'sc-workspace-investigation-documentary-snapshot-request/1.0',includeEntityGraph:true}),
    snapshots:(projectId,limit)=>api().documentarySnapshots(projectId,limit||100)
  });
})(window);
