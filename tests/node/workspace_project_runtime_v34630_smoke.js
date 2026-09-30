'use strict';
const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const contract = require(path.join(root, 'app/core/workspace-host-adapter-contract-v11.js'));
const transportFactory = require(path.join(root, 'app/client/workspace-transport-v34620.js'));
const authFactory = require(path.join(root, 'app/client/workspace-auth-context-v34620.js'));
const apiFactory = require(path.join(root, 'app/client/workspace-api-client-v34620.js'));
const projectFactory = require(path.join(root, 'app/projects/workspace-project-runtime-v34630.js'));
const kernelFactory = require(path.join(root, 'app/core/workspace-application-kernel-v34630.js'));

const memory = { projects: [], activeProjectId: null, writes: 0, renders: 0, cleanup: [] };
const port = {
  snapshot() { return { projects: memory.projects, activeProjectId: memory.activeProjectId }; },
  replaceProjects(projects) { memory.projects = projects; },
  setActiveProjectId(id) { memory.activeProjectId = id; },
  persist() { memory.writes += 1; return true; },
  render() { memory.renders += 1; },
  cleanupReferences(id) { memory.cleanup.push(id); },
  confirmDelete() { return true; }
};

const fakeFetch = async () => ({
  ok: true,
  status: 200,
  headers: { get() { return 'application/json'; } },
  async json() { return { ok: true }; },
  async text() { return ''; }
});

(async () => {
  const host = contract.create({ host: 'standalone', workspaceVersion: '3.46.3.0' });
  const transport = transportFactory.createDirect({ baseUrl: 'https://workspace-api.example.test', fetchImpl: fakeFetch });
  const auth = authFactory.createAnonymous();
  const api = apiFactory.create({ transport, auth });
  const projects = projectFactory.create({ port });

  const kernel = kernelFactory.createKernel({ hostConfig: { host: 'standalone' } });
  kernel.registerHostAdapter(host);
  kernel.registerTransport(transport);
  kernel.registerAuth(auth);
  kernel.registerApiClient(api);
  kernel.registerProjectLifecycle(projects);
  await kernel.boot();

  const created = await kernel.createProject({ title: 'Extracted runtime project', description: 'Standalone project runtime' });
  assert.ok(created && created.id);
  assert.equal(memory.projects.length, 1);
  assert.equal(memory.activeProjectId, created.id);

  const opened = await kernel.openProject(created.id);
  assert.equal(opened.id, created.id);

  const deleted = await kernel.deleteProject(created.id, { confirm: true });
  assert.equal(deleted, true);
  assert.equal(memory.projects.length, 0);
  assert.equal(memory.activeProjectId, null);
  assert.deepEqual(memory.cleanup, [created.id]);

  const state = kernel.inspect();
  assert.equal(state.projectRuntimeExtracted, true);
  assert.equal(state.wordpressRequired, false);

  console.log('WORKSPACE_STANDALONE_BOOT=PASS');
  console.log('WORKSPACE_NEW_PROJECT_STANDALONE=PASS');
  console.log('WORKSPACE_PROJECT_OPEN_STANDALONE=PASS');
  console.log('WORKSPACE_PROJECT_DELETE_STANDALONE=PASS');
  console.log('WORKSPACE_PROJECT_RUNTIME_EXTRACTED=PASS');
  console.log('WORKSPACE_PROJECT_STATE_PORT=PASS');
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
