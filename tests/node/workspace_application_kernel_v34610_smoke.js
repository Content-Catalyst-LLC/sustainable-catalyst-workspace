'use strict';
const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const contract = require(path.join(root, 'app/core/workspace-host-adapter-contract-v1.js'));
const factory = require(path.join(root, 'app/core/workspace-application-kernel-v34610.js'));

const host = contract.create({
  host: 'standalone',
  workspaceVersion: '3.46.1.0',
  assetBase: 'https://example.invalid/assets/',
  apiBase: 'https://example.invalid/api/'
});

const projects = [];
let activeProjectId = null;
const lifecycle = {
  name: 'standalone-memory-smoke',
  version: '3.46.1.0',
  listProjects() { return projects.map((p) => ({...p})); },
  createProject(input) {
    const p = { id: 'project-1', title: String(input.title || 'Untitled project') };
    projects.push(p);
    activeProjectId = p.id;
    return {...p};
  },
  openProject(id) {
    const p = projects.find((item) => item.id === id);
    if (!p) return null;
    activeProjectId = p.id;
    return {...p};
  },
  deleteProject(id) {
    const index = projects.findIndex((item) => item.id === id);
    if (index < 0) return false;
    projects.splice(index, 1);
    if (activeProjectId === id) activeProjectId = null;
    return true;
  }
};

(async () => {
  const kernel = factory.createKernel({ hostConfig: { host: 'standalone' } });
  kernel.registerHostAdapter(host);
  kernel.registerProjectLifecycle(lifecycle);
  const boot = await kernel.boot();
  assert.equal(boot.booted, true);
  assert.equal(boot.host, 'standalone');
  assert.equal(boot.wordpressRequired, false);

  const created = await kernel.createProject({ title: 'Standalone kernel project' });
  assert.equal(created.id, 'project-1');
  assert.equal((await kernel.listProjects()).length, 1);

  const opened = await kernel.openProject(created.id);
  assert.equal(opened.id, created.id);

  const deleted = await kernel.deleteProject(created.id);
  assert.equal(deleted, true);
  assert.equal((await kernel.listProjects()).length, 0);

  console.log('WORKSPACE_STANDALONE_BOOT=PASS');
  console.log('WORKSPACE_NEW_PROJECT_STANDALONE=PASS');
  console.log('WORKSPACE_PROJECT_OPEN_STANDALONE=PASS');
  console.log('WORKSPACE_PROJECT_DELETE_STANDALONE=PASS');
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
