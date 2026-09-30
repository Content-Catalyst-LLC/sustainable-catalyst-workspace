'use strict';
const assert = require('assert');
const path = require('path');
const fs = require('fs');

const rootPath = path.resolve(__dirname, '../..');
const adapter = require(path.join(rootPath, 'adapters/wordpress/workspace-wordpress-thin-adapter-v34670.js'));

(async () => {
  const root = {};
  const loaded = [];

  const bridge = {
    schema: 'sc-workspace-wordpress-thin-bridge/1.0',
    workspaceVersion: '3.46.7.0',
    entryPointUrl: 'https://example.test/assets/js/workspace-v3.46.7.0.js',
    config: {
      apiBase: 'https://example.test/wp-json/sc-workspace/v1/backend',
      assetBase: 'https://example.test/wp-content/plugins/sustainable-catalyst-workspace/assets/js/',
      transport: 'wordpress-server-proxy',
      legacyCompatUrl: 'https://example.test/compat.js'
    },
    identity: {
      authenticated: true,
      displayName: 'Test User',
      restNonce: 'nonce'
    }
  };

  const result = await adapter.boot(bridge, {
    root,
    document: null,
    loadScript: async (url) => {
      loaded.push(url);
      root.SCWorkspaceFrontendRuntime = { version: '3.46.7.0' };
      return true;
    }
  });

  assert.equal(loaded.length, 1);
  assert.equal(loaded[0], bridge.entryPointUrl);
  assert.equal(root.SCWorkspaceConfig.host, 'wordpress');
  assert.equal(root.SCWorkspaceConfig.wordpressRequired, false);
  assert.equal(root.SCWorkspaceConfig.wordpressThinAdapter, true);
  assert.equal(root.SCWorkspaceConfig.legacyPhpScriptGraphRetired, true);
  assert.equal(root.SCWorkspaceIdentity.frontendMode, 'host-neutral-core-with-wordpress-thin-adapter');
  assert.equal(result.entryPointLoaded, true);
  assert.equal(adapter.inspect(root).phpScriptGraphRetired, true);

  const adapterSource = fs.readFileSync(
    path.join(rootPath, 'adapters/wordpress/workspace-wordpress-thin-adapter-v34670.js'),
    'utf8'
  );
  assert.equal(adapterSource.includes('localStorage'), false);
  assert.equal(adapterSource.includes('createProject('), false);
  assert.equal(adapterSource.includes('deleteProject('), false);
  assert.equal(adapterSource.includes('registerProjectLifecycle('), false);

  console.log('WORKSPACE_WORDPRESS_THIN_ADAPTER=PASS');
  console.log('WORKSPACE_WORDPRESS_THIN_BRIDGE=PASS');
  console.log('WORKSPACE_WORDPRESS_SINGLE_ENTRYPOINT_BOOT=PASS');
  console.log('WORKSPACE_WORDPRESS_HAS_ZERO_PROJECT_LOGIC=PASS');
  console.log('WORKSPACE_WORDPRESS_CORE_INDEPENDENCE=PASS');
})();
