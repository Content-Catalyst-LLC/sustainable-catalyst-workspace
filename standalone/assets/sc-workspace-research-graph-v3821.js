(function(root){'use strict';
const V='3.82.1';
function create(options){
  const api=options.apiClient,shared=root.SCSharedResearchGraphRuntime.create();
  async function profile(){try{return await api.get('/v1/shared-research-graph/profile')}catch(e){return{version:V,error:String(e&&e.message||e)}}}
  async function demo(lens){const qs=lens&&lens!=='all'?'?lens='+encodeURIComponent(lens):'';try{return await api.get('/v1/shared-research-graph/demo'+qs)}catch(e){return null}}
  async function project(id,lens){if(!id)return demo(lens);const qs=lens&&lens!=='all'?'?lens='+encodeURIComponent(lens):'';try{return await api.get('/v1/shared-research-graph/projects/'+encodeURIComponent(id)+qs)}catch(e){return{version:V,authRequired:true,error:String(e&&e.message||e)}}}
  function render(panel,g,onLens){const host=panel.querySelector('[data-research-graph-map]');if(!host)return;const score=panel.querySelector('.research-graph-scorecard');if(score)score.hidden=true;const legacy=panel.querySelector('[data-research-graph-lenses]');if(legacy)legacy.hidden=true;shared.render(host,g,{onLens})}
  return Object.freeze({version:V,profile,demo,project,render,shared});
}
root.SCWorkspaceResearchGraphFactory=Object.freeze({version:V,create});
})(globalThis);