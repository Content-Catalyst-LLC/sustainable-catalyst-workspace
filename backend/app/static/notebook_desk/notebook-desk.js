// SC-SCI-01 Research notebook workspace. Same-origin over the authenticated Workspace APIs; the SC Identity
// session cookie is the only credential. Every state shown (revision, run, verification, currency) comes from
// the API. The pure helpers live in notebook-recipes.js and are tested there.

import {
  AGREEMENT_TEXT, RECIPES, STATE_TEXT, agreement, columns, csvRecords, dependents, describeEvidence, downstream,
  markdownCell, newNotebook, nextCellId, recordsBytes, slug,
} from "./notebook-recipes.js";

const DESK = "/v1/desk/notebooks";
const POLL_MS = 1500;
const POLL_LIMIT = 400;  // ten minutes

const state = { me: null, projects: [], projectId: "", notebooks: [], datasets: [], nb: null, saved: null,
                status: null, dirty: false, polling: false, idp: null };

// --- API -------------------------------------------------------------------------------------------------

async function api(method, path, body) {
  const init = { method, credentials: "same-origin", headers: { Accept: "application/json" } };
  if (body !== undefined) { init.headers["Content-Type"] = "application/json"; init.body = JSON.stringify(body); }
  const res = await fetch(path, init);
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  if (res.status === 401) { showSignIn(); throw new Error("Your session ended. Sign in again."); }
  if (!res.ok) throw new Error(problem(data) || `Request failed (HTTP ${res.status}).`);
  return data;
}

function problem(body) {
  if (!body || typeof body !== "object") return "";
  const d = body.detail && typeof body.detail === "object" ? body.detail : body;
  const msg = typeof d.message === "string" ? d.message : typeof body.detail === "string" ? body.detail : "";
  const code = typeof d.code === "string" ? d.code : "";
  return [msg, code && `(${code})`].filter(Boolean).join(" ");
}

function b64(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(s);
}

function rid(prefix) {
  const r = crypto.getRandomValues(new Uint8Array(6));
  return `${prefix}-${[...r].map(x => x.toString(16).padStart(2, "0")).join("")}`;
}

// --- DOM helpers ---------------------------------------------------------------------------------------

const el = (id) => document.getElementById(id);
function h(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") n.className = v; else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : String(v));
  }
  for (const k of kids.flat()) if (k != null && k !== false) n.append(k instanceof Node ? k : String(k));
  return n;
}
function notice(text, kind = "ok") {
  const n = el("notice"); n.hidden = !text; n.textContent = text || ""; n.dataset.kind = kind;
}
const fmt = (x) => typeof x === "number" ? (Math.abs(x) >= 1e5 || (x !== 0 && Math.abs(x) < 1e-3) ? x.toExponential(6) : x.toPrecision(8).replace(/\.?0+$/, "")) : String(x);
const short = (sha) => sha ? String(sha).slice(0, 12) : "";
function options(select, items, value, empty) {
  select.replaceChildren(...(empty ? [h("option", { value: "" }, empty)] : []),
    ...items.map(([v, label]) => h("option", { value: v, selected: v === value }, label)));
}
async function busy(button, fn) {
  const was = button.disabled; button.disabled = true;
  try { return await fn(); } catch (e) { notice(e.message, "error"); return null; } finally { button.disabled = was; }
}

// --- session -------------------------------------------------------------------------------------------

// Without SC Identity (production today) the existing ERW account sign-in issues the Workspace session.
async function identityProvider() {
  if (state.idp) return state.idp;
  const res = await fetch("/v1/session/profile", { credentials: "same-origin", headers: { Accept: "application/json" } }).catch(() => null);
  const profile = res && res.ok ? await res.json().catch(() => null) : null;
  state.idp = profile && profile.globalIdentityProviderConfigured ? "sc-identity" : "erw";
  return state.idp;
}

async function showSignIn() {
  el("signin").hidden = false; el("app").hidden = true; el("signout").hidden = true; el("who").textContent = "";
  const login = (await identityProvider()) === "sc-identity" ? "/v1/auth/login" : "/v1/private-research/login";
  el("signin-link").href = `${login}?returnTo=${encodeURIComponent(DESK + location.search)}`;
}

