'use strict';
const assert = require('assert');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const factory = require(path.join(root, 'app/core/workspace-module-registry-v34650.js'));

(async () => {
  const issues = [];
  const registry = factory.create({ onIssue: (issue) => issues.push(issue) });

  registry.registerReady({
    id: 'core.api',
    version: '3.46.5.0',
    optional: false,
    capabilities: ['workspace.api']
  }, { request() {} });

  registry.register({
    id: 'optional.good',
    version: '1.0.0',
    optional: true,
    dependsOn: ['core.api'],
    capabilities: ['feature.good']
  }, async () => ({ value: 42 }));

  registry.register({
    id: 'optional.bad',
    version: '1.0.0',
    optional: true,
    capabilities: ['feature.bad']
  }, async () => {
    throw new Error('intentional optional failure');
  });

  registry.register({
    id: 'optional.dependent',
    version: '1.0.0',
    optional: true,
    dependsOn: ['optional.bad'],
    capabilities: ['feature.dependent']
  }, async () => ({ shouldNotLoad: true }));

  const snapshot = await registry.loadAll({ test: true });

  assert.equal(registry.state('core.api').state, 'ready');
  assert.equal(registry.state('optional.good').state, 'ready');
  assert.equal(registry.state('optional.bad').state, 'failed');
  assert.equal(registry.state('optional.dependent').state, 'blocked');
  assert.equal(registry.capability('feature.good').provider.value, 42);
  assert.equal(registry.capability('feature.bad'), null);
  assert.equal(snapshot.optionalFailureIsolation, true);
  assert.ok(issues.some((issue) => issue.moduleId === 'optional.bad'));

  const required = factory.create();
  required.register({
    id: 'required.bad',
    optional: false
  }, async () => { throw new Error('required failure'); });

  let requiredFailed = false;
  try {
    await required.loadAll({});
  } catch (_) {
    requiredFailed = true;
  }
  assert.equal(requiredFailed, true);

  console.log('WORKSPACE_MODULE_REGISTRY=PASS');
  console.log('WORKSPACE_CAPABILITY_RESOLUTION=PASS');
  console.log('WORKSPACE_OPTIONAL_MODULE_FAILURE_ISOLATION=PASS');
  console.log('WORKSPACE_MODULE_DEPENDENCY_BLOCKING=PASS');
  console.log('WORKSPACE_REQUIRED_MODULE_FAILURE_BLOCKS=PASS');
})();
