(function(root){'use strict';
const VERSION='3.82.1';
const NS='http://www.w3.org/2000/svg';

function unique(xs){return Array.from(new Set(xs.filter(Boolean)))}
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
function hash(s){let h=2166136261;for(const ch of String(s)){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}

function create(){
  let state={
    graph:null,lens:'all',query:'',kindFilters:new Set(),relationFilters:new Set(),
    selected:null,hovered:null,zoom:1,panX:0,panY:0,layout:'force',
    collapsedGroups:new Set(),pinned:new Map(),positions:new Map(),container:null,
    showLabels:true,showEdgeLabels:false,fullscreen:false
  };

  function filtered(){
    const g=state.graph||{nodes:[],edges:[]},q=state.query.trim().toLowerCase();
    let nodes=(g.nodes||[]).filter(n=>{
      const group=n.group||n.kind;
      if(state.kindFilters.size&&!state.kindFilters.has(group))return false;
      if(q&&!(`${n.label||''} ${n.summary||''} ${n.kind||''} ${n.id||''}`.toLowerCase().includes(q)))return false;
      return true;
    });
    const collapsed=new Set(state.collapsedGroups);
    if(collapsed.size){
      nodes=nodes.filter(n=>!collapsed.has(n.group||n.kind)||(n.group||n.kind)==='project');
    }
    const ids=new Set(nodes.map(n=>n.id));
    const edges=(g.edges||[]).filter(e=>ids.has(e.source)&&ids.has(e.target)&&(!state.relationFilters.size||state.relationFilters.has(e.relation)));
    return {nodes,edges};
  }

  function adjacency(edges){
    const m=new Map();
    edges.forEach(e=>{
      if(!m.has(e.source))m.set(e.source,new Set());
      if(!m.has(e.target))m.set(e.target,new Set());
      m.get(e.source).add(e.target);m.get(e.target).add(e.source);
    });
    return m;
  }

  function seedPosition(n,i,w,h){
    const hsh=hash(n.id),a=(hsh%6283)/1000,r=90+((hsh>>>8)%270);
    return {x:w/2+Math.cos(a)*r,y:h/2+Math.sin(a)*r,vx:0,vy:0};
  }

  function forceLayout(nodes,edges,w,h){
    const pos=new Map();
    nodes.forEach((n,i)=>pos.set(n.id,state.pinned.get(n.id)||state.positions.get(n.id)||seedPosition(n,i,w,h)));
    const project=nodes.find(n=>(n.group||n.kind)==='project');
    if(project&&!state.pinned.has(project.id))pos.set(project.id,{x:w/2,y:h/2,vx:0,vy:0});
    for(let step=0;step<85;step++){
      for(let i=0;i<nodes.length;i++){
        const a=pos.get(nodes[i].id);
        for(let j=i+1;j<nodes.length;j++){
          const b=pos.get(nodes[j].id),dx=a.x-b.x,dy=a.y-b.y,d2=Math.max(1600,dx*dx+dy*dy),f=3000/d2;
          const d=Math.sqrt(d2),fx=dx/d*f,fy=dy/d*f;
          if(!state.pinned.has(nodes[i].id)){a.vx=(a.vx||0)+fx;a.vy=(a.vy||0)+fy}
          if(!state.pinned.has(nodes[j].id)){b.vx=(b.vx||0)-fx;b.vy=(b.vy||0)-fy}
        }
      }
      edges.forEach(e=>{
        const a=pos.get(e.source),b=pos.get(e.target);if(!a||!b)return;
        const dx=b.x-a.x,dy=b.y-a.y,d=Math.max(1,Math.sqrt(dx*dx+dy*dy)),target=150,k=(d-target)*0.0028,fx=dx/d*k,fy=dy/d*k;
        if(!state.pinned.has(e.source)){a.vx=(a.vx||0)+fx;a.vy=(a.vy||0)+fy}
        if(!state.pinned.has(e.target)){b.vx=(b.vx||0)-fx;b.vy=(b.vy||0)-fy}
      });
      nodes.forEach(n=>{
        const p=pos.get(n.id);if(state.pinned.has(n.id))return;
        p.vx=((p.vx||0)+(w/2-p.x)*0.0007)*0.78;p.vy=((p.vy||0)+(h/2-p.y)*0.0007)*0.78;
        p.x=clamp(p.x+p.vx,55,w-55);p.y=clamp(p.y+p.vy,55,h-55);
      });
    }
    return pos;
  }

  function clusterLayout(nodes,w,h){
    const groups=unique(nodes.map(n=>n.group||n.kind)).sort(),pos=new Map();
    const cols=Math.max(1,Math.ceil(Math.sqrt(groups.length))),cw=w/cols,ch=h/Math.ceil(groups.length/cols);
    groups.forEach((g,gi)=>{
      const arr=nodes.filter(n=>(n.group||n.kind)===g),cx=(gi%cols+.5)*cw,cy=(Math.floor(gi/cols)+.5)*ch;
      arr.forEach((n,i)=>{const a=(i/Math.max(1,arr.length))*Math.PI*2,r=arr.length===1?0:Math.min(cw,ch)*.27;pos.set(n.id,state.pinned.get(n.id)||{x:cx+Math.cos(a)*r,y:cy+Math.sin(a)*r,vx:0,vy:0})})
    });
    return pos;
  }

  function timelineLayout(nodes,w,h){
    const pos=new Map(),sorted=[...nodes].sort((a,b)=>String(a.createdAt||a.updatedAt||a.id).localeCompare(String(b.createdAt||b.updatedAt||b.id)));
    const groups=unique(nodes.map(n=>n.group||n.kind)).sort();
    sorted.forEach((n,i)=>{
      const x=70+(i/Math.max(1,sorted.length-1))*(w-140),gi=Math.max(0,groups.indexOf(n.group||n.kind)),y=90+gi*(Math.min(70,(h-180)/Math.max(1,groups.length-1)));
      pos.set(n.id,state.pinned.get(n.id)||{x,y,vx:0,vy:0});
    });
    return pos;
  }

  function provenanceLayout(nodes,edges,w,h){
    const pos=new Map(),incoming=new Map(),level=new Map(),project=nodes.find(n=>(n.group||n.kind)==='project');
    nodes.forEach(n=>incoming.set(n.id,0));edges.forEach(e=>incoming.set(e.target,(incoming.get(e.target)||0)+1));
    let roots=nodes.filter(n=>(incoming.get(n.id)||0)===0);if(project&&!roots.some(n=>n.id===project.id))roots.unshift(project);
    roots.forEach(n=>level.set(n.id,0));
    for(let pass=0;pass<nodes.length;pass++)edges.forEach(e=>{if(level.has(e.source))level.set(e.target,Math.max(level.get(e.target)||0,level.get(e.source)+1))});
    nodes.forEach(n=>{if(!level.has(n.id))level.set(n.id,1)});
    const max=Math.max(...level.values(),1);
    for(let l=0;l<=max;l++){
      const arr=nodes.filter(n=>level.get(n.id)===l);arr.forEach((n,i)=>{const x=90+l*((w-180)/Math.max(1,max)),y=80+(i+1)*(h-160)/(arr.length+1);pos.set(n.id,state.pinned.get(n.id)||{x,y,vx:0,vy:0})});
    }
    return pos;
  }

  function positionsFor(nodes,edges,w,h){
    let p;
    if(state.layout==='cluster')p=clusterLayout(nodes,w,h);
    else if(state.layout==='timeline')p=timelineLayout(nodes,w,h);
    else if(state.layout==='provenance')p=provenanceLayout(nodes,edges,w,h);
    else p=forceLayout(nodes,edges,w,h);
    state.positions=p;return p;
  }

  function relatedSet(id,edges){
    if(!id)return new Set();
    const s=new Set([id]);edges.forEach(e=>{if(e.source===id)s.add(e.target);if(e.target===id)s.add(e.source)});return s;
  }

  function inspect(n,edges,inspector){
    state.selected=n?n.id:null;
    if(!n){inspector.innerHTML='<h3>RESEARCH INSPECTOR</h3><p>Select a node to inspect context, provenance and direct relationships.</p>';return}
    const direct=edges.filter(e=>e.source===n.id||e.target===n.id);
    inspector.innerHTML='<h3>RESEARCH INSPECTOR</h3><span class="sgr-type"></span><h4></h4><p class="sgr-summary"></p><hr><h3>PROVENANCE</h3><p class="sgr-prov"></p><hr><h3>DIRECT TRACE</h3><div class="sgr-trace"></div><hr><button class="sgr-action" data-connected>Show only connected</button><button class="sgr-action" data-pin>Pin / unpin</button>';
    inspector.querySelector('.sgr-type').textContent=(n.group||n.kind||'object').toUpperCase();
    inspector.querySelector('h4').textContent=n.label||n.id;
    inspector.querySelector('.sgr-summary').textContent=n.summary||'Research object in the current graph.';
    inspector.querySelector('.sgr-prov').textContent=`${n.sourceProduct||state.graph.sourceProduct||'workspace'} · ${n.authority||'project authority'} · ${n.provenanceInspectable===false?'limited':'inspectable'}`;
    const trace=inspector.querySelector('.sgr-trace');
    if(!direct.length)trace.textContent='No visible direct relationships.';
    direct.forEach(e=>{
      const other=e.source===n.id?e.target:e.source,x=(state.graph.nodes||[]).find(z=>z.id===other),b=document.createElement('button');
      b.type='button';b.textContent=`${e.relation} → ${(x&&x.label)||other}`;b.onclick=()=>{if(x){inspect(x,filtered().edges,inspector);drawCurrent()}};trace.appendChild(b);
    });
    inspector.querySelector('[data-connected]').onclick=()=>{state.query='';state.kindFilters.clear();state.relationFilters.clear();state.connectedOnly=n.id;drawCurrent()};
    inspector.querySelector('[data-pin]').onclick=()=>{if(state.pinned.has(n.id))state.pinned.delete(n.id);else{const p=state.positions.get(n.id);if(p)state.pinned.set(n.id,{...p})}drawCurrent()};
  }

  let drawCurrent=()=>{};

  function render(container,graph,opts={}){
    state.graph=graph;state.container=container;state.lens=graph.lens||'all';state.query='';state.kindFilters.clear();state.relationFilters.clear();state.selected=null;state.hovered=null;state.zoom=1;state.panX=0;state.panY=0;state.connectedOnly=null;state.pinned.clear();
    container.innerHTML='';container.className='shared-research-graph sgr-v3821';

    const head=document.createElement('div');head.className='sgr-head';head.innerHTML='<div><span class="sgr-kicker">SHARED RESEARCH GRAPH / VISUAL INTERACTION ENGINE</span><strong></strong><small></small></div><div class="sgr-head-actions"><input type="search" placeholder="Search graph…" data-sgr-search><button data-fullscreen>Full screen</button><button data-sgr-reset>Reset</button></div>';
    head.querySelector('strong').textContent=(graph.project&&graph.project.title)||'Research graph';head.querySelector('small').textContent=graph.publicDemo?'Interactive public demonstration':'Project-owned research graph';container.appendChild(head);

    const toolbar=document.createElement('div');toolbar.className='sgr-toolbar';toolbar.innerHTML='<div class="sgr-layouts"><button data-layout="force" class="active">Force</button><button data-layout="cluster">Clusters</button><button data-layout="timeline">Timeline</button><button data-layout="provenance">Provenance</button></div><div><button data-toggle-labels>Labels</button><button data-toggle-edges>Edge labels</button><button data-collapse>Collapse groups</button></div>';container.appendChild(toolbar);

    const metrics=document.createElement('div');metrics.className='sgr-metrics';container.appendChild(metrics);
    const lensbar=document.createElement('div');lensbar.className='sgr-lenses';container.appendChild(lensbar);

    const body=document.createElement('div');body.className='sgr-body';const left=document.createElement('aside');left.className='sgr-filters';const stage=document.createElement('div');stage.className='sgr-stage';const right=document.createElement('aside');right.className='sgr-inspector';body.append(left,stage,right);container.appendChild(body);

    const mini=document.createElement('div');mini.className='sgr-minimap';stage.appendChild(mini);
    const foot=document.createElement('div');foot.className='sgr-foot';foot.innerHTML='<span>Shared renderer · product authority preserved</span><span>Drag nodes · pan background · wheel zoom · hover neighborhood</span>';container.appendChild(foot);

    function renderLens(){lensbar.innerHTML='';['all'].concat(graph.availableLenses||[]).forEach(l=>{const b=document.createElement('button');b.type='button';b.textContent=l;b.className=(state.lens===l?'active':'');b.onclick=()=>opts.onLens&&opts.onLens(l);lensbar.appendChild(b)})}

    function renderFilters(){
      left.innerHTML='<h3>LAYERS & FILTERS</h3>';
      unique((graph.nodes||[]).map(n=>n.group||n.kind)).sort().forEach(k=>{const lab=document.createElement('label');lab.innerHTML='<input type="checkbox" checked> <span></span>';lab.querySelector('span').textContent=k;lab.querySelector('input').onchange=e=>{if(e.target.checked)state.kindFilters.delete(k);else state.kindFilters.add(k);draw()};left.appendChild(lab)});
      left.appendChild(document.createElement('hr'));const h=document.createElement('h3');h.textContent='RELATIONSHIPS';left.appendChild(h);
      unique((graph.edges||[]).map(e=>e.relation)).sort().forEach(r=>{const lab=document.createElement('label');lab.innerHTML='<input type="checkbox" checked> <span></span>';lab.querySelector('span').textContent=r;lab.querySelector('input').onchange=e=>{if(e.target.checked)state.relationFilters.delete(r);else state.relationFilters.add(r);draw()};left.appendChild(lab)});
    }

    function activeFiltered(){
      let x=filtered();
      if(state.connectedOnly){
        const keep=relatedSet(state.connectedOnly,x.edges);x.nodes=x.nodes.filter(n=>keep.has(n.id));const ids=new Set(x.nodes.map(n=>n.id));x.edges=x.edges.filter(e=>ids.has(e.source)&&ids.has(e.target));
      }
      return x;
    }

    function drawMini(nodes,edges,pos,w,h){
      mini.innerHTML='';const svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox',`0 0 ${w} ${h}`);
      edges.forEach(e=>{const a=pos.get(e.source),b=pos.get(e.target);if(!a||!b)return;const l=document.createElementNS(NS,'line');l.setAttribute('x1',a.x);l.setAttribute('y1',a.y);l.setAttribute('x2',b.x);l.setAttribute('y2',b.y);svg.appendChild(l)});
      nodes.forEach(n=>{const p=pos.get(n.id);if(!p)return;const c=document.createElementNS(NS,'circle');c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);c.setAttribute('r',(n.group||n.kind)==='project'?12:6);svg.appendChild(c)});mini.appendChild(svg);
    }

    function draw(){
      const {nodes,edges}=activeFiltered(),w=1000,h=650,pos=positionsFor(nodes,edges,w,h),adj=adjacency(edges),focus=state.hovered||state.selected,focusSet=relatedSet(focus,edges);
      metrics.innerHTML='';[['NODES',nodes.length],['RELATIONSHIPS',edges.length],['LAYOUT',state.layout.toUpperCase()],['LENS',state.lens.toUpperCase()],['MODE',graph.publicDemo?'DEMO':'PROJECT']].forEach(([a,b])=>{const d=document.createElement('span');d.innerHTML='<b></b><small></small>';d.querySelector('b').textContent=b;d.querySelector('small').textContent=a;metrics.appendChild(d)});
      stage.querySelectorAll(':scope > svg,:scope > .sgr-zoom').forEach(x=>x.remove());
      if(!nodes.length){const empty=document.createElement('p');empty.textContent='No nodes match the current graph filters.';stage.appendChild(empty);return}

      const svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.classList.add('sgr-canvas');
      const defs=document.createElementNS(NS,'defs');defs.innerHTML='<marker id="sgr-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z"></path></marker>';svg.appendChild(defs);
      const world=document.createElementNS(NS,'g');world.setAttribute('transform',`translate(${state.panX} ${state.panY}) scale(${state.zoom})`);svg.appendChild(world);

      edges.forEach((e,idx)=>{
        const a=pos.get(e.source),b=pos.get(e.target);if(!a||!b)return;
        const dx=b.x-a.x,dy=b.y-a.y,mx=(a.x+b.x)/2,my=(a.y+b.y)/2,curve=((idx%5)-2)*18;
        const nx=-dy/Math.max(1,Math.sqrt(dx*dx+dy*dy)),ny=dx/Math.max(1,Math.sqrt(dx*dx+dy*dy)),cx=mx+nx*curve,cy=my+ny*curve;
        const p=document.createElementNS(NS,'path');p.setAttribute('d',`M ${a.x} ${a.y} Q ${cx} ${cy} ${b.x} ${b.y}`);p.setAttribute('class','sgr-edge'+(focus&&!(focusSet.has(e.source)&&focusSet.has(e.target))?' dim':'')+(focus&&(e.source===focus||e.target===focus)?' focus':''));p.setAttribute('marker-end','url(#sgr-arrow)');world.appendChild(p);
        if(state.showEdgeLabels){const t=document.createElementNS(NS,'text');t.setAttribute('x',cx);t.setAttribute('y',cy);t.setAttribute('class','sgr-edge-label');t.textContent=e.relation;world.appendChild(t)}
      });

      nodes.forEach(n=>{
        const p=pos.get(n.id),group=n.group||n.kind,g=document.createElementNS(NS,'g');g.setAttribute('class','sgr-node group-'+String(group).replace(/[^a-z0-9_-]/gi,'-')+(state.selected===n.id?' selected':'')+(focus&&!focusSet.has(n.id)?' dim':'')+(focus&&focusSet.has(n.id)?' focus':'')+(state.pinned.has(n.id)?' pinned':''));g.setAttribute('tabindex','0');
        const c=document.createElementNS(NS,'circle');c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);c.setAttribute('r',group==='project'?28:Math.max(12,Math.min(20,11+(adj.get(n.id)?.size||0)*1.4)));
        const title=document.createElementNS(NS,'title');title.textContent=`${n.label||n.id} · ${group}`;c.appendChild(title);g.appendChild(c);
        if(state.showLabels){const t=document.createElementNS(NS,'text');t.setAttribute('x',p.x+22);t.setAttribute('y',p.y+4);t.textContent=String(n.label||n.id).slice(0,52);g.appendChild(t)}
        g.onmouseenter=()=>{state.hovered=n.id;draw()};g.onmouseleave=()=>{state.hovered=null;draw()};g.onclick=()=>{inspect(n,edges,right);draw()};
        g.onkeydown=e=>{if(e.key==='Enter'){inspect(n,edges,right);draw()}};
        let dragging=false,last=null;
        g.addEventListener('pointerdown',e=>{e.stopPropagation();dragging=true;last={x:e.clientX,y:e.clientY};g.setPointerCapture(e.pointerId)});
        g.addEventListener('pointermove',e=>{if(!dragging)return;const dx=(e.clientX-last.x)/state.zoom,dy=(e.clientY-last.y)/state.zoom,lastPos=pos.get(n.id);state.pinned.set(n.id,{x:clamp(lastPos.x+dx,35,w-35),y:clamp(lastPos.y+dy,35,h-35),vx:0,vy:0});last={x:e.clientX,y:e.clientY};draw()});
        g.addEventListener('pointerup',e=>{dragging=false;try{g.releasePointerCapture(e.pointerId)}catch(_){}});
        world.appendChild(g);
      });

      let panning=false,lastPan=null;
      svg.addEventListener('pointerdown',e=>{if(e.target===svg){panning=true;lastPan={x:e.clientX,y:e.clientY};svg.setPointerCapture(e.pointerId)}});
      svg.addEventListener('pointermove',e=>{if(!panning)return;state.panX+=e.clientX-lastPan.x;state.panY+=e.clientY-lastPan.y;lastPan={x:e.clientX,y:e.clientY};draw()});
      svg.addEventListener('pointerup',e=>{panning=false;try{svg.releasePointerCapture(e.pointerId)}catch(_){}});
      svg.addEventListener('wheel',e=>{e.preventDefault();state.zoom=clamp(state.zoom*(e.deltaY<0?1.1:.9),.45,2.8);draw()},{passive:false});
      stage.appendChild(svg);

      const zoom=document.createElement('div');zoom.className='sgr-zoom';zoom.innerHTML='<button>+</button><button>−</button><button>⌗</button>';const bs=zoom.querySelectorAll('button');bs[0].onclick=()=>{state.zoom=clamp(state.zoom+.15,.45,2.8);draw()};bs[1].onclick=()=>{state.zoom=clamp(state.zoom-.15,.45,2.8);draw()};bs[2].onclick=()=>{state.zoom=1;state.panX=0;state.panY=0;draw()};stage.appendChild(zoom);
      drawMini(nodes,edges,pos,w,h);
    }
    drawCurrent=draw;

    head.querySelector('[data-sgr-search]').oninput=e=>{state.query=e.target.value;state.connectedOnly=null;draw()};
    head.querySelector('[data-sgr-reset]').onclick=()=>{state.query='';head.querySelector('[data-sgr-search]').value='';state.kindFilters.clear();state.relationFilters.clear();state.selected=null;state.hovered=null;state.connectedOnly=null;state.zoom=1;state.panX=state.panY=0;state.pinned.clear();state.collapsedGroups.clear();renderFilters();inspect(null,[],right);draw()};
    head.querySelector('[data-fullscreen]').onclick=()=>{container.classList.toggle('sgr-fullscreen');state.fullscreen=container.classList.contains('sgr-fullscreen');head.querySelector('[data-fullscreen]').textContent=state.fullscreen?'Exit full screen':'Full screen';setTimeout(draw,30)};

    toolbar.querySelectorAll('[data-layout]').forEach(b=>b.onclick=()=>{state.layout=b.dataset.layout;toolbar.querySelectorAll('[data-layout]').forEach(x=>x.classList.toggle('active',x===b));state.pinned.clear();draw()});
    toolbar.querySelector('[data-toggle-labels]').onclick=()=>{state.showLabels=!state.showLabels;draw()};
    toolbar.querySelector('[data-toggle-edges]').onclick=()=>{state.showEdgeLabels=!state.showEdgeLabels;draw()};
    toolbar.querySelector('[data-collapse]').onclick=()=>{const groups=unique((graph.nodes||[]).map(n=>n.group||n.kind).filter(x=>x!=='project'));if(state.collapsedGroups.size)state.collapsedGroups.clear();else groups.forEach(g=>state.collapsedGroups.add(g));draw()};

    lensbar.innerHTML='';['all'].concat(graph.availableLenses||[]).forEach(l=>{const b=document.createElement('button');b.type='button';b.textContent=l;b.className=(state.lens===l?'active':'');b.onclick=()=>opts.onLens&&opts.onLens(l);lensbar.appendChild(b)});
    renderFilters();inspect(null,[],right);draw();
  }

  return Object.freeze({version:VERSION,render,state:()=>({...state})});
}
root.SCSharedResearchGraphRuntime=Object.freeze({version:VERSION,create});
})(globalThis);