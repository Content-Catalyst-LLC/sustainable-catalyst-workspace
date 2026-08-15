(function(root,factory){
  const base=(typeof module==='object'&&module.exports)?require('./sc-workspace-relationship-explorer-v1.js'):root.SCWorkspaceRelationshipExplorer;
  const api=factory(base);
  if(typeof module==='object'&&module.exports)module.exports=api;else root.SCWorkspaceKnowledgeGraphExplorer=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(base){
  'use strict';
  const SCHEMA='sc-workspace-relationship-explorer/2.0', SNAPSHOT_SCHEMA='sc-workspace-knowledge-graph-snapshot/1.0';
  const text=v=>String(v==null?'':v).trim();
  const token=value=>{let h=2166136261,s=text(value);for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return(h>>>0).toString(16).padStart(8,'0');};
  function build(state,options={}){
    const graph=base&&typeof base.build==='function'?base.build(state,options):{nodes:[],edges:[],governance:{}};
    const nodes=[...(graph.nodes||[])],edges=[...(graph.edges||[])],nodeIds=new Set(nodes.map(n=>n.id)),edgeIds=new Set(edges.map(e=>`${e.from}|${e.relation}|${e.to}`));
    const addNode=n=>{if(n&&n.id&&!nodeIds.has(n.id)){nodeIds.add(n.id);nodes.push(n);}};
    const addEdge=(from,to,relation,meta={})=>{const k=`${from}|${relation}|${to}`;if(from&&to&&from!==to&&!edgeIds.has(k)){edgeIds.add(k);edges.push({id:`rge2-${token(k)}`,from,to,relation,explicit:true,...meta});}};
    const staged=Array.isArray(options.libraryContinuityItems)?options.libraryContinuityItems:[];
    for(const item of staged){const lid=text(item?.origin?.libraryId||item?.libraryId||item?.id);if(!lid)continue;const id=`library-record:${lid}`;addNode({id,type:'library-record',label:text(item.title)||'Knowledge Library record',summary:text(item.summary),libraryRecordId:lid,libraryKind:text(item.kind),sourceUrl:text(item.url||item?.origin?.sourceUrl||'/knowledge-libraries/'),private:Boolean(item.private),staged:true,updatedAt:item.updatedAt||item.createdAt||''});}
    const projects=Array.isArray(state?.projects)?state.projects:[];
    for(const project of projects){for(const o of (Array.isArray(project.objects)?project.objects:[])){const lid=text(o?.provenance?.libraryRecordId);if(!lid)continue;const ln=`library-record:${lid}`,on=`object:${text(project.id)}:${text(o.id)}`;addNode({id:ln,type:'library-record',label:text(o.provenance?.sourceTitle||o.title)||'Knowledge Library record',summary:text(o.provenance?.sourceUrl),libraryRecordId:lid,libraryKind:text(o.provenance?.libraryRecordKind),sourceUrl:text(o.provenance?.sourceUrl||'/knowledge-libraries/'),private:Boolean(o.provenance?.privatePersonalRecommendation),staged:false,updatedAt:o.provenance?.capturedAt||o.updatedAt});addEdge(on,ln,'originates-in-library',{source:'library-continuity-provenance'});}}
    return {...graph,explorerSchema:SCHEMA,nodes,edges,governance:{...(graph.governance||{}),libraryContinuityPointersOnly:true,pathTracingExplicit:true,backlinkLedgerDerived:true,portableSnapshot:true,duplicateGraphDatabase:false,automaticRelationshipInference:false,automaticAI:false,automaticMutation:false,localFirst:true}};
  }
  function backlinks(graph,nodeId,relation='all'){
    const nodes=new Map((graph?.nodes||[]).map(n=>[n.id,n]));
    return (graph?.edges||[]).filter(e=>(e.from===nodeId||e.to===nodeId)&&(relation==='all'||e.relation===relation)).map(e=>({edge:e,direction:e.to===nodeId?'incoming':'outgoing',other:nodes.get(e.to===nodeId?e.from:e.to)||null}));
  }
  function shortestPath(graph,from,to,maxDepth=5){
    if(!from||!to)return {found:false,nodes:[],edges:[],hops:0};if(from===to){const n=(graph?.nodes||[]).find(x=>x.id===from);return{found:Boolean(n),nodes:n?[n]:[],edges:[],hops:0};}
    const edges=graph?.edges||[],nodeMap=new Map((graph?.nodes||[]).map(n=>[n.id,n])),q=[[from,[],[from]]],seen=new Set([from]),limit=Math.max(1,Math.min(5,Number(maxDepth)||5));
    while(q.length){const [id,path,nodePath]=q.shift();if(path.length>=limit)continue;for(const e of edges){let next='';if(e.from===id)next=e.to;else if(e.to===id)next=e.from;else continue;if(seen.has(next))continue;const ep=[...path,e],np=[...nodePath,next];if(next===to)return{found:true,nodes:np.map(x=>nodeMap.get(x)).filter(Boolean),edges:ep,hops:ep.length};seen.add(next);q.push([next,ep,np]);}}
    return {found:false,nodes:[],edges:[],hops:0};
  }
  function edgeExplanation(edge){if(!edge)return'';const source=text(edge.source||'explicit Workspace record');return `${text(edge.relation).replaceAll('-',' ')} · recorded by ${source}${edge.note?` · ${text(edge.note)}`:''}`;}
  function snapshot(graph,options={}){const selected=text(options.selectedNodeId),path=options.path&&options.path.found?options.path:null;return{schema:SNAPSHOT_SCHEMA,createdAt:new Date().toISOString(),workspaceVersion:text(options.workspaceVersion),selectedNodeId:selected,filters:options.filters||{},counts:{nodes:(graph?.nodes||[]).length,edges:(graph?.edges||[]).length},path:path?{hops:path.hops,nodeIds:path.nodes.map(n=>n.id),edges:path.edges.map(e=>({from:e.from,to:e.to,relation:e.relation,source:text(e.source)}))}:null,nodes:(graph?.nodes||[]).map(n=>({id:n.id,type:n.type,label:n.label,projectId:n.projectId||'',libraryRecordId:n.libraryRecordId||''})),edges:(graph?.edges||[]).map(e=>({from:e.from,to:e.to,relation:e.relation,source:text(e.source)})),governance:{derivedAtRuntime:true,canonicalBodiesCopied:false,canonicalRecordsMutated:false,automaticInference:false,automaticAI:false,telemetry:false}};}
  return {...(base||{}),SCHEMA,SNAPSHOT_SCHEMA,build,backlinks,shortestPath,edgeExplanation,snapshot,NODE_TYPES:[...(base?.NODE_TYPES||[]),'library-record'],RELATION_TYPES:[...(base?.RELATION_TYPES||[]),'originates-in-library']};
});
