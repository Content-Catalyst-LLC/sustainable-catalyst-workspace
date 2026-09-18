(() => {
  'use strict';
  const VERSION = '2.28.1';
  const runtime = window.SCWorkspaceInteractionRuntime = window.SCWorkspaceInteractionRuntime || {
    schema: 'sc-workspace-interaction-runtime/1.0', version: VERSION, ready: false,
    roots: 0, initializedRoots: 0, issues: [], unhandledErrors: [], lastReadyAt: null
  };
  runtime.version = VERSION;
  runtime.bootstrapReady = true;

  function rootFor(target) {
    return target && target.closest ? target.closest('[data-sc-workspace]') : null;
  }
  function setView(root, view) {
    if (!root) return;
    const requested = String(view || 'start');
    const sections = [...root.querySelectorAll('[data-scw-workspace-section]')];
    const hasTarget = sections.some((section) => section.dataset.scwWorkspaceSection === requested);
    const resolved = hasTarget ? requested : 'start';
    sections.forEach((section) => { section.hidden = section.dataset.scwWorkspaceSection !== resolved; });
    root.querySelectorAll('[data-scw-workspace-view]').forEach((button) => {
      const selected = button.dataset.scwWorkspaceView === resolved;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      if (selected) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current');
    });
    root.dataset.scwBootstrapView = resolved;
  }
  function setProjectMode(root, mode) {
    if (!root) return;
    const allowed = new Set(['overview','guide','research','analysis','decision','canvas','traceability','assist','briefing','objects']);
    const resolved = allowed.has(mode) ? mode : 'overview';
    root.querySelectorAll('[data-scw-project-mode]').forEach((button) => {
      const selected = button.dataset.scwProjectMode === resolved;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
    root.querySelectorAll('[data-scw-project-panel]').forEach((panel) => { panel.hidden = panel.dataset.scwProjectPanel !== resolved; });
    root.dataset.scwBootstrapProjectMode = resolved;
  }
  function revealForm(root, selector, focusSelector) {
    const form = root && root.querySelector(selector);
    if (!form) return false;
    form.hidden = false;
    const focus = form.querySelector(focusSelector);
    if (focus && typeof focus.focus === 'function') focus.focus();
    return true;
  }

  document.addEventListener('click', (event) => {
    const target = event.target instanceof Element ? event.target.closest('button, a') : null;
    if (!target || target.disabled || target.dataset.scwBound === '1') return;
    let root = rootFor(target);
    if (!root && target.matches('[data-scw-platform-new-project]')) root = document.querySelector('[data-sc-workspace]');
    if (!root) return;

    if (target.matches('[data-scw-workspace-view]')) {
      event.preventDefault(); setView(root, target.dataset.scwWorkspaceView); return;
    }
    if (target.matches('[data-scw-project-mode]')) {
      event.preventDefault(); setView(root, 'projects'); setProjectMode(root, target.dataset.scwProjectMode); return;
    }
    if (target.matches('[data-scw-new-project], [data-scw-platform-new-project]')) {
      event.preventDefault(); revealForm(root, '[data-scw-create-form]', 'input[name="title"]'); return;
    }
    if (target.matches('[data-scw-cancel-create]')) {
      event.preventDefault(); const form=root.querySelector('[data-scw-create-form]'); if(form){form.reset();form.hidden=true;} return;
    }
    if (target.matches('[data-scw-import-project]')) {
      event.preventDefault(); const input=root.querySelector('[data-scw-import-file]'); if(input && typeof input.click==='function') input.click(); return;
    }
    if (target.matches('[data-scw-new-object]')) {
      event.preventDefault(); revealForm(root, '[data-scw-object-create-form]', 'input[name="title"]'); return;
    }
    if (target.matches('[data-scw-cancel-object]')) {
      event.preventDefault(); const form=root.querySelector('[data-scw-object-create-form]'); if(form){form.reset();form.hidden=true;}
    }
  }, true);

  document.querySelectorAll('[data-sc-workspace]').forEach((root) => {
    root.dataset.scwInteractionBootstrap = VERSION;
    if (!root.dataset.scwBootstrapView) setView(root, 'start');
  });
})();
