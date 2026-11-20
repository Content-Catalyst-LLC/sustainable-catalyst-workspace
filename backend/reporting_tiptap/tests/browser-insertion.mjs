/**
 * SC-FIG-PLACE-01: Chromium regression test for figure and scientific-output placement.
 *
 * Runs the Studio's real host insertion code (reporting_publication_visual.js and
 * reporting_scientific_outputs_ui.js) with the real Tiptap bundle, driven by real clicks and keys,
 * so focus moves to panels and buttons exactly as it does for the researcher. Synthetic content only;
 * no network, databases or credentials.
 *
 * Usage: node tests/browser-insertion.mjs
 */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const app = path.resolve(here, '../../app');
const host = ['reporting_publication_visual.js', 'reporting_scientific_outputs_ui.js']
  .map(name => fs.readFileSync(path.join(app, name), 'utf8')).join('\n');
const original = ['# Synthetic Paper', '', '## Introduction', '',
  'Intro sentence one. Intro sentence two.', '', '## Methods', '', '$$', 'y = a + b x', '', '$$', '',
  '- First step', '- Second step', '', '## Discussion', '', 'Final paragraph.', ''].join('\n');
const OUTPUT = ['![SYNTHETIC fitted response](asset:sco-0123456789-SYN-dose-v1-chart)',
  '**Table: SYNTHETIC fitted response by dose** Values rounded to 4 significant figures.',
  '| Dose (mg) | Fit (units) |\n| --- | --- |\n| 1 | 1.100 |\n| 2 | 2.050 |',
  '*Source:* Synthetic Author (2026). Scientific output SYN-dose version 1.'].join('\n\n');
const FIGURE = '![Synthetic map](asset:art-synthetic-map-svg)';
const NO_CURSOR = /Nothing was inserted/;

const browser = await chromium.launch({headless: true});
let page, errors;
const value = () => page.locator('#manuscript').inputValue();
const statusText = () => page.locator('#status').textContent();
const editor = () => page.locator('.sc-doc-page .tiptap');

async function open(manuscript = original, visual = true) {
  if (page) await page.close();
  page = await browser.newPage({viewport: {width: 1100, height: 900}});
  errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.setContent(`<!doctype html><html><body>
    <div id="status"></div>
    <section><input id="scoQuery"><button id="scoSearch">Search</button><button id="scoOpen">Insert</button>
      <div id="scoPanel"></div><div id="scoResults"></div><div id="scoPreview"></div>
      <button id="insertOutput" type="button">Insert at cursor</button>
      <button id="insertFigure" type="button">Insert figure</button></section>
    <button id="visualMode"></button><button id="sourceMode"></button>
    <div id="visualTools"><button id="addHeading">+ Section</button><button id="addParagraph">+ Paragraph</button>
      <button id="addList"></button><button id="addQuote"></button><button id="addEquation"></button></div>
    <div id="visualBlocks"></div>
    <textarea id="manuscript" rows="30" cols="90"></textarea></body></html>`);
  // The few Studio globals the host insertion code uses; the network call returns a fixed insertion.
  await page.addScriptTag({content: `'use strict';
    const E = id => document.getElementById(id);
    const pub = '/pub';
    const state = {project: 'synthetic', citations: []};
    function status(message, error = false) { E('status').textContent = message; E('status').dataset.error = String(error); }
    function run(fn) { return async () => { try { await fn(); } catch (error) { status(error.message, true); } }; }
    function el(tag, text, cls) { const n = document.createElement(tag); if (text != null) n.textContent = text; if (cls) n.className = cls; return n; }
    function path(s) { return s; }
    function markDirty() { window.dirty = (window.dirty || 0) + 1; }
    async function preview() {}
    async function api() { return {markdown: ${JSON.stringify(OUTPUT + '\n')}}; }
    E('manuscript').value = ${JSON.stringify(manuscript)};
    ${host}
    SCO.selected = {outputId: 'SYN-dose', version: 1};
    E('insertOutput').onclick = run(scoInsert);
    E('insertFigure').onclick = run(async () => insertManuscriptBlocks(${JSON.stringify(FIGURE)}));`});
  await page.addScriptTag({path: path.join(app, 'reporting_publication_tiptap.bundle.js')});
  await page.waitForSelector('[data-sc-research-editor="tiptap"]');
  if (!visual) await page.click('#sourceMode');
  assert.equal(await value(), manuscript, 'opening does not change the manuscript');
}

