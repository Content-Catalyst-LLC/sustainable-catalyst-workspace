(function(w){
  'use strict';
  const version='3.9.0';
  function api(){ return w.SCWorkspaceApi || null; }
  function invoke(name,args){
    const client=api();
    if(!client || typeof client[name] !== 'function') return Promise.reject(new Error('Workspace typed API method unavailable: '+name));
    return client[name](args||{});
  }
  w.SustainableCatalystInvestigationTimeline=Object.freeze({
    version,
    profile:()=>invoke('investigationTimelineWorkspace'),
    events:(projectId,limit)=>invoke('investigationEvents',{projectId:projectId||'',limit:limit||500}),
    event:(eventId)=>invoke('investigationEvent',{event_id:eventId}),
    storeEvent:(request)=>invoke('investigationEventStore',request),
    eventRevisions:(eventId,limit)=>invoke('investigationEventRevisions',{event_id:eventId,limit:limit||100}),
    linkStatement:(request)=>invoke('investigationEventStatementLinkCreate',request),
    eventStatementLinks:(projectId,eventId,limit)=>invoke('investigationEventStatementLinks',{projectId:projectId||'',eventId:eventId||'',limit:limit||1000}),
    relateEvents:(request)=>invoke('investigationEventRelationCreate',request),
    eventRelations:(projectId,eventId,limit)=>invoke('investigationEventRelations',{projectId:projectId||'',eventId:eventId||'',limit:limit||1000}),
    timeline:(projectId)=>invoke('investigationTimeline',{project_id:projectId}),
    reconstructionGraph:(projectId,includeInvestigationGraph)=>invoke('investigationReconstructionGraph',{project_id:projectId,includeInvestigationGraph:includeInvestigationGraph!==false}),
    temporalDiagnostics:(projectId)=>invoke('investigationTemporalDiagnostics',{project_id:projectId}),
    createSnapshot:(projectId,request)=>invoke('investigationTimelineSnapshotCreate',Object.assign({project_id:projectId},request||{})),
    snapshots:(projectId,limit)=>invoke('investigationTimelineSnapshots',{project_id:projectId,limit:limit||100})
  });
})(window);
