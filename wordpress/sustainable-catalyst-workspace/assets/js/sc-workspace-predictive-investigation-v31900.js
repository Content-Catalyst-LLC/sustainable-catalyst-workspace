(function(w){'use strict';
function api(path,opts){opts=opts||{};var base=(w.SC_WORKSPACE&&w.SC_WORKSPACE.restUrl)||'/wp-json/sc-workspace/v1/';var headers=Object.assign({'Content-Type':'application/json'},opts.headers||{});if(w.SC_WORKSPACE&&w.SC_WORKSPACE.nonce)headers['X-WP-Nonce']=w.SC_WORKSPACE.nonce;return fetch(base.replace(/\/$/,'/')+'backend/predictive-investigation-workspace'+path,Object.assign({},opts,{headers:headers})).then(function(r){return r.json();});}
function q(o){if(!o)return'';var p=new URLSearchParams();Object.keys(o).forEach(function(k){if(o[k]!==undefined&&o[k]!==null&&o[k]!=='')p.set(k,o[k]);});var s=p.toString();return s?'?'+s:'';}
w.SCWorkspacePredictiveInvestigation={
 profile:function(){return api('');},
 scenarios:function(x){return api('/scenarios'+q(x));},scenario:function(id){return api('/scenarios/'+encodeURIComponent(id));},scenarioRevisions:function(id,x){return api('/scenarios/'+encodeURIComponent(id)+'/revisions'+q(x));},storeScenario:function(x){return api('/scenarios',{method:'POST',body:JSON.stringify(x)});},
 modelBindings:function(x){return api('/model-bindings'+q(x));},createModelBinding:function(x){return api('/model-bindings',{method:'POST',body:JSON.stringify(x)});},
 forecastRequests:function(x){return api('/forecast-requests'+q(x));},createForecastRequest:function(x){return api('/forecast-requests',{method:'POST',body:JSON.stringify(x)});},
 resultBindings:function(x){return api('/result-bindings'+q(x));},createResultBinding:function(x){return api('/result-bindings',{method:'POST',body:JSON.stringify(x)});},
 comparisons:function(x){return api('/comparisons'+q(x));},createComparison:function(x){return api('/comparisons',{method:'POST',body:JSON.stringify(x)});},
 manifest:function(projectId){return api('/projects/'+encodeURIComponent(projectId)+'/manifest');},
 graph:function(projectId){return api('/projects/'+encodeURIComponent(projectId)+'/graph');},
 diagnostics:function(projectId){return api('/projects/'+encodeURIComponent(projectId)+'/diagnostics');},
 snapshots:function(projectId,x){return api('/projects/'+encodeURIComponent(projectId)+'/snapshots'+q(x));},
 createSnapshot:function(projectId,x){return api('/projects/'+encodeURIComponent(projectId)+'/snapshots',{method:'POST',body:JSON.stringify(x)});}
};
})(window);
