(function(){
'use strict';
function demoGraph(){
  return {
    schema:'sc-workspace-personal-research-graph-demo/1.0',
    version:'3.81.0',
    lens:'all',
    demo:true,
    availableLenses:['knowledge','evidence','sources','data','analysis','timeline','decision','provenance'],
    graphFingerprint:'demo-accelerated-weathering',
    nodeCount:9,edgeCount:12,
    nodes:[
      {id:'demo:project',kind:'project',label:'Accelerated Weathering Research'},
      {id:'demo:source1',kind:'source',label:'Peer-reviewed literature'},
      {id:'demo:source2',kind:'source',label:'Inventory guidance'},
      {id:'demo:evidence',kind:'statement',label:'Field dissolution evidence'},
      {id:'demo:dataset',kind:'dataset',label:'Soil chemistry dataset'},
      {id:'demo:analysis',kind:'scientific-receipt',label:'Sensitivity analysis'},
      {id:'demo:model',kind:'model',label:'Carbon removal model'},
      {id:'demo:finding',kind:'study-package',label:'Site-sensitive outcome'},
      {id:'demo:decision',kind:'reference',label:'Decision record'}
    ],
    edges:[
      {source:'demo:project',target:'demo:source1',relation:'contains-source'},
      {source:'demo:project',target:'demo:source2',relation:'contains-source'},
      {source:'demo:source1',target:'demo:evidence',relation:'supports'},
      {source:'demo:source2',target:'demo:evidence',relation:'constrains'},
      {source:'demo:project',target:'demo:dataset',relation:'contains-dataset'},
      {source:'demo:dataset',target:'demo:analysis',relation:'used-by'},
      {source:'demo:evidence',target:'demo:analysis',relation:'informs'},
      {source:'demo:analysis',target:'demo:model',relation:'parameterizes'},
      {source:'demo:model',target:'demo:finding',relation:'produces'},
      {source:'demo:evidence',target:'demo:finding',relation:'supports'},
      {source:'demo:finding',target:'demo:decision',relation:'informs'},
      {source:'demo:project',target:'demo:decision',relation:'contains-decision'}
    ]
  };
}
function patch(){
  var rt=window.SCWorkspaceStandaloneRuntime;
  if(!rt||!rt.researchGraph||rt.researchGraph.__demoPatched)return false;
  var original=rt.researchGraph.project.bind(rt.researchGraph);
  rt.researchGraph.project=async function(id,lens){
    if(!id){var g=demoGraph();g.lens=lens||'all';return g}
    try{
      var result=await original(id,lens);
      if(result&&result.authRequired){var g=demoGraph();g.lens=lens||'all';g.demoReason='authentication-required';return g}
      return result;
    }catch(e){var g=demoGraph();g.lens=lens||'all';g.demoReason='project-unavailable';return g}
  };
  rt.researchGraph.__demoPatched=true;
  return true;
}
function init(){
  if(patch())return;
  var tries=0,t=setInterval(function(){tries++;if(patch()||tries>80)clearInterval(t)},100);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();