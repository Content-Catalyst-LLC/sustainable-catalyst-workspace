(function(w){
  'use strict';
  const api=w.SCWorkspaceApi||null;
  const v='3.8.0';
  function invoke(name,args){ if(!api||typeof api[name]!=='function') return Promise.reject(new Error('Workspace typed client unavailable')); return api[name](args||{}); }
  w.SustainableCatalystInvestigationGraph={version:v,profile:()=>invoke('investigationGraphWorkspace'),graph:(projectId)=>invoke('investigationGraph',{project_id:projectId}),contradictions:(projectId)=>invoke('investigationContradictions',{project_id:projectId}),hypothesisMatrix:(projectId)=>invoke('investigationHypothesisMatrix',{project_id:projectId}),coverage:(projectId)=>invoke('investigationCoverage',{project_id:projectId})};
})(window);