async function boot() {
  const res = await fetch("/v1/session", { credentials: "same-origin", headers: { Accept: "application/json" } });
  const me = res.ok ? await res.json() : null;
  if (!me || !me.authenticated) return showSignIn();
  state.me = me;
  el("who").textContent = `Signed in as ${me.displayName || me.subject}`;
  el("signout").hidden = false; el("signin").hidden = true; el("app").hidden = false;
  await loadProjects(new URLSearchParams(location.search).get("project") || "");
  const nb = new URLSearchParams(location.search).get("notebook");
  if (nb) await openNotebook(nb);
}

// --- projects, notebooks, datasets ----------------------------------------------------------------------

async function loadProjects(prefer) {
  const data = await api("GET", "/v1/projects");
  state.projects = (data.items || []).map(p => ({ id: p.projectId, title: p.title || p.projectId }));
  state.projectId = state.projects.some(p => p.id === prefer) ? prefer : (state.projects[0] || {}).id || "";
  options(el("project"), state.projects.map(p => [p.id, p.title]), state.projectId, state.projects.length ? null : "No projects yet");
  await loadProject();
}

async function loadProject() {
  const pid = state.projectId;
  const [nbs, dss] = pid ? await Promise.all([api("GET", "/v1/notebooks"),
    api("GET", `/v1/datasets?projectId=${encodeURIComponent(pid)}`)]) : [{ items: [] }, { items: [] }];
  state.notebooks = (nbs.items || []).filter(n => n.projectId === pid);
  state.datasets = (dss.items || []).filter(d => d.projectId === pid);
  renderNotebookList(); renderDatasets(); renderCellForm();
}

function renderNotebookList() {
  const ul = el("notebooks");
  ul.replaceChildren(...state.notebooks.map(n => h("li", {},
    h("button", { type: "button", class: "link", onclick: () => openNotebook(n.notebookId) }, n.title || n.notebookId),
    h("span", { class: "muted" }, ` r${n.revision}`))));
  el("notebooks-empty").hidden = state.notebooks.length > 0;
}

function datasetClass(d) { return ((d.metadata || {}).scientificClassification) || "unclassified"; }

function renderDatasets() {
  const ul = el("datasets");
  ul.replaceChildren(...state.datasets.map(d => h("li", {},
    h("strong", {}, d.name), " ",
    h("span", { class: `badge ${datasetClass(d)}` }, datasetClass(d)), h("br"),
    d.artifactSha256 ? h("code", { title: d.artifactSha256 }, `r${d.revision} · sha256 ${short(d.artifactSha256)}…`)
                     : h("span", { class: "muted" }, "no pinned bytes"))));
  el("datasets-empty").hidden = state.datasets.length > 0;
}

async function createProject(ev) {
  ev.preventDefault();
  const title = el("project-title").value.trim();
  const id = `${slug(title, "project").slice(0, 40)}-${rid("p").slice(2)}`;
  await busy(ev.submitter || ev.target, async () => {
    await api("POST", "/v1/projects", { schema: "sc-workspace-cloud-backup/1.0", sourceProjectId: id, projectTitle: title,
      project: { schema: "sc-workspace-project/20.0", id, title, objects: [] } });
    el("project-title").value = ""; ev.target.closest("details").open = false;
    await loadProjects(id); notice(`Project “${title}” created.`);
  });
}

