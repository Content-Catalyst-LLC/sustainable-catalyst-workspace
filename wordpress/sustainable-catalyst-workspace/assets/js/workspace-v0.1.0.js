(() => {
  'use strict';
  const KEY = 'sc_workspace_v0_1';
  const MAX_RECENT = 5;

  function nowIso() { return new Date().toISOString(); }
  function readState() {
    try {
      const raw = window.localStorage.getItem(KEY);
      if (!raw) return { schema: 1, activeSession: null, recentTools: [] };
      const parsed = JSON.parse(raw);
      return {
        schema: 1,
        activeSession: parsed && parsed.activeSession ? parsed.activeSession : null,
        recentTools: Array.isArray(parsed && parsed.recentTools) ? parsed.recentTools.slice(0, MAX_RECENT) : []
      };
    } catch (_) {
      return { schema: 1, activeSession: null, recentTools: [] };
    }
  }
  function writeState(state) {
    try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) {}
  }
  function newSession() {
    const stamp = nowIso();
    return { id: `ws-${Date.now().toString(36)}`, title: 'Workspace session', createdAt: stamp, updatedAt: stamp };
  }
  function formatTime(iso) {
    if (!iso) return 'Browser-local state is ready.';
    try { return `Updated ${new Intl.DateTimeFormat(undefined,{dateStyle:'medium',timeStyle:'short'}).format(new Date(iso))}`; }
    catch (_) { return 'Session active in this browser.'; }
  }
  function toolLabel(link) {
    const strong = link.querySelector('strong');
    return strong ? strong.textContent.trim() : link.dataset.scwTool;
  }
  function init(root) {
    if (root.dataset.scwReady === '1') return;
    root.dataset.scwReady = '1';
    let state = readState();
    const name = root.querySelector('[data-scw-session-name]');
    const time = root.querySelector('[data-scw-session-time]');
    const start = root.querySelector('[data-scw-start]');
    const clear = root.querySelector('[data-scw-clear]');
    const recentWrap = root.querySelector('[data-scw-recent-wrap]');
    const recent = root.querySelector('[data-scw-recent]');

    function render() {
      if (state.activeSession) {
        name.textContent = state.activeSession.title || 'Workspace session';
        time.textContent = formatTime(state.activeSession.updatedAt);
        start.textContent = 'Continue workspace';
        clear.hidden = false;
      } else {
        name.textContent = 'No active session';
        time.textContent = 'Browser-local state is ready.';
        start.textContent = 'Start workspace';
        clear.hidden = true;
      }
      recent.innerHTML = '';
      if (state.recentTools.length) {
        state.recentTools.forEach((item) => {
          const chip = document.createElement('span');
          chip.textContent = item.label;
          recent.appendChild(chip);
        });
        recentWrap.hidden = false;
      } else {
        recentWrap.hidden = true;
      }
    }

    start.addEventListener('click', () => {
      if (!state.activeSession) state.activeSession = newSession();
      state.activeSession.updatedAt = nowIso();
      writeState(state);
      render();
    });
    clear.addEventListener('click', () => {
      state.activeSession = null;
      writeState(state);
      render();
    });
    root.querySelectorAll('[data-scw-tool]').forEach((link) => {
      link.addEventListener('click', () => {
        if (!state.activeSession) state.activeSession = newSession();
        state.activeSession.updatedAt = nowIso();
        const key = link.dataset.scwTool;
        state.recentTools = [{ key, label: toolLabel(link), openedAt: nowIso() }, ...state.recentTools.filter((item) => item.key !== key)].slice(0, MAX_RECENT);
        writeState(state);
      });
    });
    render();
  }
  function boot() { document.querySelectorAll('[data-sc-workspace]').forEach(init); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
