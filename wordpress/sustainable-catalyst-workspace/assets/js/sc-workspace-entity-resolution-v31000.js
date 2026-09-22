(function(w){
  'use strict';
  const version='3.10.0';
  function api(){ return w.SCWorkspaceApi || null; }
  function invoke(name,args){ const c=api(); if(!c || typeof c[name] !== 'function') return Promise.reject(new Error('Workspace typed API method unavailable: '+name)); return c[name](args||{}); }
  w.SustainableCatalystEntityResolution=Object.freeze({
    version,
    profile:()=>invoke('entityResolutionWorkspace'),
    entities:(projectId,entityType,limit)=>invoke('entities',{projectId:projectId||'',entityType:entityType||'',limit:limit||500}),
    entity:(entityId)=>invoke('entity',{entity_id:entityId}),
    storeEntity:(request)=>invoke('entityStore',request),
    revisions:(entityId,limit)=>invoke('entityRevisions',{entity_id:entityId,limit:limit||100}),
    addAlias:(request)=>invoke('entityAliasCreate',request), aliases:(projectId,entityId,limit)=>invoke('entityAliases',{projectId:projectId||'',entityId:entityId||'',limit:limit||1000}),
    addIdentifier:(request)=>invoke('entityIdentifierCreate',request), identifiers:(projectId,entityId,limit)=>invoke('entityIdentifiers',{projectId:projectId||'',entityId:entityId||'',limit:limit||1000}),
    relate:(request)=>invoke('entityRelationshipCreate',request), relationships:(projectId,entityId,limit)=>invoke('entityRelationships',{projectId:projectId||'',entityId:entityId||'',limit:limit||1000}),
    linkContext:(request)=>invoke('entityContextLinkCreate',request), contextLinks:(projectId,entityId,limit)=>invoke('entityContextLinks',{projectId:projectId||'',entityId:entityId||'',limit:limit||1000}),
    createMatchCandidate:(request)=>invoke('entityMatchCandidateCreate',request), matchCandidates:(projectId,reviewState,limit)=>invoke('entityMatchCandidates',{projectId:projectId||'',reviewState:reviewState||'',limit:limit||1000}),
    reviewMatch:(candidateId,request)=>invoke('entityMatchCandidateReview',Object.assign({candidate_id:candidateId},request||{})),
    graph:(projectId,includeTimelineGraph)=>invoke('entityResolutionGraph',{project_id:projectId,includeTimelineGraph:includeTimelineGraph!==false}),
    diagnostics:(projectId)=>invoke('entityResolutionDiagnostics',{project_id:projectId}),
    createSnapshot:(projectId,request)=>invoke('entityResolutionSnapshotCreate',Object.assign({project_id:projectId},request||{})),
    snapshots:(projectId,limit)=>invoke('entityResolutionSnapshots',{project_id:projectId,limit:limit||100})
  });
})(window);
