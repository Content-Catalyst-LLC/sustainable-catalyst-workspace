(function(w){'use strict';
function api(path,opts){opts=opts||{};var base=(w.SC_WORKSPACE&&w.SC_WORKSPACE.restUrl)||'/wp-json/sc-workspace/v1/';var headers=Object.assign({'Content-Type':'application/json'},opts.headers||{});if(w.SC_WORKSPACE&&w.SC_WORKSPACE.nonce)headers['X-WP-Nonce']=w.SC_WORKSPACE.nonce;return fetch(base.replace(/\/$/,'/')+'backend/causal-analysis-workspace'+path,Object.assign({},opts,{headers:headers})).then(function(r){return r.json();});}
function q(o){if(!o)return'';var p=new URLSearchParams();Object.keys(o).forEach(function(k){if(o[k]!==undefined&&o[k]!==null&&o[k]!=='')p.set(k,o[k]);});var s=p.toString();return s?'?'+s:'';}
w.SCWorkspaceCausalAnalysis={
 profile:function(){return api('');},
 questions:function(x){return api('/questions'+q(x));},
 question:function(id){return api('/questions/'+encodeURIComponent(id));},
 questionRevisions:function(id,x){return api('/questions/'+encodeURIComponent(id)+'/revisions'+q(x));},
 storeQuestion:function(x){return api('/questions',{method:'POST',body:JSON.stringify(x)});},
 structures:function(x){return api('/structures'+q(x));},createStructure:function(x){return api('/structures',{method:'POST',body:JSON.stringify(x)});},
 alternativeExplanations:function(x){return api('/alternative-explanations'+q(x));},createAlternativeExplanation:function(x){return api('/alternative-explanations',{method:'POST',body:JSON.stringify(x)});},
 identificationAssumptions:function(x){return api('/identification-assumptions'+q(x));},createIdentificationAssumption:function(x){return api('/identification-assumptions',{method:'POST',body:JSON.stringify(x)});},
 handoffs:function(x){return api('/handoffs'+q(x));},createHandoff:function(x){return api('/handoffs',{method:'POST',body:JSON.stringify(x)});},
 resultBindings:function(x){return api('/result-bindings'+q(x));},createResultBinding:function(x){return api('/result-bindings',{method:'POST',body:JSON.stringify(x)});},
 analysis:function(projectId){return api('/projects/'+encodeURIComponent(projectId)+'/analysis');},
 snapshots:function(projectId,x){return api('/projects/'+encodeURIComponent(projectId)+'/snapshots'+q(x));},
 createSnapshot:function(projectId,x){return api('/projects/'+encodeURIComponent(projectId)+'/snapshots',{method:'POST',body:JSON.stringify(x)});}
};
})(window);
