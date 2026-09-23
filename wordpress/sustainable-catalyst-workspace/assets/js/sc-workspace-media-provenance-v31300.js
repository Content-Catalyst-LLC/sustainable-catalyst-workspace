(function(w){'use strict';
function api(){return w.SCWorkspaceApi||null;}
function call(name,params){var a=api();if(!a||typeof a.request!=='function')return Promise.reject(new Error('Workspace typed API unavailable'));return a.request(name,params||{});}
w.SCWorkspaceMediaProvenance={
 profile:function(){return call('mediaProvenanceWorkspace');},
 artifacts:function(params){return call('mediaArtifacts',params);},
 artifact:function(artifactId){return call('mediaArtifact',{artifact_id:artifactId});},
 graph:function(projectId,includeSpatialGraph){return call('mediaProvenanceGraph',{project_id:projectId,includeSpatialGraph:includeSpatialGraph!==false});},
 diagnostics:function(projectId){return call('mediaDiagnostics',{project_id:projectId});},
 integrity:function(projectId){return call('mediaIntegrity',{project_id:projectId});},
 boundaries:{automaticSimilarityMatching:false,automaticAuthenticityDetermination:false,automaticTruthDetermination:false}
};
})(window);
