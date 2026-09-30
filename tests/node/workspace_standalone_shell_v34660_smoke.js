'use strict';
const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const hostContract = require(path.join(root, 'app/core/workspace-host-adapter-contract-v11.js'));
const hostAdapterFactory = require(path.join(root, 'adapters/standalone/workspace-standalone-host-adapter-v34660.js'));
const transportFactory = require(path.join(root, 'app/client/workspace-transport-v34620.js'));
const authFactory = require(path.join(root, 'app/client/workspace-auth-context-v34620.js'));
const apiFactory = require(path.join(root, 'app/client/workspace-api-client-v34620.js'));
const persistenceFactory = require(path.join(root, 'app/state/workspace-persistence-runtime-v34640.js'));
const stateStoreFactory = require(path.join(root, 'app/state/workspace-state-store-v34640.js'));
const projectFactory = require(path.join(root, 'app/projects/workspace-project-runtime-v34630.js'));
const moduleRegistryFactory = require(path.join(root, 'app/core/workspace-module-registry-v34650.js'));
const kernelFactory = require(path.join(root, 'app/core/workspace-application-kernel-v34660.js'));
const standaloneFactory = require(path.join(root, 'app/standalone/workspace-standalone-runtime-v34660.js'));

class MemoryStorage {
  constructor() { this.data = {}; }
  getItem(key) { return Object.prototype.hasOwnProperty.call(this.data, key) ? this.data[key] : null; }
  setItem(key, value) { this.data[key] = String(value); }
  removeItem(key) { delete this.data[key]; }
}

let observedUrl = '';
const fakeFetch = async (url) => {
  observedUrl = String(url);
  return {
    ok: true,
    status: 200,
    headers: { get() { return 'application/json'; } },
    async json() { return { ok: true, version: '3.46.6.0' }; },
    async text() { return ''; }
  };
};

(async () => {
  const runtime = await standaloneFactory.create({
    config: {
      workspaceVersion: '3.46.6.0',
      host: 'standalone',
      apiBase: 'https://workspace-api.example.test',
      assetBase: './assets/',
      storageKey: 'sc_workspace'
    },
    storage: new MemoryStorage(),
    fetchImpl: fakeFetch,
    hostContract,
    hostAdapterFactory,
    transportFactory,
    authFactory,
    apiFactory,
    persistenceFactory,
    stateStoreFactory,
    projectFactory,
    moduleRegistryFactory,
    kernelFactory
  });

  assert.equal(runtime.host, 'standalone');
  assert.equal(runtime.inspect().wordpressRequired, false);
  assert.equal(runtime.kernel.inspect().host, 'standalone');
  assert.equal(runtime.kernel.inspect().moduleRegistryRegistered, true);

  const project = await runtime.kernel.createProject({
    title: 'Standalone project',
    description: 'Created without WordPress'
  });
  assert.ok(project && project.id);

  let projects = await runtime.kernel.listProjects();
  assert.equal(projects.length, 1);
  assert.equal(projects[0].title, 'Standalone project');

  const health = await runtime.health();
  assert.equal(health.ok, true);
  assert.equal(observedUrl, 'https://workspace-api.example.test/health');

  const projectsCapability = runtime.moduleRegistry.capability('workspace.projects');
  assert.ok(projectsCapability);
  assert.equal(projectsCapability.moduleId, 'core.project-runtime');

  assert.equal(await runtime.kernel.deleteProject(project.id, { confirm: false }), true);
  projects = await runtime.kernel.listProjects();
  assert.equal(projects.length, 0);

  console.log('WORKSPACE_STANDALONE_BOOT=PASS');
  console.log('WORKSPACE_WORDPRESS_ABSENT_CERTIFICATION=PASS');
  console.log('WORKSPACE_STANDALONE_DIRECT_TRANSPORT=PASS');
  console.log('WORKSPACE_STANDALONE_PROJECT_CREATE=PASS');
  console.log('WORKSPACE_STANDALONE_PROJECT_OPEN_DELETE=PASS');
  console.log('WORKSPACE_STANDALONE_MODULE_REGISTRY=PASS');
})();
