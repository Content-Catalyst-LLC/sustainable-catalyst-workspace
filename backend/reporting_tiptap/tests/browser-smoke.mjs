/**
 * SC-PUB-TIPTAP-01 / SC-EDITOR-DOCX-01 true Chromium test of the local bundled editor.
 * No production network, databases, credentials or existing source volumes.
 *
 * Usage: node tests/browser-smoke.mjs [manuscript.md]
 * Without an argument a synthetic policy paper with the Venezuela paper's
 * structure (title, H2/H3, one three-column table, one figure, references)
 * is used.
 */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const bundle=path.resolve(here,'../../app/reporting_publication_tiptap.bundle.js');
// The Studio's own stylesheet, so layout assertions test what the owner sees.
const studioCss=fs.readFileSync(path.resolve(here,'../../app/reporting_publication_ui.html'),'utf8')
  .match(/<style>([\s\S]*?)<\/style>/)[1];
const synthetic=[
  '# Synthetic Policy Paper: Sanctions and Sustainability',
  '',
  'By Synthetic Author',
  '',
  '## Executive Summary',
  '',
  'Implementation has been dominated by **collapse** and *constraint* (IMF, 2022). Additionality remains uncertain [@Beerling2020].',
  '',
  '## Background',
  '',
  'Oil exports financed social programs while crowding out diversified production.',
  '',
  '![Figure 1. Binding constraint pathway](asset:docx-figure-0123456789abcdef01234567)',
  '',
  '### Food security',
  '',
  'Table 1. Issues and implementation barriers',
  '',
  '| Issue area | Why it matters | Practical barriers |',
  '|---|---|---|',
  '| Food security | Hunger and health | Import dependence \\| payment rails |',
  '| Climate capacity | Paris Agreement | Limited investment |',
  '',
  '$$',
  'CO_2 + basalt',
  '$$',
  '',
  '1. First recommendation',
  '2. Second recommendation',
  '',
  '## List of References',
  '',
  "ACAPS (2018) 'Venezuela: Humanitarian Crisis', ACAPS. → https://www.acaps.org/en/countries/archives/detail/venezuela\\_crisis",
  '',
  "IMF (2022) 'An Unprecedented Economic and Humanitarian Crisis', International Monetary Fund. → https://www.imf.org/",
  '',
  "Weisbrot, M. and Sachs, J. (2019) 'Economic Sanctions as Collective Punishment', CEPR. → https://cepr.net/",
  '',
].join('\n');
const fixture=process.argv[2]?fs.readFileSync(process.argv[2],'utf8'):synthetic;
const real=Boolean(process.argv[2]);

