(function(root){
'use strict';

const ALL=['knowledge','evidence','sources','data','analysis','timeline','decision','provenance'];

function base(){
  return {
    schema:'sc-workspace-personal-research-graph-demo/1.0',
    version:'3.81.0',
    projectId:'public-demo',
    project:{id:'public-demo',title:'Accelerated Weathering Research — Demo'},
    ownership:'public-demo-only',
    visibility:'demonstration',
    graphFingerprint:'demo-accelerated-weathering-v3810',
    availableLenses:ALL,
    nodes:[
      {id:'demo:project',kind:'project',label:'Accelerated Weathering Research',lenses:['knowledge','evidence','sources','data','analysis','timeline','decision','provenance']},
      {id:'demo:source1',kind:'source',label:'Peer-reviewed literature',lenses:['knowledge','evidence','sources','provenance']},
      {id:'demo:source2',kind:'source',label:'Inventory guidance',lenses:['knowledge','evidence','sources','provenance']},
      {id:'demo:evidence',kind:'statement',label:'Field dissolution evidence',lenses:['knowledge','evidence','provenance']},
      {id:'demo:dataset',kind:'dataset',label:'Soil chemistry dataset',lenses:['data','analysis','provenance']},
      {id:'demo:analysis',kind:'scientific-receipt',label:'Sensitivity analysis',lenses:['analysis','timeline','provenance']},
      {id:'demo:model',kind:'model',label:'Carbon removal model',lenses:['analysis','provenance']},
      {id:'demo:finding',kind:'study-package',label:'Site-sensitive outcome',lenses:['knowledge','evidence','analysis','decision','provenance']},
      {id:'demo:decision',kind:'reference',label:'Decision record',lenses:['decision','timeline','provenance']}
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

function graph(lens){
  const g=base(), active=(lens&&lens!=='all')?lens:'all';
  g.lens=active;
  if(active==='all'){g.nodeCount=g.nodes.length;g.edgeCount=g.edges.length;return g;}
  const keep=new Set(g.nodes.filter(n=>n.kind==='project'||(n.lenses||[]).includes(active)).map(n=>n.id));
  g.nodes=g.nodes.filter(n=>keep.has(n.id));
  g.edges=g.edges.filter(e=>keep.has(e.source)&&keep.has(e.target));
  g.nodeCount=g.nodes.length;g.edgeCount=g.edges.length;
  return g;
}

function renderDemo(lens){
  const rt=root.SCWorkspaceStandaloneRuntime;
  const panel=document.querySelector('[data-research-graph-workspace]');
  if(!rt||!rt.researchGraph||!panel)return false;
  const active=document.querySelector('[data-active]');
  const noProject=!active || /no active project/i.test(active.textContent||'');
  if(!noProject)return false;
  panel.dataset.demo='true';
  panel.dataset.lens=lens||'all';
  const intro=panel.querySelector('p');
  if(intro)intro.textContent='Interactive public demonstration. Open or create a project to replace this with your private, project-owned research graph.';
  rt.researchGraph.render(panel,graph(lens||'all'),next=>renderDemo(next));
  return true;
}

function boot(){
  renderDemo('all');
  const refresh=document.querySelector('[data-research-graph-refresh]');
  if(refresh)refresh.addEventListener('click',function(){
    const panel=document.querySelector('[data-research-graph-workspace]');
    if(panel&&panel.dataset.demo==='true')renderDemo(panel.dataset.lens||'all');
  });
}

document.addEventListener('sc-workspace-standalone:ready',boot,{once:true});
if(root.SCWorkspaceStandaloneRuntime){setTimeout(boot,0);}
root.SCWorkspacePublicResearchGraphDemo=Object.freeze({version:'3.81.0',graph,render:renderDemo});
})(globalThis);