// ProseMirror reads a click's DOM selection asynchronously; a person never types faster than that, a test can.
const settled = () => page.waitForFunction(() => {
  const view = document.querySelector('.sc-doc-page .tiptap').editor.view, dom = getSelection();
  return dom.anchorNode && view.posAtDOM(dom.anchorNode, dom.anchorOffset) === view.state.selection.anchor;
});

// A real click on the block containing `text`, then keys to the wanted caret position.
async function clickIn(text, key) {
  await editor().locator('h1,h2,p,li', {hasText: text}).first().click();
  await settled();
  if (key) { await page.keyboard.press(key); await settled(); }
}

// Top-level blocks of the Markdown, abbreviated, to assert order.
const blocks = markdown => markdown.trim().split(/\n\n+/).map(b => b.split('\n')[0].slice(0, 24));
const outputBlocks = blocks(OUTPUT);

function assertOutputAfter(markdown, anchor, label) {
  const list = blocks(markdown);
  const at = list.indexOf(outputBlocks[0]);
  assert.ok(at >= 0, label + ': output inserted');
  assert.deepEqual(list.slice(at, at + outputBlocks.length), outputBlocks,
    label + ': figure, caption, table and source note stay together and in order');
  assert.equal(anchor === null ? at : list[at - 1], anchor === null ? 0 : anchor, label + ': placed at the cursor');
  assert.equal(markdown.split('asset:sco-0123456789-SYN-dose-v1-chart').length - 1, 1, label + ': exactly one copy');
}

// Every existing byte is unchanged: the manuscript is the original with one inserted span at a block boundary.
// Inserted content: the figure line byte for byte, the table cells verbatim (Tiptap pads the inserted table's columns).
const FIRST = ['![SYNTHETIC fitted response]', '![Synthetic map]'];
const LAST = ['Scientific output SYN-dose version 1.', '(asset:art-synthetic-map-svg)'];
function assertOriginalKept(markdown, label, base = original) {
  const start = Math.min(...FIRST.map(m => markdown.indexOf(m)).filter(i => i >= 0));
  const end = Math.max(...LAST.map(m => markdown.lastIndexOf(m) + m.length).filter(i => i > 0 && i - 1 >= start));
  const before = markdown.slice(0, start).replace(/\s*$/, ''), after = markdown.slice(end).replace(/^\s*/, '');
  assert.ok(base.startsWith(before) && base.endsWith(after) &&
    base.slice(before.length, base.length - after.length).trim() === '', label + ': every existing block unchanged');
  const span = markdown.slice(start, end);
  if (span.includes('SYNTHETIC fitted')) {
    assert.ok(span.includes(OUTPUT.split('\n')[0] + '\n'), label + ': figure line byte for byte');
    const cells = span.split('\n').filter(l => /^\| (Dose|1|2) /.test(l)).map(l => l.split('|').map(c => c.trim()).filter(Boolean));
    assert.deepEqual(cells, [['Dose (mg)', 'Fit (units)'], ['1', '1.100'], ['2', '2.050']], label + ': table verbatim');
  }
}

const results = [];
async function check(name, fn) {
  await fn();
  assert.deepEqual(errors, [], name + ': no page errors');
  results.push(name);
  console.log('PASS ' + name);
}