const browser=await chromium.launch({headless:true});
try {
  const page=await browser.newPage({viewport:{width:1280,height:900}});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await page.setContent('<!doctype html><html><head><style>'+studioCss+'</style></head><body>'+
    '<textarea id="manuscript"></textarea>'+
    '<div id="visualBlocks"></div></body></html>');
  await page.evaluate(initial=>{
    document.getElementById('manuscript').value=initial;
    window.dirtyCount=0;
    window.markDirty=()=>{window.dirtyCount+=1};
    window.preview=async()=>({});
    window.setEditorMode=()=>{};
    // 1x1 transparent PNG stands in for the project figure endpoint.
    window.SCStudioAssetUrl=id=>'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=#'+id;
    window.SCStudioCitations=()=>[{key:'imf2022unprecedented',label:'(IMF, 2022) An Unprecedented Crisis'}];
    window.SCStudioCitationLabel=key=>key==='imf2022unprecedented'?'IMF (2022) An Unprecedented Crisis.':'';
    window.SCStudioRegisterTiptap=adapter=>{
      window.editorAdapter=adapter;
      adapter.render();
    };
  },fixture);
  // Declared like the Studio host's global status() (window.status itself is a legacy string property).
  await page.addScriptTag({content:'function status(message){window.lastStatus=message}'});
  await page.addScriptTag({path:bundle});
  await page.waitForSelector('[data-sc-research-editor="tiptap"]');
  const value=()=>page.locator('#manuscript').inputValue();

  // One continuous document, one toolbar, an outline.
  assert.equal(await page.locator('[data-sc-research-editor="tiptap"]').count(),1,'exactly one editor');
  assert.equal(await page.locator('.sc-doc-toolbar').count(),1,'exactly one shared toolbar');
  assert.equal(await page.locator('.sc-rich-toolbar, .sc-tiptap-block').count(),0,'no per-paragraph editors');
  assert.equal(await value(),fixture,'Viewing must not serialize or mutate original source');
  const editor=page.locator('.sc-doc-page .tiptap');
  // Put the caret after `text` inside the first block containing it (DOM selection, as a click would).
  const caretAfter=async(selector,text)=>{
    await page.evaluate(([selector,text])=>{
      const node=[...document.querySelectorAll('.sc-doc-page .tiptap '+selector)].find(n=>n.textContent.includes(text));
      const walker=document.createTreeWalker(node,NodeFilter.SHOW_TEXT);
      let t;while((t=walker.nextNode())){const i=t.data.indexOf(text);if(i>=0){
        node.closest('.tiptap').focus();
        const range=document.createRange();range.setStart(t,i+text.length);range.collapse(true);
        const sel=getSelection();sel.removeAllRanges();sel.addRange(range);return}}
      throw Error('text not found: '+text);
    },[selector,text]);
    await page.waitForTimeout(50);
  };

  // Structure survives as structure.
  const headings=await editor.locator('h1,h2,h3,h4').count();
  const expectedHeadings=(fixture.match(/^#{1,4} /gm)||[]).length;
  assert.equal(headings,expectedHeadings,'headings remain headings');
  assert.equal(await page.locator('.sc-outline-list button').count(),expectedHeadings,'outline lists every heading');
  const tables=(fixture.match(/^\|[^\n]*\|\n\|[-|: ]+\|$/gm)||[]).length;
  assert.equal(await editor.locator('table').count(),tables,'tables are editable tables');
  const firstTable=editor.locator('table').first();
  assert.equal(await firstTable.locator('tr').first().locator('th').count(),3,'three-column header row');
  assert.ok(!(await editor.innerText()).includes('| Issue'),'no pipe-separated table text');
  const figures=(fixture.match(/^!\[[^\]]*\]\(asset:/gm)||[]).length;
  assert.equal(await editor.locator('figure.sc-doc-figure img').count(),figures,'figures render in the manuscript');
  const refs=await editor.locator('p.sc-ref-entry').count();
  assert.ok(refs>=3,'reference entries are one hanging-indent list: '+refs);
  const indent=await editor.locator('p.sc-ref-entry').first().evaluate(n=>getComputedStyle(n).textIndent);
  assert.match(indent,/^-/,'hanging indent');

  if(!real){
    // Figure stays at its original position: after the Background paragraph, before the Food security heading.
    const order=await editor.evaluate(root=>[...root.children].map(n=>n.tagName+':'+(n.textContent||'').slice(0,20)));
    const fig=order.findIndex(x=>x.startsWith('FIGURE'));
    assert.match(order[fig-1],/^P:Oil exports/);assert.match(order[fig+1],/^H3:Food security/);
    assert.equal(await editor.locator('ol li').count(),2,'numbered list');
    assert.equal(await editor.locator('.sc-doc-source').count(),1,'equation preserved as source');

    // Edit one paragraph: only that block changes.
    await caretAfter('p','diversified production.');
    await page.keyboard.type(' More research.');
    await page.waitForFunction(()=>window.dirtyCount>0);
    let revised=await value();
    assert.match(revised,/diversified production\. More research\./);
    assert.equal(revised.replace(' More research.',''),fixture,'every other block is byte-identical');

    // Insert a linked citation at the cursor, without leaving the visual editor.
    await caretAfter('p','(IMF, 2022). ');
    await page.locator('.sc-cite-select').selectOption('imf2022unprecedented');
    revised=await value();
    assert.match(revised,/\(IMF, 2022\)\. \[@imf2022unprecedented\]Additionality/,'citation inserted exactly at the cursor');
    assert.match(revised,/\[@Beerling2020\]/,'existing citation key preserved');
    assert.ok(!revised.includes('\\[@'),'markers are not escaped');
    await page.keyboard.type(' ');
    revised=await value();
    assert.match(revised,/\[@imf2022unprecedented\] Additionality/,'cursor stays after the inserted citation');
    assert.ok(await editor.locator('.sc-cite').count()>=2,'citations are shown as linked citations');

    // Edit a table cell: the table stays a table.
    await caretAfter('td','Limited investment');
    await page.keyboard.type(' and finance');
    revised=await value();
    assert.match(revised,/^\| Issue area +\| Why it matters +\| Practical barriers +\|\n\| -{3,} \| -{3,} \| -{3,} \|$/m,'still a GFM table');
    assert.match(revised,/Import dependence \\\| payment rails/,'escaped pipe stays inside its cell');
    assert.match(revised,/Limited investment and finance/);
    assert.match(revised,/\$\$\nCO_2 \+ basalt\n\$\$/);
    assert.match(revised,/!\[Figure 1\. Binding constraint pathway\]\(asset:docx-figure-0123456789abcdef01234567\)/);

    // Reopen: the saved Markdown renders back to the same document without changes.
    await page.evaluate(()=>{window.editorAdapter.destroy();window.editorAdapter.render()});
    assert.equal(await value(),revised,'reopening does not rewrite the manuscript');
    assert.equal(await editor.locator('table').count(),tables);
    assert.equal(await editor.locator('figure.sc-doc-figure').count(),figures);
  }
  if(process.env.SC_SMOKE_SCREENSHOT)await page.screenshot({path:process.env.SC_SMOKE_SCREENSHOT,fullPage:false});
  await page.evaluate(()=>window.editorAdapter.destroy());
  assert.equal(errors.length,0,errors.join('; '));
  console.log('SC-EDITOR-DOCX-01 browser PASS: one editor, '+headings+' headings, '+tables+' table(s), '+
              figures+' figure(s), '+refs+' reference entries'+(real?' (supplied manuscript)':', edits/citation/reopen verified'));
} finally {
  await browser.close();
}
