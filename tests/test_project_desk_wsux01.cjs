'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const desk = require('../standalone/project-desk.js');

const html = fs.readFileSync(path.join(__dirname, '../standalone/index.html'), 'utf8');
const js = fs.readFileSync(path.join(__dirname, '../standalone/project-desk.js'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, '../standalone/project-desk.css'), 'utf8');

test('project desk is installed in standalone shell using additive local assets', () => {
  assert.match(html, /href="\.\/project-desk\.css"/);
  assert.match(html, /src="\.\/project-desk\.js"/);
  assert.ok(html.indexOf('./bootstrap.js') < html.indexOf('./project-desk.js'));
  assert.match(js, /sc-workspace-standalone:ready/);
});

test('single project context preserves local project identity and never implies publication', () => {
  const projects = [
    {id: 'p1', title: 'Wexford ERW', description: 'Carbon removal analysis'},
    {id: 'p2', title: 'Metrics', description: ''},
    {id: 'p3', title: 'Old project', archivedAt: '2026-11-06'}
  ];
  const value = desk.model({projects, activeProjectId: 'p1'});
  assert.deepEqual(value.projects.map(x => x.id), ['p1', 'p2']);
  assert.equal(value.activeProjectId, 'p1');
  assert.equal(value.activeTitle, 'Wexford ERW');
  assert.equal(value.outputStatus, 'not-connected');
  assert.equal(value.outputCount, null);
  assert.ok(Object.isFrozen(value));
  const missing = desk.model({projects, activeProjectId: 'p3'});
  assert.equal(missing.activeProjectId, null);
  assert.equal(missing.activeTitle, 'Choose or create a project');
});

test('user-facing sections are the existing same-page capabilities', () => {
  const tabs = desk.tabs.map(([name]) => name);
  assert.deepEqual(tabs, ['overview','sources','analysis','outputs','history','tools','projects']);
  for (const id of ['library-bridge','evidence','integrated-project','datasets',
      'models-runtimes','visual-analysis','session-timeline','research-map','launcher',
      'objects','diagnostics','projects']) {
    assert.match(html, new RegExp('id="' + id + '"'));
    assert.ok(js.includes("'" + id + "'"));
  }
  assert.match(js, /data-create-form/);
  assert.match(js, /runtime\.stateStore\.current/);
});

test('publishing is not faked or activated by the project desk', () => {
  assert.match(desk.outputNotice, /not yet linked/);
  assert.match(desk.outputNotice, /unavailable/);
  assert.match(js, /No output has been published/);
  assert.doesNotMatch(js, /fetch\s*\(/);
  assert.doesNotMatch(js, /localStorage\./);
  assert.doesNotMatch(js, /\/api\/research\/v1\/private/);
  assert.doesNotMatch(js, /\.innerHTML\s*=\s*.*(?:activeTitle|description)/);
});

test('project context stays accessible and styled without marketing panels', () => {
  assert.match(js, /aria-label="Project sections"/);
  assert.match(js, /role', 'tab'/);
  assert.match(css, /\.ws-desk-tab\[aria-selected=true\]/);
  assert.match(css, /#ff0000/);
  assert.match(css, /@media\(max-width:830px\)/);
});
