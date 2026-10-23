'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const scope = {globalThis: null};
scope.globalThis = scope;
vm.runInNewContext(fs.readFileSync(path.join(root, 'standalone/config.js'), 'utf8'), scope);
const config = scope.SCWorkspaceStandaloneConfig;
const transportFactory = require(path.join(root, 'standalone/assets/sc-workspace-transport-v3710.js'));
let request;
const transport = transportFactory.createDirect({
  baseUrl: config.apiBase,
  fetchImpl: async (url, init) => {
    request = {url, init};
    return {ok: true, headers: {get: () => 'application/json'}, json: async () => ({ok: true})};
  },
});
(async () => {
  await transport.request({method: 'GET', path: config.serverProjectBootstrapEndpoint});
  assert.equal(request.url, '/v1/user-workspace/bootstrap');
  assert.equal(request.init.credentials, 'include');
  assert.equal(config.sessionEndpoint, '/v1/session');
  console.log('WXR-09.3 same-origin signed-session transport passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
