// SC-OUTPUT-01: freeze a registered scientific output as a static SVG with the pinned existing Lab engine.
// Input is a server-built line/scatter spec from verified run rows; never caller-provided JS, HTML or styles.
'use strict';
(async()=>{
 const fs=require('node:fs');const {JSDOM}=await import('jsdom');
 const input=JSON.parse(fs.readFileSync(0,'utf8'));
 if(!['line-scatter','scatter'].includes(input.spec.kind))throw Error('Unsupported output chart kind');
 const dom=new JSDOM('<!doctype html><div id="plot"></div>');
 global.window=dom.window;global.document=dom.window.document;global.XMLSerializer=dom.window.XMLSerializer;
 require('./vendor/lab-scientific-visualization-v0440.cjs');
 const rendered=window.SCLab.ScientificVisualizationEngineV0440.render(document.getElementById('plot'),input.spec,{width:860,height:520});
 const svg=rendered.svg;
 // Engine styles live in Lab CSS; a frozen figure carries them as presentation attributes (Okabe-Ito blue).
 const ink='#0072B2';
 const set=(selector,attrs)=>{for(const n of svg.querySelectorAll(selector))for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v)};
 set('text',{'font-family':'sans-serif','font-size':'13','fill':'#172a26'});
 set('.sc-sve0440-title',{'font-size':'19','font-weight':'bold'});
 set('line,path',{'stroke':'#60766c','stroke-width':'0.8'});
 set('.sc-sve0440-grid line,.sc-sve0440-grid',{'stroke':'#d8e0dc','stroke-width':'0.6'});
 set('.sc-sve0440-band',{'fill':ink,'fill-opacity':'0.18','stroke':'none'});
 set('.sc-sve0440-line',{'stroke':ink,'stroke-width':'2','fill':'none'});
 set('.sc-sve0440-error line',{'stroke':ink,'stroke-width':'1'});
 set('.sc-sve0440-point',{'fill':ink,'stroke':'white','stroke-width':'0.8'});
 // Freeze the SVG; executable DOM handlers and focus behaviour never enter the stored figure.
 svg.removeAttribute('xmlns');svg.removeAttribute('tabindex');svg.setAttribute('width','860');svg.setAttribute('height','520');
 process.stdout.write(new XMLSerializer().serializeToString(svg));
 dom.window.close();
})().catch(e=>{process.stderr.write(String(e.message));process.exit(1)});
