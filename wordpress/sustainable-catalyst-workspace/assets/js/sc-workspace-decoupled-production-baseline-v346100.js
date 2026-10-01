(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceDecoupledProductionBaseline = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-decoupled-production-baseline/1.0';
  const VERSION = '3.46.10.0';

  const INVARIANTS = Object.freeze({
    wordpressRequiredByCore: false,
    wordpressOwnsProjectLogic: false,
    wordpressOwnsCanonicalState: false,
    wordpressOwnsPersistence: false,
    wordpressOwnsModuleBoot: false,
    wordpressScriptEntrypoints: 1,
    standaloneBootCertified: true,
    standaloneDirectTransport: true,
    canonicalBackendAuthority: true,
    canonicalAssetPipeline: true,
    sharedAssetChecksumParity: true,
    optionalModuleFailureIsolation: true,
    databaseMigration: false,
    storageSchemaMigration: false
  });

  function inspect(context) {
    const source = context && typeof context === 'object' ? context : {};
    const kernel = source.kernel && typeof source.kernel === 'object' ? source.kernel : {};
    const runtime = source.runtime && typeof source.runtime === 'object' ? source.runtime : {};
    const registry = source.registry && typeof source.registry === 'object' ? source.registry : {};

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      productionBaseline: true,
      rollbackRelease: '3.46.9.0',
      invariants: INVARIANTS,
      observed: Object.freeze({
        kernelWordpressRequired: kernel.wordpressRequired,
        kernelStandaloneCertified: kernel.standaloneProductionCertificationCapable,
        kernelDecoupledBaseline: kernel.decoupledProductionBaseline,
        runtimeWordpressRequired: runtime.wordpressRequired,
        runtimeDirectBackendTransport: runtime.directBackendTransport,
        registryOptionalFailureIsolation: registry.optionalFailureIsolation
      })
    });
  }

  function assert(context) {
    const state = inspect(context);
    const observed = state.observed;

    const checks = [
      observed.kernelWordpressRequired === false,
      observed.kernelStandaloneCertified === true,
      observed.kernelDecoupledBaseline === true,
      observed.runtimeWordpressRequired === false,
      observed.runtimeDirectBackendTransport === true,
      observed.registryOptionalFailureIsolation === true
    ];

    if (!checks.every(Boolean)) {
      throw new Error('Workspace decoupled production baseline invariant failed');
    }
    return state;
  }

  return Object.freeze({
    schema: SCHEMA,
    version: VERSION,
    productionBaseline: true,
    rollbackRelease: '3.46.9.0',
    invariants: INVARIANTS,
    inspect,
    assert
  });
});
