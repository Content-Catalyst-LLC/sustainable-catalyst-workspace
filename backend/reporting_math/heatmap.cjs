// Render the pinned existing Lab engine, never caller-provided JS or HTML.
'use strict';
(async()=>{
 const fs=require('node:fs');const {JSDOM}=await import('jsdom');
 const input=JSON.parse(fs.readFileSync(0,'utf8'));
 const dom=new JSDOM('<!doctype html><div id="plot"></div>');
 global.window=dom.window;global.document=dom.window.document;global.XMLSerializer=dom.window.XMLSerializer;
 require('./vendor/lab-scientific-visualization-v0440.cjs');
 const height=input.geospatial?Math.round(172+748*(input.spec.domain.y[1]-input.spec.domain.y[0])/(input.spec.domain.x[1]-input.spec.domain.x[0])):570;
 const rendered=window.SCLab.ScientificVisualizationEngineV0440.render(document.getElementById('plot'),input.spec,{width:860,height});
 const svg=rendered.svg;
 const colors=input.palette==='diverging'?['#2166ac','#67a9cf','#d1e5f0','#f7f7f7','#fddbc7','#ef8a62','#b2182b']:['#440154','#443983','#31688e','#21918c','#35b779','#90d743','#fde725'];
 for(const node of svg.querySelectorAll('text')){node.setAttribute('font-family','sans-serif');node.setAttribute('font-size',node.classList.contains('sc-sve0440-title')?'19':'12');node.setAttribute('fill','#172a26');}
 for(const node of svg.querySelectorAll('line,path')){node.setAttribute('stroke','#60766c');node.setAttribute('stroke-width','0.7');}
 const cells=svg.querySelectorAll('.sc-sve0440-heat');
 for(let i=0;i<cells.length;i++){const cell=cells[i],value=input.spec.cells[i].z,domain=input.spec.domain.z;const cv=v=>input.transform==='log10'?Math.log10(v):v;const t=domain[0]===domain[1]?0.5:(cv(value)-cv(domain[0]))/(cv(domain[1])-cv(domain[0]));cell.setAttribute('fill',colors[Math.max(0,Math.min(colors.length-1,Math.round(t*(colors.length-1))))]);
  if(cells.length<=100&&!input.geospatial){const c=input.spec.cells[i],pw=748,ph=height-172,cw=pw/input.spec.xValues.length,ch=ph/input.spec.yValues.length;const label=document.createElementNS('http://www.w3.org/2000/svg','text');label.setAttribute('x',String(82+(c.xIndex+0.5)*cw));label.setAttribute('y',String(86+ph-(c.yIndex+0.5)*ch+5));label.setAttribute('text-anchor','middle');label.setAttribute('font-size','15');label.setAttribute('font-family','sans-serif');label.setAttribute('fill',t<0.55?'white':'#10251e');label.textContent=String(c.z);svg.appendChild(label);}}

 // Freeze the SVG; executable DOM handlers never enter the export.
 svg.removeAttribute('xmlns');svg.setAttribute('width','860');svg.setAttribute('height',String(height));
 process.stdout.write(new XMLSerializer().serializeToString(svg));
 dom.window.close();
})().catch(e=>{process.stderr.write(String(e.message));process.exit(1)});