async function storeDataset(ev) {
  ev.preventDefault();
  if (!state.projectId) return notice("Create or choose a project first.", "error");
  const file = el("dataset-file").files[0], name = el("dataset-name").value.trim(), cls = el("dataset-class").value;
  if (!file || !cls) return notice("Choose a file and say what kind of data it is.", "error");
  await busy(ev.submitter || ev.target, async () => {
    const text = await file.text();
    const records = /\.json$/i.test(file.name) || file.type === "application/json"
      ? (j => Array.isArray(j) ? j : j && Array.isArray(j.rows) ? j.rows : null)(JSON.parse(text)) : csvRecords(text);
    const bytes = recordsBytes(records);
    const datasetId = `${slug(name, "dataset").slice(0, 40)}-${rid("d").slice(2)}`;
    const artifactId = `${datasetId}-bytes`;
    await api("POST", "/v1/artifacts", { schema: "sc-workspace-artifact-store/1.0", artifactId, projectId: state.projectId,
      filename: `${slug(name)}.json`, mediaType: "application/json", contentBase64: b64(bytes),
      metadata: { classification: cls, sourceFilename: file.name.slice(0, 200) } });
    const cols = columns(records);
    await api("POST", "/v1/datasets", { schema: "sc-workspace-dataset-record/1.0", datasetId, projectId: state.projectId,
      name, datasetType: "table", sourceKind: "artifact", artifactId,
      schemaDefinition: { columns: cols.map(c => ({ name: c.name, type: c.numeric ? "number" : "string" })) },
      metadata: { scientificClassification: cls, rows: records.length } });
    ev.target.reset(); ev.target.closest("details").open = false;
    await loadProject(); notice(`Dataset “${name}” stored: ${records.length} rows, bytes pinned by SHA-256.`);
  });
}

// --- notebook ----------------------------------------------------------------------------------------------

async function createNotebook(ev) {
  ev.preventDefault();
  if (!state.projectId) return notice("Create or choose a project first.", "error");
  const title = el("notebook-title").value.trim();
  state.nb = newNotebook(`nb-${slug(title, "notebook").slice(0, 40)}-${rid("n").slice(2)}`, title);
  state.saved = null; state.status = null; state.dirty = true;
  el("notebook-title").value = "";
  await save();
}

async function openNotebook(id) {
  const data = await api("GET", `/v1/notebooks/${encodeURIComponent(id)}`);
  const pkg = data.package || {};
  if (data.item && data.item.projectId && data.item.projectId !== state.projectId) {
    state.projectId = data.item.projectId; el("project").value = state.projectId; await loadProject();
  }
  state.nb = JSON.parse(JSON.stringify(pkg.notebook || {}));
  state.nb.cells = Array.isArray(state.nb.cells) ? state.nb.cells : [];
  state.saved = data.item; state.dirty = false;
  history.replaceState(null, "", `${DESK}?project=${encodeURIComponent(state.projectId)}&notebook=${encodeURIComponent(id)}`);
  await refreshStatus();
}

async function save() {
  const nb = state.nb;
  if (!nb) return null;
  const expected = state.saved ? state.saved.revision : 0;
  const data = await api("POST", "/v1/notebooks", { schema: "sc-workspace-notebook-sync-push/1.0",
    sourceNotebookId: nb.id, sourceProjectId: state.projectId, notebookTitle: nb.title, expectedRevision: expected,
    operationId: `${nb.id}-r${expected + 1}-${rid("o").slice(2)}`, clientUpdatedAt: new Date().toISOString(), notebook: nb });
  state.saved = data.item; state.dirty = false;
  const listed = state.notebooks.find(n => n.notebookId === nb.id);
  if (!listed) await loadProject(); else { Object.assign(listed, state.saved); renderNotebookList(); }
  history.replaceState(null, "", `${DESK}?project=${encodeURIComponent(state.projectId)}&notebook=${encodeURIComponent(nb.id)}`);
  await refreshStatus();
  notice(`Saved revision ${state.saved.revision}.`);
  return state.saved;
}

async function refreshStatus() {
  if (state.saved) {
    state.status = await api("GET", `/v1/notebooks/${encodeURIComponent(state.nb.id)}/cell-status`);
  }
  render();
}

