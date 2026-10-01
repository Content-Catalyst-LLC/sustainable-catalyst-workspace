(function (root) {
  'use strict';

  const config = Object.freeze({
    schema: 'sc-workspace-standalone-config/1.0',
    workspaceVersion: '3.47.0',
    host: 'standalone',
    apiBase: 'https://workspace-api.sustainablecatalyst.com',
    assetBase: './assets/',
    storageKey: 'sc_workspace',
    legacyStorageKey: 'sc_workspace_v0_1',
    recoveryStorageKey: 'sc_workspace_recovery_v0_8_2',
    lastGoodStorageKey: 'sc_workspace_last_good_v1',
    optionalModules: [
      {
        id: 'workspace.linguistics.original-language-corpus',
        assetId: 'workspace.linguistics.original-language-corpus',
        version: '3.47.0',
        title: 'Original-Language Text & Corpus Workspace',
        optional: true,
        enabled: true,
        dependsOn: ['core.api'],
        capabilities: [
          'workspace.linguistics.original-language',
          'workspace.linguistics.corpus',
          'workspace.linguistics.transformation-provenance'
        ],
        source: 'workspace',
        global: 'SCWorkspaceOriginalLanguageCorpusWorkspace'
      }
    ],
    automaticBackendHealthCheck: false,
    wordpressRequired: false
  });

  root.SCWorkspaceStandaloneConfig = config;
  root.SCWorkspaceConfig = config;
})(typeof globalThis !== 'undefined' ? globalThis : this);
