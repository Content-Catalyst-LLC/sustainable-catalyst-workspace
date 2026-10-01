(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceStandaloneProductionCertification = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-standalone-production-certification/1.0';
  const VERSION = '3.51.0';

  function gate(name, ok, detail) {
    return Object.freeze({
      name: String(name),
      ok: Boolean(ok),
      detail: String(detail || '')
    });
  }

  async function certify(runtime, manifest) {
    if (!runtime || typeof runtime.inspect !== 'function') {
      throw new Error('Standalone production certification requires a runtime');
    }
    if (!manifest || manifest.schema !== 'sc-workspace-runtime-asset-manifest/1.0') {
      throw new Error('Standalone production certification requires a runtime asset manifest');
    }

    const runtimeState = runtime.inspect();
    const kernelState = runtime.kernel && runtime.kernel.inspect ? runtime.kernel.inspect() : {};
    const registryState = runtime.moduleRegistry && runtime.moduleRegistry.inspect ? runtime.moduleRegistry.inspect() : {};
    const persistenceState = runtime.persistence && runtime.persistence.inspect ? runtime.persistence.inspect() : {};
    const stateStoreState = runtime.stateStore && runtime.stateStore.inspect ? runtime.stateStore.inspect() : {};

    const before = await runtime.kernel.listProjects();
    const project = await runtime.kernel.createProject({
      title: 'Production certification project',
      description: 'Ephemeral v3.51.0 certification object'
    });
    const opened = project ? await runtime.kernel.openProject(project.id, { restoreArchived: true }) : null;
    const during = await runtime.kernel.listProjects();
    const deleted = project ? await runtime.kernel.deleteProject(project.id, { confirm: false }) : false;
    const after = await runtime.kernel.listProjects();

    const gates = [
      gate('WORKSPACE_STANDALONE_BOOT', runtimeState.host === 'standalone', runtimeState.host),
      gate('WORKSPACE_WORDPRESS_ABSENT_CERTIFICATION', runtimeState.wordpressRequired === false, String(runtimeState.wordpressRequired)),
      gate('WORKSPACE_STANDALONE_DIRECT_TRANSPORT', runtimeState.directBackendTransport === true, String(runtimeState.directBackendTransport)),
      gate('WORKSPACE_STANDALONE_ASSET_MANIFEST', manifest.host === 'standalone' && manifest.version === VERSION, `${manifest.host}:${manifest.version}`),
      gate('WORKSPACE_STANDALONE_KERNEL', kernelState.booted === true && kernelState.wordpressRequired === false, JSON.stringify({ booted: kernelState.booted, wordpressRequired: kernelState.wordpressRequired })),
      gate('WORKSPACE_STANDALONE_MODULE_REGISTRY', registryState.optionalFailureIsolation === true, String(registryState.optionalFailureIsolation)),
      gate('WORKSPACE_STANDALONE_PERSISTENCE', persistenceState.verifiedReadAfterWrite === true, String(persistenceState.verifiedReadAfterWrite)),
      gate('WORKSPACE_STANDALONE_STATE_STORE', stateStoreState.canonicalStateOwned === true, String(stateStoreState.canonicalStateOwned)),
      gate('WORKSPACE_STANDALONE_PROJECT_CREATE', Boolean(project && during.some((item) => item.id === project.id)), project ? project.id : ''),
      gate('WORKSPACE_STANDALONE_PROJECT_OPEN', Boolean(project && opened && opened.id === project.id), opened && opened.id),
      gate('WORKSPACE_STANDALONE_PROJECT_DELETE', Boolean(deleted && !after.some((item) => project && item.id === project.id)), String(deleted)),
      gate('WORKSPACE_STANDALONE_PROJECT_COUNT_RESTORED', after.length === before.length, `${before.length}->${after.length}`)
    ];

    const passed = gates.every((item) => item.ok);
    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      passed,
      gateCount: gates.length,
      gates: Object.freeze(gates),
      runtime: runtimeState,
      manifestVersion: manifest.version
    });
  }

  return Object.freeze({ schema: SCHEMA, version: VERSION, certify });
});