async function runAll(button) {
  await busy(button, async () => {
    if (!state.nb.cells.some(c => c.type !== "markdown")) throw new Error("Add an R or Julia cell first.");
    if (state.dirty || !state.saved) await save();
    const plan = await api("POST", "/v1/notebook-execution-plans", { schema: "sc-workspace-notebook-execution-plan-request/1.0",
      notebookId: state.nb.id });
    const planId = plan.item.planId;
    await api("POST", `/v1/notebook-execution-plans/${encodeURIComponent(planId)}/dispatch`, {
      schema: "sc-workspace-notebook-execution-dispatch-request/1.0", idempotencyKey: `${planId}-dispatch` });
    notice(`Running revision ${plan.item.notebookRevision ?? state.saved.revision}…`);
    state.polling = true;
    for (let i = 0; i < POLL_LIMIT && state.polling; i++) {
      await new Promise(r => setTimeout(r, POLL_MS));
      const p = (await api("GET", `/v1/notebook-execution-plans/${encodeURIComponent(planId)}`)).item;
      await refreshStatus();
      if (["succeeded", "failed", "blocked", "cancelled"].includes(p.status)) {
        notice(p.status === "succeeded" ? "All cells ran. Check each cell's verification below."
                                        : `The run stopped: ${p.status}. See the cells below.`, p.status === "succeeded" ? "ok" : "error");
        break;
      }
    }
    state.polling = false;
  });
}

// --- cells ----------------------------------------------------------------------------------------------

function statusFor(id) { return ((state.status && state.status.cells) || []).find(c => c.cellId === id) || null; }

function render() {
  const nb = state.nb;
  el("editor").hidden = !nb;
  if (!nb) return;
  el("nb-title").textContent = nb.title;
  el("nb-rev").textContent = state.saved ? `revision ${state.saved.revision} · ${short(state.saved.notebookFingerprint || state.saved.fingerprint)}` : "not saved";
  el("nb-dirty").hidden = !state.dirty;
  for (const [id, f] of [["export-ipynb", "ipynb"], ["export-qmd", "qmd"], ["export-package", "package"]]) {
    const a = el(id);
    if (state.saved) { a.href = `/v1/notebooks/${encodeURIComponent(nb.id)}/revisions/${state.saved.revision}/export?format=${f}`; a.removeAttribute("aria-disabled"); }
    else { a.removeAttribute("href"); a.setAttribute("aria-disabled", "true"); }
  }
  el("cells").replaceChildren(...nb.cells.map((c, i) => renderCell(c, i)));
  el("cells-empty").hidden = nb.cells.length > 0;
  const code = nb.cells.filter(c => c.type !== "markdown").map(c => [c.id, `${c.id} · ${c.title || c.language || c.type}`]);
  const ids = code.map(([id]) => id);
  const a = ids.includes(el("cmp-a").value) ? el("cmp-a").value : ids[0];
  const b = ids.includes(el("cmp-b").value) && el("cmp-b").value !== a ? el("cmp-b").value : ids.find(id => id !== a);
  options(el("cmp-a"), code, a);
  options(el("cmp-b"), code, b);
  renderCellForm();
}

