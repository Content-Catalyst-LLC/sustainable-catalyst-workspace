// Fixed, offline typesetting worker. No scientific expression evaluation.
'use strict';
const fs=require('node:fs');
const {mathjax}=require('mathjax-full/js/mathjax.js');
const {TeX}=require('mathjax-full/js/input/tex.js');
const {SVG}=require('mathjax-full/js/output/svg.js');
const {liteAdaptor}=require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=require('mathjax-full/js/handlers/html.js');
require('mathjax-full/js/input/tex/ams/AmsConfiguration.js');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
if(typeof input.latex!=='string'||input.latex.length>2000)throw Error('Math input limit');
// No dynamic packages, user macros, HTML, URLs, environment hooks or external IO.
if(/\\(?:href|url|html\w*|style|class|cssId|require|include\w*|input|write\w*|read|open\w*|newcommand|renewcommand|providecommand|def|gdef|edef|xdef|let|futurelet|csname|catcode|unicode|bbox|enclose|verb|newenvironment)\b/i.test(input.latex))throw Error('Unsafe math command');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const tex=new TeX({packages:['base','ams'],maxBuffer:4000,maxMacros:1000,formatError:(_jax,error)=>{throw error}});
const doc=mathjax.document('',{InputJax:tex,OutputJax:new SVG({fontCache:'none'})});
const node=doc.convert(input.latex,{display:input.mode!=='inline',em:16,ex:8,containerWidth:760});
const output=adaptor.outerHTML(node);
const svg=output.match(/<svg[\s\S]*<\/svg>/);
if(!svg||output.includes('data-mjx-error'))throw Error('Invalid LaTeX');
process.stdout.write(svg[0]);
