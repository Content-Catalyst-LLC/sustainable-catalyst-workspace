/**
 * SC-PUB-TIPTAP-01 true Chromium test of the local bundled editor.
 * No production network, databases, credentials or existing source volumes.
 */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const bundle=path.resolve(here,'../../app/reporting_publication_tiptap.bundle.js');
const fixture=[
  '# Wexford ERW',
  '',
  'Additionality remains uncertain [@Beerling2020].',
  '',
  '$$',
  'CO_2 + basalt',
  '$$',
  '',
  '![Verified figure](asset:fig-01)',
  '',
  '| Source | Value |',
  '|---|---|',
  '| Fixture | Synthetic |',
  '',
].join('\n');
const browser=await chromium.launch({headless:true});
try {
  const page=await browser.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.setContent('<!doctype html><html><body>'+
    '<textarea id="manuscript"></textarea>'+
    '<div id="visualBlocks"></div></body></html>');
  await page.evaluate(initial=>{
    document.getElementById('manuscript').value=initial;
    window.dirtyCount=0;
    window.markDirty=()=>{window.dirtyCount+=1};
    window.preview=async()=>({});
    window.status=()=>{};
    window.setEditorMode=()=>{};
    window.SCStudioRegisterTiptap=adapter=>{
      window.editorAdapter=adapter;
      adapter.render();
    };
  },fixture);
  await page.addScriptTag({path:bundle});
  await page.waitForSelector('[data-sc-research-editor="tiptap"]');
  const initial=await page.locator('#manuscript').inputValue();
  assert.equal(initial,fixture,'Viewing must not serialize or mutate original source');
  assert.equal(await page.locator('.sc-source-only').count(),3,
    'Equations, figures, and table must have independent read-only blocks');
  const paragraph=page.locator('[data-sc-research-editor="tiptap"]').nth(1);
  await paragraph.click();
  await page.keyboard.press('End');
  await page.keyboard.type(' More research.');
  await page.waitForFunction(()=>window.dirtyCount>0);
  const revised=await page.locator('#manuscript').inputValue();
  assert.match(revised,/More research\./);
  assert.match(revised,/\[@Beerling2020\]/);
  assert.match(revised,/\$\$\nCO_2 \+ basalt\n\$\$/);
  assert.match(revised,/!\[Verified figure\]\(asset:fig-01\)/);
  assert.match(revised,/\| Fixture \| Synthetic \|/);
  await page.evaluate(()=>window.editorAdapter.destroy());
  assert.equal(errors.length,0,errors.join('; '));
  console.log('SC-PUB-TIPTAP-01 browser PASS: editor mounted, edited, source islands preserved');
} finally {
  await browser.close();
}