function renderCell(cell, index) {
  if (cell.type === "markdown") {
    return h("li", { class: "cell md" }, h("div", { class: "cell-head" }, h("span", { class: "badge" }, "Text"),
      h("span", { class: "grow" }), cellButtons(cell, index)), h("p", { class: "md-text" }, cell.source));
  }
  const st = statusFor(cell.id);
  const savedSha = st && st.cellSha256;
  // An unsaved edit makes the shown result describe an older cell; say so before the server can.
  const label = st ? st.state : "not-run";
  const ex = cell.execution || {};
  const deps = ex.dependsOnCellIds || [];
  const run = st && st.run;
  const kids = [
    h("div", { class: "cell-head" },
      h("span", { class: `badge lang` }, cell.language ? cell.language.toUpperCase() : "Decision"),
      h("strong", {}, cell.title || cell.id), h("code", { class: "muted" }, cell.id),
      h("span", { class: "grow" }),
      h("span", { class: `badge state-${label}` }, STATE_TEXT[label] || label),
      cellButtons(cell, index)),
    h("pre", { class: "src" }, cell.source || ""),
    h("p", { class: "fine" }, `Operation ${ex.operation}`, deps.length ? ` · after ${deps.join(", ")}` : "",
      ex.payload && ex.payload.datasetInput ? ` · dataset ${ex.payload.datasetInput.datasetId} r${ex.payload.datasetInput.datasetRevision} (sha256 ${short(ex.payload.datasetInput.artifactSha256)}…)` : "",
      ex.payload && ex.payload.upstreamInput ? ` · uses verified results of ${ex.payload.upstreamInput.cells.map(c => `${c.cellId} (${c.role})`).join(", ")}` : ""),
  ];
  if (state.dirty && savedSha) kids.push(h("p", { class: "fine warn-text" }, "Unsaved changes: results below describe the saved revision."));
  if (st && st.state === "stale" && st.currency) {
    const r = st.currency.reasons || [];
    kids.push(h("p", { class: "warn-text" }, "Stale: ",
      r.includes("cell-changed") ? "this cell changed since it ran. " : "",
      r.includes("upstream-changed") ? `upstream cell(s) ${(st.currency.changedUpstreamCells || []).join(", ")} changed. ` : "",
      "Run again to refresh."));
  }
  if (run) {
    const v = run.verification || {};
    if (run.errorMessage && label === "failed") kids.push(h("p", { class: "err-text" }, run.errorMessage));
    const rv = run.resultValues;
    if (rv && rv.values && Object.keys(rv.values).length) {
      const unc = (rv.uncertainty && rv.uncertainty.values) || {};
      kids.push(h("table", { class: "values" }, h("thead", {}, h("tr", {}, h("th", {}, "Value"), h("th", {}, "Estimate"), h("th", {}, "Std. error"))),
        h("tbody", {}, ...Object.entries(rv.values).map(([k, x]) => h("tr", {}, h("td", {}, k), h("td", {}, fmt(x)), h("td", {}, k in unc ? fmt(unc[k]) : "—"))))));
    } else if (rv && rv.error) kids.push(h("p", { class: "fine" }, `Values: ${rv.error}`));
    const notes = describeEvidence(st);
    kids.push(h("p", { class: "fine" }, `Run ${run.runId} · ${v.status || run.runStatus}`, notes.length ? ` · ${notes.join(" · ")}` : ""));
    if (label === "verified" && cell.language === "r") {
      kids.push(h("button", { type: "button", class: "secondary", onclick: () => openFigure(cell) }, "Make a figure from this result"));
    }
  }
  return h("li", { class: `cell state-${label}` }, ...kids);
}

function cellButtons(cell, index) {
  const nb = state.nb;
  const move = (d) => () => { const j = index + d; if (j < 0 || j >= nb.cells.length) return;
    [nb.cells[index], nb.cells[j]] = [nb.cells[j], nb.cells[index]]; touched(); };
  return h("span", { class: "cell-actions" },
    h("button", { type: "button", class: "link", "aria-label": "Move up", onclick: move(-1), disabled: index === 0 }, "↑"),
    h("button", { type: "button", class: "link", "aria-label": "Move down", onclick: move(1), disabled: index === nb.cells.length - 1 }, "↓"),
    h("button", { type: "button", class: "link", onclick: () => editCell(cell) }, "Edit"),
    h("button", { type: "button", class: "link", onclick: () => removeCell(cell) }, "Remove"));
}

function touched(message) {
  state.dirty = true;
  render();
  if (message) notice(message);
}

function removeCell(cell) {
  const deps = dependents(state.nb.cells, cell.id);
  if (deps.length) return notice(`Cells ${deps.join(", ")} depend on ${cell.id}. Remove or change them first.`, "error");
  state.nb.cells = state.nb.cells.filter(c => c.id !== cell.id);
  touched(`Removed ${cell.id}. Save to record the change.`);
}

// --- cell form --------------------------------------------------------------------------------------------

function recipeOf(cell) {
  if (cell.type === "markdown") return "markdown";
  const op = (cell.execution || {}).operation;
  return Object.keys(RECIPES).find(k => {
    const probe = { "r-linear-model": "workspace.polyglot.r.linear-model", "julia-least-squares": "workspace.polyglot.julia.quadratic-optimize",
                    "scenario-from-fit": "workspace.decision.minimax-regret" };
    return probe[k] === op;
  }) || "";
}

