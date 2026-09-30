'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '../..');
const wpManifest = JSON.parse(fs.readFileSync(path.join(root, 'wordpress/sustainable-catalyst-workspace/assets/manifests/workspace-runtime-assets-v34680.json'), 'utf8'));
const standaloneManifest = JSON.parse(fs.readFileSync(path.join(root, 'standalone/asset-manifest-v34680.json'), 'utf8'));
const adapter = require(path.join(root, 'adapters/wordpress/workspace-wordpress-thin-adapter-v34680.js'));

(async () => {
  assert.equal(wpManifest.version, '3.46.8.0');
  assert.equal(standaloneManifest.version, '3.46.8.0');

  const shared = Object.keys(wpManifest.assets).filter((id) => (
    standaloneManifest.assets[id] && wpManifest.assets[id].shared
  ));
  assert.ok(shared.length >= 8);
  shared.forEach((id) => assert.equal(wpManifest.assets[id].sha256, standaloneManifest.assets[id].sha256));

  const rootObject = {};
  const loaded = [];
  const bridge = {
    schema: 'sc-workspace-wordpress-thin-bridge/1.1',
    workspaceVersion: '3.46.8.0',
    assetManifestUrl: 'https://example.test/assets/js/sc-workspace-runtime-asset-manifest-v34680.js',
    config: {
      assetBase: 'https://example.test/assets/js/',
      apiBase: 'https://example.test/wp-json/sc-workspace/v1/backend',
      transport: 'wordpress-server-proxy'
    },
    identity: { authenticated: false }
  };

  await adapter.boot(bridge, {
    root: rootObject,
    document: null,
    loadScript: async (url, marker) => {
      loaded.push([marker, url]);
      if (marker === 'runtime-manifest') rootObject.SCWorkspaceRuntimeAssetManifest = wpManifest;
      if (marker === 'application-entry') rootObject.SCWorkspaceFrontendRuntime = { version: '3.46.8.0' };
      return true;
    }
  });

  assert.equal(loaded[0][0], 'runtime-manifest');
  assert.equal(loaded[1][0], 'application-entry');
  assert.ok(loaded[1][1].endsWith('/workspace-v3.46.8.0.js'));
  assert.equal(rootObject.SCWorkspaceConfig.hostAgnosticAssetPipeline, true);

  console.log('WORKSPACE_HOST_AGNOSTIC_ASSET_PIPELINE=PASS');
  console.log('WORKSPACE_SHARED_ASSET_CHECKSUM_PARITY=PASS');
  console.log('WORKSPACE_WORDPRESS_MANIFEST_BOOT=PASS');
  console.log('WORKSPACE_STANDALONE_MANIFEST_BOOT_CONTRACT=PASS');
})();
