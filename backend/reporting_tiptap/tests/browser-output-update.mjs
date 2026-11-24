/**
 * SC-OUTPUT-02: Chromium test for cross-application outputs in the picker and the explicit "Update vN -> vM" action.
 *
 * Runs the Studio's real picker and insertion code (reporting_publication_visual.js and
 * reporting_scientific_outputs_ui.js) with the real Tiptap bundle and real clicks. The registry API is a fixed stub
 * shaped like the Studio's responses. Synthetic content only; no network, databases or credentials.
 *
 * Usage: node tests/browser-output-update.mjs
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

const chart = v => `sco-0123456789-SYN-basalt-cdr-v${v}-chart`;
const ROWS = {1: [['0.0', '0.000'], ['10.0', '0.330']], 2: [['0.0', '0.000'], ['10.0', '0.330'], ['20.0', '0.600']]};
const group = v => [`![SYNTHETIC estimated CO2 removal by basalt application rate](asset:${chart(v)})`,
  '**Table: SYNTHETIC estimated CO2 removal** Values rounded to 3 significant figures.',
  '| Basalt application rate (t/ha) | Estimated CO2 removal (t CO2/ha) |\n| --- | --- |\n' +
    ROWS[v].map(r => `| ${r.join(' | ')} |`).join('\n'),
  `*Source:* Synthetic Author (2026). Scientific output SYN-basalt-cdr version ${v} (bundle sha256 ${String(v).repeat(16)}), ` +
    'computed by Workbench workspace.workbench.uncertainty-propagation through its governed Workspace adapter.'].join('\n\n');
const before = ['# Synthetic Paper', '', '## Results', '', 'Results paragraph.', '', group(1), '', '## Discussion', '',
  'Final paragraph.', ''].join('\n');

const summary = v => ({version: v, registeredAt: '2026-11-20T10:0' + v + ':00', title: 'SYNTHETIC estimated CO2 removal',
  caption: 'c', application: 'workbench', applicationLabel: 'Workbench', evidenceClass: 'modelled', visibility: 'private',
  insertable: true, chart: {artifactId: chart(v)}});
const SEARCH = {outputs: [{outputId: 'SYN-basalt-cdr', application: 'workbench', latestVersion: 2,
  latest: summary(2), versions: [summary(2), summary(1)]}],
  applications: [{application: 'workspace-notebook', label: 'Workspace Notebook Desk', outputs: 0},
                 {application: 'workbench', label: 'Workbench', outputs: 1}, {application: 'decision-studio', label: 'Decision Studio', outputs: 0}]};

const browser = await chromium.launch({headless: true});
let page, errors, checks = 0;
const value = () => page.locator('#manuscript').inputValue();
const statusText = () => page.locator('#status').textContent();
const ok = (cond, label) => { assert.ok(cond, label); checks++; };

async function open(manuscript, visual = true) {
  if (page) await page.close();
  page = await browser.newPage({viewport: {width: 1100, height: 900}});
  errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.setContent(`<!doctype html><html><body>
    <div id="status"></div>
    <section><input id="scoQuery"><select id="scoApp"></select><button id="scoSearch">Search</button><button id="scoOpen">Insert</button>
      <div id="scoPanel"></div><div id="scoResults"></div><div id="scoPreview"></div></section>
    <button id="visualMode"></button><button id="sourceMode"></button>
    <div id="visualTools"><button id="addHeading"></button><button id="addParagraph"></button><button id="addList"></button><button id="addQuote"></button><button id="addEquation"></button></div><div id="visualBlocks"></div>
    <textarea id="manuscript" rows="30" cols="90"></textarea></body></html>`);
  await page.addScriptTag({content: `'use strict';
    const E = id => document.getElementById(id);
    const pub = '/pub';
    const state = {project: 'synthetic', citations: [], documentRevision: 3};
    function status(message, error = false) { E('status').textContent = message; E('status').dataset.error = String(error); }
    function run(fn) { return async () => { try { await fn(); } catch (error) { status(error.message, true); } }; }
    function el(tag, text, cls) { const n = document.createElement(tag); if (text != null) n.textContent = text; if (cls) n.className = cls; return n; }
    function path(s) { return s; }
    function markDirty() { window.dirty = (window.dirty || 0) + 1; }
    async function preview() {}
    window.calls = [];
    async function api(url) {
      window.calls.push(url);
      if (url.includes('/insertion')) { const v = +url.match(/versions\\/(\\d+)/)[1]; return {markdown: ${JSON.stringify({1: group(1), 2: group(2)})}[v] + '\\n', chartArtifactId: 'sco-0123456789-SYN-basalt-cdr-v' + v + '-chart'}; }
      if (url.includes('/versions/')) { const v = +url.match(/versions\\/(\\d+)/)[1]; return {outputId: 'SYN-basalt-cdr', version: v, table: {rows: ${JSON.stringify(ROWS)}[v]}}; }
      const app = new URL('http://x' + url).searchParams.get('application');
      const r = ${JSON.stringify(SEARCH)};
      return app && app !== 'workbench' ? {...r, outputs: []} : r;
    }
    E('manuscript').value = ${JSON.stringify(manuscript)};
    ${host}`});
  await page.addScriptTag({path: path.join(app, 'reporting_publication_tiptap.bundle.js')});
  await page.waitForSelector('[data-sc-research-editor="tiptap"]');
  if (!visual) await page.click('#sourceMode');
}

const card = () => page.locator('#scoResults .asset').first();
const blocks = md => md.trim().split(/\n\n+/).map(b => b.split('\n')[0].slice(0, 30));

// 1. Search lists the Workbench output with its source, the draft's version, and an explicit update action.
await open(before);
await page.click('#scoSearch');
await page.waitForSelector('#scoResults .asset');
ok((await card().locator('.sco-app').textContent()) === 'Workbench', 'source application badge');
ok((await card().textContent()).includes('In this draft: v1'), 'the draft version is shown');
const options = await page.locator('#scoApp option').allTextContents();
ok(options.join('|') === 'All sources|Workspace Notebook Desk (0)|Workbench (1)|Decision Studio (0)', 'application filter: ' + options);
await page.selectOption('#scoApp', 'decision-studio');
await page.waitForFunction(() => document.querySelector('#scoResults .empty'));
ok((await page.evaluate(() => window.calls.at(-1))).includes('application=decision-studio'), 'filter is sent');
await page.selectOption('#scoApp', '');
await page.waitForSelector('#scoResults .asset');

// 2. Update v1 -> v2 in the visual editor: the group is replaced in place, nothing else changes.
await card().locator('button.sco-update').click();
await page.waitForFunction(() => /updated from v1 to v2/.test(document.getElementById('status').textContent));
let md = await value();
ok(!md.includes(chart(1)) && md.split(chart(2)).length === 2, 'v1 replaced by exactly one v2');
ok(JSON.stringify(blocks(md)) === JSON.stringify(blocks(before.replace(group(1), group(2)))), 'v2 group in v1\'s place, order kept');
ok(md.includes('version 2 (bundle') && /\|\s*20\.0\s*\|\s*0\.600\s*\|/.test(md), 'v2 table rows');
ok(md.startsWith('# Synthetic Paper\n\n## Results\n\nResults paragraph.\n\n') && md.trimEnd().endsWith('## Discussion\n\nFinal paragraph.'),
  'every other block unchanged');
ok((await statusText()).includes('Saved revision 3 still pins v1'), 'status says the saved revision keeps v1');
ok(await page.locator('.sc-doc-page .tiptap figure').count() === 1, 'one figure in the visual editor after the update');
ok(!(await card().textContent()).includes('Update'), 'no update offered once the latest version is in the draft');

// 3. An edited group is never replaced.
await open(before.replace('| 10.0 | 0.330 |', '| 10.0 | 0.331 |'));
await page.click('#scoSearch');
await card().locator('button.sco-update').click();
await page.waitForFunction(() => document.getElementById('status').dataset.error === 'true');
ok((await statusText()).includes('edited or split up') && (await value()) === before.replace('| 10.0 | 0.330 |', '| 10.0 | 0.331 |'),
  'edited table: refused, manuscript unchanged');
await open(before.replace(group(1), group(1).replace('\n\n**Table:', '\n\nInserted sentence.\n\n**Table:')));
await page.click('#scoSearch');
await card().locator('button.sco-update').click();
await page.waitForFunction(() => document.getElementById('status').dataset.error === 'true');
ok((await statusText()).includes('edited or split up'), 'split group: refused');

// 4. The same update in Markdown source mode.
await open(before, false);
await page.click('#scoSearch');
await card().locator('button.sco-update').click();
await page.waitForFunction(() => /updated from v1 to v2/.test(document.getElementById('status').textContent));
ok((await value()) === before.replace(group(1), group(2)), 'source mode: byte-exact replacement of the group only');

// 5. Both versions present: the latest is already in the draft, so no update is offered.
await open(before.replace('Final paragraph.', 'Final paragraph.\n\n' + group(2)));
await page.click('#scoSearch');
await page.waitForSelector('#scoResults .asset');
ok((await card().textContent()).includes('In this draft: v2, v1') && (await card().locator('button.sco-update').count()) === 0,
  'v1 and v2 both present: no update offered');

ok(errors.length === 0, 'no page errors: ' + errors.join('; '));
await browser.close();
console.log(`SC-OUTPUT-02 browser PASS: ${checks} picker and update checks`);
