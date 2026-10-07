(function(root){'use strict';
const V='3.81.0';
const LENSES=['all','knowledge','evidence','sources','data','analysis','timeline','geography','decision','provenance'];
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
function create(options){
 const api=options.apiClient;
 async function profile(){try{return await api.get('/v1/research-graph/profile')}catch(e){return{version:V,authRequired:true,error:String(e&&e.message||e)}}}
 async function project(id,lens){const qs=lens&&lens!=='all'?'?lens='+encodeURIComponent(lens):'';try{return await api.get('/v1/research-graph/projects/'+encodeURIComponent(id)+qs)}catch(e){return{version:V,nodes:[],edges:[],nodeCount:0,edgeCount:0,availableLenses:LENSES.slice(1),authRequired:true,error:String(e&&e.message||e)}}}
 function render(panel,g,onLens){
   const map=panel.querySelector('[data-research-graph-map]');
   const detail=panel.querySelector('[data-research-graph-detail]');
   const nodeCount=panel.querySelector('[data-research-graph-node-count]');
   const edgeCount=panel.querySelector('[data-research-graph-edge-count]');
   const fp=panel.querySelector('[data-research-graph-fingerprint]');
   if(nodeCount)nodeCount.textContent=String(g.nodeCount||0);
   if(edgeCount)edgeCount.textContent=String(g.edgeCount||0);
   if(fp)fp.textContent=String(g.graphFingerprint||'').slice(0,16);
   const lenses=panel.querySelector('[data-research-graph-lenses]');
   if(lenses){
     lenses.innerHTML='';
     ['all'].concat(g.availableLenses||LENSES.slice(1)).forEach(l=>{
       const b=document.createElement('button');b.type='button';b.className='btn research-graph-lens'+((g.lens||'all')===l?' active':'');b.textContent=l[0].toUpperCase()+l.slice(1);b.onclick=()=>onLens&&onLens(l);lenses.appendChild(b);
     });
   }
   if(!map)return;
   map.innerHTML='';
   const nodes=g.nodes||[],edges=g.edges||[];
   if(!nodes.length){map.textContent='No graph nodes are available for this project/lens.';return}
   const w=960,h=620,cx=w/2,cy=h/2;
   const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
   svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('role','img');svg.setAttribute('aria-label','Personal research graph');
   const project=nodes.find(n=>n.kind==='project')||nodes[0];
   const rest=nodes.filter(n=>n.id!==project.id);
   const groups={};rest.forEach(n=>(groups[n.kind]||(groups[n.kind]=[])).push(n));
   const kinds=Object.keys(groups).sort();
   const pos=new Map();pos.set(project.id,{x:cx,y:cy});
   kinds.forEach((kind,ki)=>{
     const arr=groups[kind],ring=1+(ki%4),radius=105+ring*72;
     arr.forEach((n,i)=>{
       const a=((i/Math.max(1,arr.length))*Math.PI*2)+(ki*0.41);
       pos.set(n.id,{x:cx+Math.cos(a)*radius,y:cy+Math.sin(a)*radius});
     });
   });
   edges.forEach(e=>{const a=pos.get(e.source),b=pos.get(e.target);if(!a||!b)return;const line=document.createElementNS(svg.namespaceURI,'line');line.setAttribute('x1',a.x);line.setAttribute('y1',a.y);line.setAttribute('x2',b.x);line.setAttribute('y2',b.y);line.setAttribute('class','research-graph-edge');line.dataset.relation=e.relation||'';svg.appendChild(line)});
   nodes.forEach(n=>{const q=pos.get(n.id);if(!q)return;const gnode=document.createElementNS(svg.namespaceURI,'g');gnode.setAttribute('class','research-graph-node kind-'+String(n.kind||'unknown').replace(/[^a-z0-9_-]/gi,'-'));gnode.setAttribute('tabindex','0');const c=document.createElementNS(svg.namespaceURI,'circle');c.setAttribute('cx',q.x);c.setAttribute('cy',q.y);c.setAttribute('r',n.kind==='project'?19:11);const t=document.createElementNS(svg.namespaceURI,'text');t.setAttribute('x',q.x+15);t.setAttribute('y',q.y+4);t.textContent=String(n.label||n.id).slice(0,44);gnode.appendChild(c);gnode.appendChild(t);gnode.addEventListener('click',()=>{if(detail){detail.hidden=false;detail.textContent=JSON.stringify(n,null,2)}});gnode.addEventListener('keydown',e=>{if(e.key==='Enter')gnode.dispatchEvent(new Event('click'))});svg.appendChild(gnode)});
   map.appendChild(svg);
 }
 return Object.freeze({version:V,profile,project,render});
}
root.SCWorkspaceResearchGraphFactory=Object.freeze({version:V,create});
})(globalThis);