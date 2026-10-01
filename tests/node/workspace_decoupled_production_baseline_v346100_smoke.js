'use strict';

const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const baseline = require(path.join(root, 'app/core/workspace-decoupled-production-baseline-v346100.js'));
const kernelFactory = require(path.join(root, 'app/core/workspace-application-kernel-v346100.js'));
const standaloneFactory = require(path.join(root, 'app/standalone/workspace-standalone-runtime-v346100.js'));
const hostContract = require(path.join(root, 'app/core/workspace-host-adapter-contract-v11.js'));
const hostAdapterFactory = require(path.join(root, 'adapters/standalone/workspace-standalone-host-adapter-v346100.js'));
const transportFactory = require(path.join(root, 'app/client/workspace-transport-v34620.js'));
const authFactory = require(path.join(root, 'app/client/workspace-auth-context-v34620.js'));
const apiFactory = require(path.join(root, 'app/client/workspace-api-client-v34620.js'));
const persistenceFactory = require(path.join(root, 'app/state/workspace-persistence-runtime-v34640.js'));
const stateStoreFactory = require(path.join(root, 'app/state/workspace-state-store-v34640.js'));
const projectFactory = require(path.join(root, 'app/projects/workspace-project-runtime-v34630.js'));
const moduleRegistryFactory = require(path.join(root, 'app/core/workspace-module-registry-v34650.js'));

class MemoryStorage {
  constructor() { this.data = {}; }
  getItem(key) { return Object.prototype.hasOwnProperty.call(this.data, key) ? this.data[key] : null; }
  setItem(key, value) { this.data[key] = String(value); }
  removeItem(key) { delete this.data[key]; }
}

(async () => {
  const runtime = await standaloneFactory.create({
    config: {
      workspaceVersion: '3.46.10.0',
      host: 'standalone',
      apiBase: 'https://workspace-api.example.test',
      assetBase: './assets/',
      storageKey: 'sc_workspace'
    },
    storage: new MemoryStorage(),
    fetchImpl: async () => ({
      ok: true,
      status: 200,
      headers: { get() { return 'application/json'; } },
      async json() { return { ok: true, version: '3.46.10.0' }; },
      async text() { return ''; }
    }),
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

  const state = baseline.assert({
    kernel: runtime.kernel.inspect(),
    runtime: runtime.inspect(),
    registry: runtime.moduleRegistry.inspect()
  });

  assert.equal(state.productionBaseline, true);
  assert.equal(state.rollbackRelease, '3.46.9.0');
  assert.equal(state.invariants.wordpressRequiredByCore, false);
  assert.equal(state.invariants.wordpressOwnsProjectLogic, false);
  assert.equal(state.invariants.wordpressOwnsCanonicalState, false);
  assert.equal(state.invariants.wordpressOwnsModuleBoot, false);
  assert.equal(state.invariants.standaloneBootCertified, true);
  assert.equal(state.invariants.canonicalBackendAuthority, true);

  console.log('WORKSPACE_DECOUPLED_PRODUCTION_BASELINE=PASS');
  console.log('WORKSPACE_WORDPRESS_THIN_HOST_BASELINE=PASS');
  console.log('WORKSPACE_STANDALONE_PRODUCTION_BASELINE=PASS');
  console.log('WORKSPACE_CANONICAL_BACKEND_AUTHORITY=PASS');
  console.log('WORKSPACE_OPTIONAL_MODULE_FAILURE_ISOLATION=PASS');
})();
