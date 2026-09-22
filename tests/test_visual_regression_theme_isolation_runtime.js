'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const css=fs.readFileSync(path.join(root,'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.0.4.css'),'utf8');
const php=fs.readFileSync(path.join(root,'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'),'utf8');
for(const marker of ['overflow-x:clip','background:#fff!important','grid-template-columns:1fr!important','grid-template-columns:repeat(2,minmax(0,1fr))!important']){
  if(!css.includes(marker)) throw new Error('missing '+marker);
}
if(!php.includes('visual-regression-theme-isolation')) throw new Error('missing release stage');
console.log('PASS - v2.0.4 visual regression JS runtime');
