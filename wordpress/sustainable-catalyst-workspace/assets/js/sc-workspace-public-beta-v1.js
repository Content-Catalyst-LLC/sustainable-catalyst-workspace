(() => {
  'use strict';

  const SCHEMA = 'sc-workspace-public-beta-readiness/1.0';
  const QUICK_STARTS = Object.freeze([
    { id: 'research-investigation', label: 'Research investigation', mode: 'guide', description: 'Start with a bounded question, sources, evidence, analysis, and a reusable briefing.' },
    { id: 'analytical-assessment', label: 'Analytical assessment', mode: 'guide', description: 'Structure variables, assumptions, methods, comparisons, and findings.' },
    { id: 'decision-case', label: 'Decision case', mode: 'guide', description: 'Frame alternatives, criteria, evidence, risks, and rationale.' },
    { id: 'publication-preparation', label: 'Publication preparation', mode: 'guide', description: 'Prepare a traceable publication draft without bypassing review.' }
  ]);

  function activeProjects(state) {
    return (Array.isArray(state?.projects) ? state.projects : []).filter(project => project && !project.archivedAt);
  }

  function summary(state) {
    const projects = activeProjects(state);
    const objects = projects.reduce((sum, project) => sum + (Array.isArray(project.objects) ? project.objects.filter(object => !object?.archivedAt).length : 0), 0);
    const milestones = projects.reduce((sum, project) => sum + (Array.isArray(project.lifecycle?.milestones) ? project.lifecycle.milestones.length : 0), 0);
    const restorePoints = Array.isArray(state?.versionHistory?.restorePoints) ? state.versionHistory.restorePoints.length : 0;
    const safeActions = Array.isArray(state?.safeActions?.history) ? state.safeActions.history.length : 0;
    const receipts = Array.isArray(state?.reconciliation?.receipts) ? state.reconciliation.receipts.length : 0;
    const syncEnrollments = Array.isArray(state?.crossDeviceSync?.enrollments) ? state.crossDeviceSync.enrollments.length : 0;
    const sorted = projects.slice().sort((a, b) => String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')));
    return {
      schema: SCHEMA,
      projectCount: projects.length,
      objectCount: objects,
      milestoneCount: milestones,
      restorePointCount: restorePoints,
      safeActionCount: safeActions,
      reconciliationReceiptCount: receipts,
      syncEnrollmentCount: syncEnrollments,
      recentProjects: sorted.slice(0, 3).map(project => ({
        id: String(project.id || ''),
        title: String(project.title || 'Untitled project'),
        updatedAt: String(project.updatedAt || ''),
        lifecycleState: String(project.lifecycle?.state || 'draft')
      })),
      governance: {
        hiddenScore: false,
        automaticProjectCreation: false,
        automaticLifecycleAdvance: false,
        automaticCloudUpload: false,
        automaticTelemetry: false
      }
    };
  }

  function capabilities(env = globalThis) {
    const nav = env?.navigator || {};
    const win = env?.window || env;
    const storage = (() => {
      try {
        const local = win?.localStorage;
        if (!local) return false;
        const key = '__scw_beta_probe__';
        local.setItem(key, '1');
        local.removeItem(key);
        return true;
      } catch (_) { return false; }
    })();
    return {
      localStorage: storage,
      sessionStorage: Boolean(win?.sessionStorage),
      webCryptoSha256: Boolean(env?.crypto?.subtle || win?.crypto?.subtle),
      fileApi: Boolean(win?.File && win?.FileReader && win?.Blob),
      postMessage: typeof win?.postMessage === 'function',
      online: nav.onLine !== false,
      reducedMotion: Boolean(win?.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches)
    };
  }

  function readiness(capabilityState) {
    const c = capabilityState || {};
    const core = [c.localStorage, c.sessionStorage, c.fileApi];
    return {
      state: core.every(Boolean) ? 'ready' : 'limited',
      coreReady: core.every(Boolean),
      integrityReady: Boolean(c.webCryptoSha256),
      crossProductReturnReady: Boolean(c.sessionStorage && c.postMessage),
      networkAvailable: c.online !== false,
      reducedMotionPreferred: Boolean(c.reducedMotion),
      hiddenScore: false
    };
  }

  function quickStarts() { return QUICK_STARTS.map(item => ({ ...item })); }

  globalThis.SCWorkspacePublicBeta = Object.freeze({
    SCHEMA,
    QUICK_STARTS,
    summary,
    capabilities,
    readiness,
    quickStarts
  });
})();