function renderCellForm() {
  const recipe = el("recipe");
  if (!recipe.options.length) {
    options(recipe, [["markdown", "Text"], ...Object.entries(RECIPES).map(([k, r]) => [k, r.title])], "r-linear-model");
  }
  const kind = recipe.value, r = RECIPES[kind];
  for (const n of document.querySelectorAll("#cell-form [data-for]")) {
    const f = n.dataset.for;
    n.hidden = !((f === "markdown" && kind === "markdown") || (f === "dataset" && r && r.needsDataset) ||
                 (f === "after" && kind === "julia-least-squares") || (f === "scenario" && kind === "scenario-from-fit") ||
                 (f === "source" && r && r.type === "code"));
  }
  const ds = state.datasets.filter(d => d.artifactSha256);
  const dsSel = el("cell-dataset"), prevDs = dsSel.value;
  options(dsSel, ds.map(d => [d.datasetId, `${d.name} (${datasetClass(d)}, r${d.revision})`]), prevDs || (ds[0] || {}).datasetId, ds.length ? null : "Add a dataset first");
  const chosen = ds.find(d => d.datasetId === dsSel.value);
  const cols = ((chosen && chosen.schemaDefinition && chosen.schemaDefinition.columns) || []).filter(c => c.type === "number").map(c => c.name);
  const outSel = el("cell-outcome"), prevOut = outSel.value;
  options(outSel, cols.map(c => [c, c]), cols.includes(prevOut) ? prevOut : cols[cols.length - 1]);
  const box = el("cell-predictors"), checked = new Set([...box.querySelectorAll("input:checked")].map(i => i.value));
  box.replaceChildren(...cols.filter(c => c !== outSel.value).map(c => h("label", { class: "check" },
    h("input", { type: "checkbox", value: c, checked: checked.size ? checked.has(c) : true }), ` ${c}`)));
  const code = ((state.nb && state.nb.cells) || []).filter(c => c.type === "code").map(c => [c.id, `${c.id} · ${c.title || c.language}`]);
  options(el("cell-after"), code, el("cell-after").value, "—");
  options(el("cell-primary"), code.filter(([id]) => (state.nb.cells.find(c => c.id === id) || {}).language === "r"), el("cell-primary").value);
  options(el("cell-cross"), code, el("cell-cross").value, "—");
  if (!el("cell-slope").value) el("cell-slope").value = [...box.querySelectorAll("input:checked")].map(i => i.value)[0] || "";
  const editing = el("cell-edit-id").value;
  el("cell-form-title").textContent = editing ? `Edit ${editing}` : "Add a cell";
  el("cell-submit").textContent = editing ? "Update cell" : "Add cell";
  el("cell-cancel").hidden = !editing;
}

function editCell(cell) {
  const kind = recipeOf(cell);
  if (!kind) return notice("This cell was created elsewhere; edit it there.", "error");
  el("recipe").value = kind; el("cell-edit-id").value = cell.id; el("cell-title").value = cell.title || "";
  const p = (cell.execution || {}).payload || {};
  if (kind === "markdown") el("cell-text").value = cell.source || "";
  if (p.datasetInput) { el("cell-dataset").value = p.datasetInput.datasetId; }
  renderCellForm();
  const fit = p.datasetInput && p.datasetInput.transform ? p.datasetInput.transform : p;
  if (fit.outcome) { el("cell-outcome").value = fit.outcome; renderCellForm(); }
  for (const i of el("cell-predictors").querySelectorAll("input")) i.checked = (fit.predictors || []).includes(i.value);
  if (kind === "julia-least-squares") el("cell-after").value = ((cell.execution || {}).dependsOnCellIds || [])[0] || "";
  if (kind === "scenario-from-fit") {
    const u = p.upstreamInput || {}, cells = u.cells || [];
    el("cell-primary").value = (cells.find(c => c.role === "primary") || {}).cellId || "";
    el("cell-cross").value = (cells.find(c => c.role === "cross-check") || {}).cellId || "";
    el("cell-slope").value = ((u.transform || {}).names || {}).slope || "";
    el("cell-rates").value = ((u.transform || {}).rates || []).join(", ");
  }
  if (RECIPES[kind] && RECIPES[kind].type === "code") el("cell-source").value = cell.source || "";
  el("cell-form").scrollIntoView({ behavior: "smooth", block: "center" });
}

function resetCellForm() {
  el("cell-edit-id").value = ""; el("cell-title").value = ""; el("cell-text").value = ""; el("cell-source").value = "";
  renderCellForm();
}

