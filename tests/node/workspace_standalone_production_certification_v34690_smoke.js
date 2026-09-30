'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const hostContract = require(path.join(root, 'app/core/workspace-host-adapter-contract-v11.js'));
const hostAdapterFactory = require(path.join(root, 'adapters/standalone/workspace-standalone-host-adapter-v34690.js'));
const transportFactory = require(path.join(root, 'app/client/workspace-transport-v34620.js'));
const authFactory = require(path.join(root, 'app/client/workspace-auth-context-v34620.js'));
const apiFactory = require(path.join(root, 'app/client/workspace-api-client-v34620.js'));
const persistenceFactory = require(path.join(root, 'app/state/workspace-persistence-runtime-v34640.js'));
const stateStoreFactory = require(path.join(root, 'app/state/workspace-state-store-v34640.js'));
const projectFactory = require(path.join(root, 'app/projects/workspace-project-runtime-v34630.js'));
const moduleRegistryFactory = require(path.join(root, 'app/core/workspace-module-registry-v34650.js'));
const kernelFactory = require(path.join(root, 'app/core/workspace-application-kernel-v34690.js'));
const standaloneFactory = require(path.join(root, 'app/standalone/workspace-standalone-runtime-v34690.js'));
const certification = require(path.join(root, 'app/standalone/workspace-standalone-production-certification-v34690.js'));

class MemoryStorage {
  constructor() { this.data = {}; }
  getItem(key) { return Object.prototype.hasOwnProperty.call(this.data, key) ? this.data[key] : null; }
  setItem(key, value) { this.data[key] = String(value); }
  removeItem(key) { delete this.data[key]; }
}

const observed = [];
const fakeFetch = async (url) => {
  observed.push(String(url));
  return {
    ok: true,
    status: 200,
    headers: { get() { return 'application/json'; } },
    async json() { return { ok: true, version: '3.46.9.0' }; },
    async text() { return ''; }
  };
};

(async () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'standalone/asset-manifest-v34690.json'), 'utf8'));

  const runtime = await standaloneFactory.create({
    config: {
      workspaceVersion: '3.46.9.0',
      host: 'standalone',
      apiBase: 'https://workspace-api.example.test',
      assetBase: './assets/',
      storageKey: 'sc_workspace',
      assetManifest: manifest
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

  const result = await certification.certify(runtime, manifest);

  assert.equal(result.passed, true);
  assert.equal(runtime.inspect().wordpressRequired, false);
  assert.equal(runtime.inspect().directBackendTransport, true);
  assert.equal(runtime.kernel.inspect().standaloneProductionCertificationCapable, true);

  const health = await runtime.health();
  assert.equal(health.ok, true);
  assert.equal(observed[0], 'https://workspace-api.example.test/health');

  const optional = moduleRegistryFactory.create();
  optional.register({ id: 'optional.failure', optional: true }, async () => {
    throw new Error('intentional certification failure');
  });
  await optional.loadAll({});
  assert.equal(optional.state('optional.failure').state, 'failed');
  assert.equal(optional.inspect().optionalFailureIsolation, true);

  console.log('WORKSPACE_STANDALONE_BOOT=PASS');
  console.log('WORKSPACE_WORDPRESS_ABSENT_CERTIFICATION=PASS');
  console.log('WORKSPACE_STANDALONE_DIRECT_TRANSPORT=PASS');
  console.log('WORKSPACE_STANDALONE_PERSISTENCE_ROUNDTRIP=PASS');
  console.log('WORKSPACE_STANDALONE_PROJECT_LIFECYCLE=PASS');
  console.log('WORKSPACE_OPTIONAL_MODULE_FAILURE_ISOLATION=PASS');
  console.log('WORKSPACE_STANDALONE_RUNTIME_PRODUCTION_CERTIFICATION=PASS');
})();