try {
  // Visual editor ---------------------------------------------------------------------------------------------
  await check('beginning: caret at the start of the title inserts before it', async () => {
    await open();
    await clickIn('Synthetic Paper', 'Home');
    await page.click('#insertOutput');
    const md = await value();
    assertOutputAfter(md, null, 'beginning');
    assertOriginalKept(md, 'beginning');
  });

  await check('middle: caret at the end of the Introduction, focus moved to the panel search first', async () => {
    await open();
    await clickIn('Intro sentence two.', 'End');
    await page.click('#scoQuery');
    await page.keyboard.type('dose');
    await page.click('#insertOutput');
    const md = await value();
    assertOutputAfter(md, 'Intro sentence one. Intr', 'middle');
    assertOriginalKept(md, 'middle');
    assert.match(await statusText(), /inserted/);
  });

  await check('middle: caret inside a sentence never splits the paragraph', async () => {
    await open();
    await clickIn('Intro sentence two.', 'Home');
    for (let i = 0; i < 6; i += 1) await page.keyboard.press('ArrowRight');
    await page.click('#insertOutput');
    const md = await value();
    assert.match(md, /Intro sentence one\. Intro sentence two\.\n\n!\[SYNTHETIC/, 'paragraph intact');
    assertOriginalKept(md, 'mid-sentence');
  });

  await check('middle: caret in a list inserts after the whole list', async () => {
    await open();
    await clickIn('First step', 'End');
    await page.click('#insertOutput');
    const md = await value();
    assert.match(md, /- First step\n- Second step\n\n!\[SYNTHETIC/);
    assertOriginalKept(md, 'list');
  });

  await check('end: caret in the final paragraph inserts at the end', async () => {
    await open();
    await clickIn('Final paragraph.', 'End');
    await page.click('#insertOutput');
    const md = await value();
    assertOutputAfter(md, 'Final paragraph.', 'end');
    assert.ok(md.trimEnd().endsWith('version 1.'), 'output is last');
    assertOriginalKept(md, 'end');
  });

  await check('unknown position: nothing is appended and the researcher is told to click', async () => {
    await open();
    await page.click('#insertOutput');
    assert.equal(await value(), original, 'manuscript unchanged');
    assert.match(await statusText(), NO_CURSOR);
    await page.click('#insertFigure');
    assert.equal(await value(), original, 'manuscript unchanged');
    await page.click('#addParagraph');
    assert.equal(await value(), original, 'manuscript unchanged');
  });

  await check('unknown position after the editor re-renders (mode switch): refused again', async () => {
    await open();
    await clickIn('Intro sentence two.', 'End');
    await page.click('#sourceMode');
    await page.click('#visualMode');
    await page.click('#insertOutput');
    assert.equal(await value(), original);
    assert.match(await statusText(), NO_CURSOR);
  });

  await check('source-file Insert figure goes to the cursor and stays in the visual editor', async () => {
    await open();
    await clickIn('Methods', 'End');
    await page.click('#insertFigure');
    const md = await value();
    assert.match(md, /## Methods\n\n!\[Synthetic map\]\(asset:art-synthetic-map-svg\)\n\n\$\$/);
    assert.equal(await page.evaluate(() => visualMode), true, 'still in the visual editor');
    assert.equal(md.trimEnd().endsWith('Final paragraph.'), true, 'nothing appended at the bottom');
    assertOriginalKept(md, 'figure');
  });

  await check('scientific output then figure at one cursor: both in order, nothing at the bottom', async () => {
    await open();
    await clickIn('Intro sentence two.', 'End');
    await page.click('#insertOutput');
    await page.click('#insertFigure');
    const md = await value();
    const list = blocks(md);
    assert.equal(list[list.indexOf(outputBlocks[3]) + 1], '![Synthetic map](asset:a', 'figure right after the output');
    assert.ok(md.trimEnd().endsWith('Final paragraph.'));
    assertOriginalKept(md, 'sequence');
  });

  await check('duplicates are refused: same output version and same figure', async () => {
    await open();
    await clickIn('Intro sentence two.', 'End');
    await page.click('#insertOutput');
    await page.click('#insertFigure');
    const once = await value();
    await clickIn('Final paragraph.', 'End');
    await page.click('#insertOutput');
    assert.equal(await value(), once, 'second copy of the output refused');
    assert.match(await statusText(), /already in the manuscript/);
    await page.click('#insertFigure');
    assert.equal(await value(), once, 'second copy of the figure refused');
  });

  await check('selected text is never replaced', async () => {
    await open();
    await clickIn('Intro sentence two.', 'Home');
    await page.keyboard.press('Shift+End');
    await page.click('#insertOutput');
    const md = await value();
    assertOutputAfter(md, 'Intro sentence one. Intr', 'selection');
    assertOriginalKept(md, 'selection');
  });

  await check('a selected figure is kept; the output goes after it', async () => {
    await open(original.replace('## Discussion', FIGURE + '\n\n## Discussion'));
    await editor().locator('figure.sc-doc-figure').click();
    await page.click('#insertOutput');
    const md = await value();
    assert.match(md, /asset:art-synthetic-map-svg\)\n\n!\[SYNTHETIC fitted response\]/);
    const withFigure = original.replace('## Discussion', FIGURE + '\n\n## Discussion');
    const start = md.indexOf('![SYNTHETIC'), end = md.indexOf('version 1.') + 'version 1.'.length;
    assert.equal(md.slice(0, start).trimEnd() + '\n\n' + md.slice(end).trimStart(), withFigure, 'figure and every block kept');
  });

  await check('reopening the inserted manuscript renders it unchanged', async () => {
    await open();
    await clickIn('Intro sentence two.', 'End');
    await page.click('#insertOutput');
    const md = await value();
    await page.evaluate(() => { tiptapBridge.destroy(); tiptapBridge.render(); });
    assert.equal(await value(), md);
    assert.equal(await editor().locator('figure.sc-doc-figure').count(), 1);
    assert.equal(await editor().locator('table').count(), 1);
  });

  // SC-FIG-PLACE-02: paragraphs made with Enter are their own blocks -------------------------------------------
  const TYPED = ['Typed one about the plots.', 'Typed two about the method.', 'Typed three before the next section.'];
  const typeParagraphs = async () => {
    await clickIn('Introduction', 'End');
    for (const text of TYPED) { await page.keyboard.press('Enter');
      await page.keyboard.type(text); }
  };
  const withTyped = original.replace('## Introduction\n\n', '## Introduction\n\n' + TYPED.join('\n\n') + '\n\n');

  await check('Enter-typed paragraphs are separate blocks and every saved block keeps its bytes', async () => {
    await open();
    await typeParagraphs();
    assert.equal(await value(), withTyped, 'the Markdown is the original plus three paragraphs');
    assert.equal(await editor().locator('p', {hasText: 'Typed'}).count(), 3);
  });

  for (const [where, at, key, anchor] of [
    ['beginning', 0, 'Home', '## Introduction'],
    ['middle', 1, 'End', TYPED[1].slice(0, 24)],
    ['middle (first typed paragraph, the SC-OUTPUT-02 staging case)', 0, 'End', TYPED[0].slice(0, 24)],
    ['end', 2, 'End', TYPED[2].slice(0, 24)],
  ]) {
    await check(`Enter-typed paragraphs: ${where} inserts at that paragraph boundary`, async () => {
      await open();
      await typeParagraphs();
      await clickIn(TYPED[at], key);
      await page.click('#insertOutput');
      const md = await value();
      assertOutputAfter(md, anchor, where);
      assertOriginalKept(md, where, withTyped);
      const order = await editor().evaluate(r => [...r.children].map(n => n.tagName + ':' + n.textContent.slice(0, 12)));
      const fig = order.findIndex(x => x.startsWith('FIGURE'));
      assert.equal(order[fig + 4], key === 'Home' ? 'P:' + TYPED[0].slice(0, 12) : at < 2 ? 'P:' + TYPED[at + 1].slice(0, 12) : 'P:Intro senten',
        where + ': the next paragraph follows the output in the editor');
    });
  }

  await check('Enter-typed paragraphs: a source-file figure goes to the same boundary, then save and reopen', async () => {
    await open();
    await typeParagraphs();
    await clickIn(TYPED[1], 'End');
    await page.click('#insertFigure');
    const md = await value();
    assert.ok(md.includes(TYPED[1] + '\n\n' + FIGURE + '\n\n' + TYPED[2]), 'figure between typed paragraphs two and three');
    await page.evaluate(() => { tiptapBridge.destroy(); tiptapBridge.render(); });
    assert.equal(await value(), md, 'reopened unchanged');
    await clickIn(TYPED[0], 'End');
    await page.click('#insertOutput');
    const again = await value();
    assertOutputAfter(again, TYPED[0].slice(0, 24), 'after reopen');
    assert.ok(again.includes(TYPED[1] + '\n\n' + FIGURE), 'figure kept in place');
  });

  const CITED = original.replace('Intro sentence one. Intro sentence two.',
    'Intro sentence one [@Alpha2020]. Intro sentence two [@Beta2021; @Gamma2022, p. 4] and \\[@Literal\\].');

  await check('splitting a saved paragraph keeps its citations active in both halves and a literal stays literal', async () => {
    await open(CITED);
    await clickIn('Intro sentence one', 'Home');
    for (let i = 0; i < 'Intro sentence one [@Alpha2020]. '.length; i += 1) await page.keyboard.press('ArrowRight');
    await settled();
    await page.keyboard.press('Enter');
    let md = await value();
    assert.equal(md, CITED.replace('[@Alpha2020]. Intro sentence two', '[@Alpha2020]. \n\nIntro sentence two'),
      'two paragraphs, split after the space; markers [@Beta2021; @Gamma2022, p. 4] restored and \\[@Literal\\] still escaped');
    await clickIn('Intro sentence one', 'End');
    await page.click('#insertOutput');
    md = await value();
    assertOutputAfter(md, 'Intro sentence one [@Alp', 'split');
    assert.ok(md.includes('version 1.\n\nIntro sentence two [@Beta2021; @Gamma2022, p. 4] and \\[@Literal\\].'), 'tail after the output');
  });

  await check('Enter at the start or end of a saved paragraph leaves that paragraph byte for byte', async () => {
    await open(CITED);
    await clickIn('Intro sentence one', 'Home');
    await page.keyboard.press('Enter');
    await page.keyboard.press('ArrowUp');
    await settled();
    await page.keyboard.type('New lead paragraph.');
    const para = CITED.split('\n\n')[2];
    assert.equal(await value(), CITED.replace(para, 'New lead paragraph.\n\n' + para));
    await open(CITED);
    await clickIn('Intro sentence one', 'End');
    await page.keyboard.press('Enter');
    await page.keyboard.type('New closing paragraph.');
    assert.equal(await value(), CITED.replace(para, para + '\n\nNew closing paragraph.'));
  });

  await check('undoing the split restores the saved manuscript exactly', async () => {
    await open(CITED);
    await clickIn('sentence two', 'End');
    for (let i = 0; i < 14; i += 1) await page.keyboard.press('ArrowLeft');
    await settled();
    await page.waitForTimeout(700);  // not grouped with the load in Undo history (fixed in the next commit)
    await page.keyboard.press('Enter');
    assert.notEqual(await value(), CITED);
    await page.keyboard.press('ControlOrMeta+z');
    assert.equal(await value(), CITED);
  });

  await check('a click and caret movement alone never change a saved manuscript', async () => {
    for (const manuscript of [original, CITED, withTyped]) {
      await open(manuscript);
      for (const text of ['Synthetic Paper', 'Intro sentence', 'First step', 'Final paragraph.']) await clickIn(text, 'End');
      await page.keyboard.press('ArrowDown');
      assert.equal(await value(), manuscript);
    }
  });

  // Markdown source mode ----------------------------------------------------------------------------------------
  const source = () => page.locator('#manuscript');
  const caretAt = async offset => {
    await source().click();
    await page.evaluate(at => { const t = E('manuscript'); t.setSelectionRange(at, at); t.dispatchEvent(new KeyboardEvent('keyup', {key: 'ArrowRight'})); }, offset);
  };

  await check('source: unknown cursor refused (no append)', async () => {
    await open(original, false);
    await page.click('#insertOutput');
    assert.equal(await value(), original);
    assert.match(await statusText(), NO_CURSOR);
  });

  await check('source: beginning, middle (mid-sentence) and end', async () => {
    await open(original, false);
    await caretAt(0);
    await page.click('#insertFigure');
    let md = await value();
    assert.ok(md.startsWith(FIGURE + '\n\n# Synthetic Paper'), 'beginning');
    await open(original, false);
    await caretAt(original.indexOf('sentence two'));
    await page.click('#insertOutput');
    md = await value();
    assertOutputAfter(md, 'Intro sentence one. Intr', 'source middle');
    assertOriginalKept(md, 'source middle');
    await open(original, false);
    await caretAt(original.length);
    await page.click('#insertOutput');
    md = await value();
    assertOutputAfter(md, 'Final paragraph.', 'source end');
    assertOriginalKept(md, 'source end');
  });

  await check('source: a blank line inside a $$ equation is not a block boundary', async () => {
    await open(original, false);
    await caretAt(original.indexOf('y = a'));
    await page.click('#insertFigure');
    assert.match(await value(), /y = a \+ b x\n\n\$\$\n\n!\[Synthetic map\]/);
  });

  await check('source: a cursor from before a programmatic change is not reused', async () => {
    await open(original, false);
    await caretAt(original.indexOf('Final'));
    await page.evaluate(() => { E('manuscript').value += '\nAppended by another action.\n'; });
    await page.click('#insertOutput');
    assert.match(await statusText(), NO_CURSOR);
    assert.ok(!(await value()).includes('SYNTHETIC fitted'));
  });

  console.log(`SC-FIG-PLACE-01 browser PASS: ${results.length} placement checks`);
} finally {
  await browser.close();
}
