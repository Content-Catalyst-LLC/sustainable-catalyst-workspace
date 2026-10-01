(function (root) {
  'use strict';

  const VERSION = '3.48.0';

  function text(node, value) {
    if (node) node.textContent = String(value == null ? '' : value);
  }

  function formatTime(value) {
    if (!value) return 'Not yet';
    try { return new Date(value).toLocaleString(); } catch (_) { return String(value); }
  }

  async function boot(runtime) {
    const app = document.querySelector('[data-sc-workspace-standalone]');
    if (!app) throw new Error('Standalone Workspace root is missing');

    const projectList = app.querySelector('[data-scws-project-list]');
    const empty = app.querySelector('[data-scws-empty]');
    const createForm = app.querySelector('[data-scws-create-form]');
    const detail = app.querySelector('[data-scws-project-detail]');
    const detailTitle = app.querySelector('[data-scws-detail-title]');
    const detailDescription = app.querySelector('[data-scws-detail-description]');
    const detailId = app.querySelector('[data-scws-detail-id]');
    const detailUpdated = app.querySelector('[data-scws-detail-updated]');
    const deleteButton = app.querySelector('[data-scws-delete]');
    const diagnostics = app.querySelector('[data-scws-diagnostics]');
    const backendStatus = app.querySelector('[data-scws-backend-status]');

    function activeProject() {
      const state = runtime.stateStore.current();
      return state.projects.find((project) => (
        project && String(project.id || '') === String(state.activeProjectId || '')
      )) || null;
    }

    function projectCard(project) {
      const row = document.createElement('article');
      row.className = 'scws-project-card';

      const body = document.createElement('div');
      const title = document.createElement('strong');
      title.textContent = project.title || 'Untitled project';
      const description = document.createElement('p');
      description.textContent = project.description || 'No description yet.';
      const meta = document.createElement('span');
      meta.textContent = 'Updated ' + formatTime(project.updatedAt || project.createdAt);
      body.append(title, description, meta);

      const open = document.createElement('button');
      open.type = 'button';
      open.textContent = 'Open';
      open.addEventListener('click', async () => {
        await runtime.kernel.openProject(project.id, { restoreArchived: true });
        await render();
      });

      row.append(body, open);
      return row;
    }

    async function render() {
      const projects = await runtime.kernel.listProjects();
      projectList.innerHTML = '';
      projects
        .filter((project) => project && !project.archivedAt)
        .sort((a, b) => String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')))
        .forEach((project) => projectList.appendChild(projectCard(project)));

      empty.hidden = projects.some((project) => project && !project.archivedAt);

      const project = activeProject();
      detail.hidden = !project;
      if (project) {
        text(detailTitle, project.title || 'Untitled project');
        text(detailDescription, project.description || 'No description yet.');
        text(detailId, project.id || '');
        text(detailUpdated, formatTime(project.updatedAt || project.createdAt));
      }

      text(diagnostics, JSON.stringify(runtime.inspect(), null, 2));
    }

    app.querySelector('[data-scws-new-project]').addEventListener('click', () => {
      createForm.hidden = false;
      const input = createForm.querySelector('input[name="title"]');
      if (input) input.focus();
    });

    app.querySelector('[data-scws-cancel-create]').addEventListener('click', () => {
      createForm.reset();
      createForm.hidden = true;
    });

    createForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = new FormData(createForm);
      const project = await runtime.kernel.createProject({
        title: data.get('title'),
        description: data.get('description')
      });
      if (project) {
        createForm.reset();
        createForm.hidden = true;
      }
      await render();
    });

    deleteButton.addEventListener('click', async () => {
      const project = activeProject();
      if (!project) return;
      await runtime.kernel.deleteProject(project.id, { confirm: true });
      await render();
    });

    app.querySelector('[data-scws-check-backend]').addEventListener('click', async () => {
      text(backendStatus, 'Checking…');
      try {
        const result = await runtime.health();
        const version = result && result.version ? result.version : 'unknown';
        text(backendStatus, 'Online · backend ' + version);
        backendStatus.dataset.state = 'ready';
      } catch (error) {
        text(backendStatus, 'Unavailable · ' + String(error && error.message || error));
        backendStatus.dataset.state = 'error';
      }
    });

    await render();
  }

  root.SCWorkspaceStandaloneShell = Object.freeze({
    schema: 'sc-workspace-standalone-shell/1.0',
    version: VERSION,
    boot
  });
})(typeof globalThis !== 'undefined' ? globalThis : this);
