/* WS-UX-01 — project-centered Workspace navigation candidate.
 * Reuses the actual live DOM panels and existing project runtime. No new
 * publishing, identity or storage authority; no contact with private Research.
 */
(function (root, factory) {
  'use strict';
  const api = factory(root);
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceProjectDesk = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
  'use strict';

  const VERSION = 'ws-ux-01/0.1';
  const TAB_PANELS = Object.freeze({
    overview: [],
    sources: ['library-bridge', 'evidence'],
    analysis: ['integrated-project', 'datasets', 'models-runtimes', 'visual-analysis'],
    outputs: [],
    history: ['session-timeline', 'research-map'],
    tools: ['launcher', 'objects', 'diagnostics'],
    projects: ['projects']
  });
  const TABS = Object.freeze([
    ['overview', 'Overview'], ['sources', 'Sources & evidence'],
    ['analysis', 'Analysis & figures'], ['outputs', 'Research outputs'],
    ['history', 'History'], ['tools', 'Advanced tools'], ['projects', 'Projects']
  ]);
  const OUTPUT_NOTICE = 'Research outputs are not yet linked to this Workspace project. ' +
    'Private Research editing and publishing remain unavailable until the Workspace–Research identity bridge passes live acceptance. ' +
    'No output has been published or imported by this screen.';

  function model(state) {
    const value = state && typeof state === 'object' ? state : {};
    const projects = Array.isArray(value.projects)
      ? value.projects.filter(p => p && !p.archivedAt && typeof p.id === 'string')
      : [];
    const active = projects.find(p => p.id === value.activeProjectId) || null;
    return Object.freeze({
      projects: projects.map(p => ({ id: p.id, title: String(p.title || 'Untitled project') })),
      activeProjectId: active ? active.id : null,
      activeTitle: active ? String(active.title || 'Untitled project') : 'Choose or create a project',
      description: active ? String(active.description || '') : '',
      outputStatus: 'not-connected',
      outputCount: null
    });
  }

  function mount(runtime, doc) {
    const document = doc || (typeof window !== 'undefined' ? window.document : null);
    const app = document && document.querySelector('[data-sc-workspace-standalone]');
    const main = app && app.querySelector('.main');
    if (!main || !runtime || !runtime.stateStore || !runtime.kernel) return null;
    if (main.querySelector('[data-ws-project-desk]')) return null;

    const desk = document.createElement('section');
    desk.className = 'panel ws-project-desk';
    desk.id = 'project-desk';
    desk.setAttribute('data-ws-project-desk', VERSION);
    desk.innerHTML = [
      '<header class="ws-desk-heading"><div>',
      '<p class="ws-desk-kicker">Workspace / active research project</p>',
      '<h2 data-ws-desk-title>Choose or create a project</h2>',
      '<p data-ws-desk-description>Your research, sources and outputs in one project.</p>',
      '</div><div class="ws-desk-picker"><label for="ws-desk-project">Project</label>',
      '<select id="ws-desk-project" data-ws-desk-select></select>',
      '<button type="button" class="btn" data-ws-desk-new>New project</button></div></header>',
      '<nav class="ws-desk-tabs" aria-label="Project sections" data-ws-desk-tabs></nav>',
      '<div class="ws-desk-view" data-ws-desk-view></div>'
    ].join('');
    main.insertBefore(desk, main.firstElementChild);

    const view = desk.querySelector('[data-ws-desk-view]');
    const tabs = desk.querySelector('[data-ws-desk-tabs]');
    const select = desk.querySelector('[data-ws-desk-select]');
    const anchors = new Map();
    const groups = new Map();

    // Place existing, working Workspace panels inside tab groups. Their event
    // listeners and original API clients survive the move.
    Object.keys(TAB_PANELS).forEach(key => {
      const group = document.createElement('div');
      group.className = 'ws-desk-group';
      group.dataset.wsDeskGroup = key;
      group.hidden = key !== 'overview';
      groups.set(key, group);
      TAB_PANELS[key].forEach(id => {
        const section = document.getElementById(id);
        if (!section) return;
        const placeholder = document.createComment('Original Workspace panel: ' + id);
        section.parentNode.insertBefore(placeholder, section);
        anchors.set(id, placeholder);
        group.appendChild(section);
        section.classList.add('ws-desk-existing-panel');
      });
      view.appendChild(group);
    });

    const intro = document.createElement('div');
    intro.className = 'ws-desk-intro';
    intro.innerHTML = '<h3>Your project, not six separate applications</h3>' +
      '<p>Save evidence in Library, study it with the analysis tools, and organize research outputs ' +
      'in this Workspace. Research remains the authority for scientific releases; no private data are published here.</p>' +
      '<div class="ws-desk-steps"></div>';
    const shortcuts = intro.querySelector('.ws-desk-steps');
    [['sources', '1. Collect sources'], ['analysis', '2. Analyze'], ['outputs', '3. Prepare outputs']].forEach(([id, label]) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'ws-desk-step'; b.textContent = label;
      b.addEventListener('click', () => showTab(id));
      shortcuts.appendChild(b);
    });
    groups.get('overview').appendChild(intro);

    const outputBox = document.createElement('div');
    outputBox.className = 'ws-desk-output-status';
    outputBox.innerHTML = '<h3>Research outputs & publishing</h3>' +
      '<p data-ws-desk-output-message></p>' +
      '<p><strong>Next capability:</strong> view each Research output, draft revision, review state, approved release, and public visibility here without leaving Workspace.</p>';
    outputBox.querySelector('[data-ws-desk-output-message]').textContent = OUTPUT_NOTICE;
    groups.get('outputs').appendChild(outputBox);

    let currentTab = 'overview';
    function showTab(name) {
      if (!groups.has(name)) return;
      currentTab = name;
      groups.forEach((group, key) => { group.hidden = key !== name; });
      [...tabs.querySelectorAll('button')].forEach(button => {
        const chosen = button.dataset.wsDeskTab === name;
        button.setAttribute('aria-selected', chosen ? 'true' : 'false');
        button.tabIndex = chosen ? 0 : -1;
      });
      desk.dataset.activeTab = name;
    }
    TABS.forEach(([key, label]) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'ws-desk-tab';
      button.dataset.wsDeskTab = key;
      button.setAttribute('role', 'tab');
      button.setAttribute('aria-selected', key === 'overview' ? 'true' : 'false');
      button.textContent = label;
      button.addEventListener('click', () => showTab(key));
      tabs.appendChild(button);
    });
    tabs.setAttribute('role', 'tablist');

    function refresh() {
      const m = model(runtime.stateStore.current());
      desk.querySelector('[data-ws-desk-title]').textContent = m.activeTitle;
      desk.querySelector('[data-ws-desk-description]').textContent =
        m.description || (m.activeProjectId
          ? 'Sources, analysis, research outputs, and project reviews together.'
          : 'Select a project or create a new one to begin.');
      const prior = select.value;
      select.replaceChildren();
      const prompt = document.createElement('option');
      prompt.value = ''; prompt.textContent = 'Select a project'; select.appendChild(prompt);
      m.projects.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id; option.textContent = p.title; select.appendChild(option);
      });
      select.value = m.activeProjectId || '';
      if (prior !== select.value) desk.dataset.projectChanged = 'true';
    }

    select.addEventListener('change', async () => {
      const id = select.value;
      if (!id) return refresh();
      // Use the EXISTING project-list click handler, which reloads every
      // connected Workspace section. Do not make a parallel state authority.
      const available = model(runtime.stateStore.current()).projects;
      const index = available.findIndex(p => p.id === id);
      const buttons = app.querySelectorAll('[data-project-list] > button.project');
      if (index >= 0 && buttons[index] && typeof buttons[index].click === 'function') {
        buttons[index].click();
      } else {
        // If UI is not yet ready, don't silently change the project.
        desk.querySelector('[data-ws-desk-description]').textContent =
          'Project selection is initializing. Choose it from the Projects tab.';
        showTab('projects');
      }
    });
    desk.querySelector('[data-ws-desk-new]').addEventListener('click', () => {
      showTab('projects');
      const form = app.querySelector('[data-create-form]');
      if (form) {
        form.hidden = false;
        const field = form.querySelector('input[name="title"]');
        if (field && typeof field.focus === 'function') field.focus();
      }
    });

    // Existing sidebar destination buttons still work: reveal their now-tabbed
    // panel before the original click's scrollIntoView fires.
    const panelToTab = {};
    Object.entries(TAB_PANELS).forEach(([key, ids]) => {
      ids.forEach(id => { panelToTab[id] = key; });
    });
    const side = app.querySelector('.side');
    if (side) side.addEventListener('click', e => {
      const button = e.target.closest('button[onclick]');
      if (!button) return;
      const call = button.getAttribute('onclick') || '';
      const found = call.match(/querySelector\('#([^']+)'\)/);
      if (found && panelToTab[found[1]]) showTab(panelToTab[found[1]]);
    }, true);
    const hash = root.location && String(root.location.hash || '').replace(/^#/, '');
    if (panelToTab[hash]) showTab(panelToTab[hash]);

    // Live shell updates this chip on project selection and creation.
    const activeChip = document.querySelector('[data-active]');
    const observer = typeof root.MutationObserver === 'function' && activeChip
      ? new root.MutationObserver(refresh) : null;
    if (observer) observer.observe(activeChip, { childList: true, characterData: true, subtree: true });
    refresh();
    showTab(currentTab);
    return Object.freeze({ version: VERSION, refresh, showTab, destroy() {
      if (observer) observer.disconnect();
      anchors.forEach((placeholder, id) => {
        const section = document.getElementById(id);
        if (section && placeholder.parentNode) placeholder.parentNode.insertBefore(section, placeholder);
        placeholder.remove();
      });
      desk.remove();
    } });
  }

  function start() {
    const rt = window.SCWorkspaceStandaloneRuntime;
    if (rt) mount(rt, window.document);
  }
  if (typeof window !== 'undefined' && window.document) {
    window.document.addEventListener('sc-workspace-standalone:ready', start);
    if (window.SCWorkspaceStandaloneRuntime) start();
  }

  return Object.freeze({ version: VERSION, tabs: TABS, model, mount, outputNotice: OUTPUT_NOTICE });
});