async function submitCell(ev) {
  ev.preventDefault();
  const nb = state.nb;
  if (!nb) return notice("Create or open a notebook first.", "error");
  const kind = el("recipe").value, editing = el("cell-edit-id").value;
  try {
    let cell, model = null;
    const id = editing || nextCellId(nb.cells, kind === "markdown" ? "text" : kind === "r-linear-model" ? "fit"
      : kind === "julia-least-squares" ? "check" : "scenario");
    if (kind === "markdown") cell = markdownCell(id, el("cell-text").value);
    else {
      const dataset = state.datasets.find(d => d.datasetId === el("cell-dataset").value);
      const predictors = [...el("cell-predictors").querySelectorAll("input:checked")].map(i => i.value);
      ({ cell, model } = RECIPES[kind].build({ projectId: state.projectId, cellId: id, dataset, outcome: el("cell-outcome").value,
        predictors, title: el("cell-title").value.trim(), after: el("cell-after").value, primary: el("cell-primary").value,
        crossCheck: el("cell-cross").value, slopeName: el("cell-slope").value.trim(), rates: el("cell-rates").value }));
      const notes = el("cell-source").value.trim();
      if (notes && cell.type === "code") cell.source = notes;
    }
    if (model) await ensureModel(model);
    if (editing) {
      const i = nb.cells.findIndex(c => c.id === editing);
      nb.cells[i] = cell;
      const affected = downstream(nb.cells, editing);
      touched(`Updated ${editing}.` + (affected.length ? ` Results of ${affected.join(", ")} will be stale until you run again.` : ""));
    } else {
      nb.cells.push(cell);
      touched(`Added ${id}. Save or run to record it.`);
    }
    resetCellForm();
  } catch (e) { notice(e.message, "error"); }
}

async function ensureModel(model) {
  const existing = await fetch(`/v1/models/${encodeURIComponent(model.modelId)}`, { credentials: "same-origin" });
  if (existing.ok) return;
  await api("POST", "/v1/models", model);
}

// --- compare --------------------------------------------------------------------------------------------

function compare() {
  const a = statusFor(el("cmp-a").value), b = statusFor(el("cmp-b").value);
  const out = el("cmp-out");
  if (!a || !b || a.cellId === b.cellId) { out.replaceChildren(h("p", { class: "fine" }, "Choose two different cells that have run.")); return; }
  const r = agreement(a, b);
  out.replaceChildren(
    h("p", { class: `badge cmp-${r.status}` }, AGREEMENT_TEXT[r.status]),
    r.independence ? h("p", { class: "fine" }, r.independence === "independent-implementation"
      ? `Independent implementation (${a.language} and ${b.language}).` : "Same implementation: a replay, which shows determinism, not reproduction.") : "",
    r.rows.length ? h("table", { class: "values" },
      h("thead", {}, h("tr", {}, h("th", {}, "Value"), h("th", {}, a.cellId), h("th", {}, b.cellId), h("th", {}, "|difference|"), h("th", {}, ""))),
      h("tbody", {}, ...r.rows.map(x => h("tr", {}, h("td", {}, x.name), h("td", {}, fmt(x.a)), h("td", {}, fmt(x.b)), h("td", {}, fmt(x.diff)), h("td", {}, x.within ? "within" : "outside"))))) : "",
    h("p", { class: "fine" }, `Tolerance: relative ${r.tolerance.relative}, absolute ${r.tolerance.absolute}.`));
}

// --- figure ---------------------------------------------------------------------------------------------

let figureCell = null;
function openFigure(cell) {
  figureCell = cell;
  el("fig-cell").textContent = cell.title || cell.id;
  const p = ((cell.execution || {}).payload) || {};
  el("fig-heading").value = `Fitted coefficients of ${p.outcome || "the model"} with 95% intervals`;
  const ds = state.datasets.find(d => d.datasetId === (p.datasetInput || {}).datasetId);
  const cls = ds ? datasetClass(ds) : "unclassified";
  el("fig-caption").value = `${cls === "synthetic" ? "SYNTHETIC data. " : ""}Coefficient estimates from ${cell.id} with ±1.96 standard errors.`;
  el("fig-alt").value = `Coefficient estimates for ${["intercept", ...(p.predictors || [])].join(", ")}, each with an interval bar.`;
  el("fig-limit").value = cls === "synthetic" ? "Synthetic data with no scientific meaning" : "Normal-approximation intervals; model assumptions are not tested";
  el("fig-out").replaceChildren();
  el("figure").hidden = false; el("figure").scrollIntoView({ behavior: "smooth" });
}

async function buildFigure(ev) {
  ev.preventDefault();
  const cell = figureCell, nb = state.nb, st = statusFor(cell.id);
  await busy(ev.submitter || ev.target, async () => {
    const rev = st && st.plan ? st.plan.notebookRevision : state.saved.revision;
    const body = {
      figureId: `${slug(nb.title).slice(0, 40)}-${cell.id}`.replace(/^-+/, "f-"), title: el("fig-heading").value.trim(),
      rowsPath: "coefficients", mark: "point",
      x: { field: "term", label: "Model term", unit: "category", type: "nominal" },
      y: { field: "estimate", label: "Coefficient estimate", unit: "1" },
      uncertainty: { kind: "ci95", spreadField: "stdError", multiplier: 1.959964,
                     statement: "Normal approximation: estimate ± 1.96 standard errors." },
      evidenceClass: el("fig-class").value, caption: el("fig-caption").value.trim(), altText: el("fig-alt").value.trim(),
      interpretation: el("fig-caption").value.trim(), limitations: [el("fig-limit").value.trim()],
    };
    const res = await fetch(`/v1/notebooks/${encodeURIComponent(nb.id)}/revisions/${rev}/cells/${encodeURIComponent(cell.id)}/figure-bundle`, {
      method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) });
    const pkg = await res.json().catch(() => null);
    if (!res.ok) throw new Error(problem(pkg) || `Figure refused (HTTP ${res.status}).`);
    el("fig-out").replaceChildren(
      h("p", {}, `Figure package from run ${pkg.run.runId} (${pkg.run.verification}, ${pkg.run.inputLineage}).`),
      h("p", { class: "fine" }, "Not stored and not published. Lab Graph Studio verifies and renders these files."),
      h("ul", { class: "list" }, ...pkg.files.map(f => {
        const url = URL.createObjectURL(new Blob([f.text], { type: f.mediaType }));
        return h("li", {}, h("a", { href: url, download: f.name }, f.name), " ", h("code", { title: f.sha256 }, `sha256 ${short(f.sha256)}…`));
      })));
  });
}

// --- wiring -----------------------------------------------------------------------------------------------

function wire() {
  el("signout").addEventListener("click", async () => {
    if ((await identityProvider()) === "sc-identity") await fetch("/v1/auth/logout", { method: "POST", credentials: "same-origin" }).catch(() => null);
    else await fetch("/v1/session", { method: "DELETE", credentials: "same-origin" }).catch(() => null);
    showSignIn();
  });
  el("project").addEventListener("change", async () => { state.projectId = el("project").value; state.nb = null; state.saved = null; render(); await loadProject(); });
  el("project-form").addEventListener("submit", createProject);
  el("notebook-form").addEventListener("submit", (ev) => busy(ev.submitter || ev.target, () => createNotebook(ev)));
  el("dataset-form").addEventListener("submit", storeDataset);
  el("save").addEventListener("click", (ev) => busy(ev.currentTarget, save));
  el("run").addEventListener("click", (ev) => runAll(ev.currentTarget));
  el("recipe").addEventListener("change", renderCellForm);
  el("cell-dataset").addEventListener("change", renderCellForm);
  el("cell-outcome").addEventListener("change", renderCellForm);
  el("cell-form").addEventListener("submit", submitCell);
  el("cell-cancel").addEventListener("click", resetCellForm);
  el("cmp-go").addEventListener("click", compare);
  el("fig-form").addEventListener("submit", buildFigure);
  el("fig-close").addEventListener("click", () => { el("figure").hidden = true; });
  window.addEventListener("beforeunload", (e) => { if (state.dirty) { e.preventDefault(); e.returnValue = ""; } });
}

if (typeof document !== "undefined" && document.getElementById("app")) {
  wire();
  boot().catch(e => notice(e.message, "error"));
}
