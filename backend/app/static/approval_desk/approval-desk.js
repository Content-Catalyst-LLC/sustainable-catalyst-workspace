// SC-PUB-M1 Research approval desk. Same-origin; every decision is made by the authenticated
// /v1/research-approvals API. The pure helpers are exported for tests; the page wiring runs only
// in a browser.

export const DESK_PATH = "/v1/desk/approvals";
export const PENDING_KEY = "sc-approval-desk:pending";
export const CONFIRM_CHARS = 12;
const SUBJECT = /^research-(object|area):([A-Za-z0-9._:-]{1,160})#([0-9a-f]{64})$/;

/** Split a subject reference into kind, id and content hash; null if it is not one. */
export function parseSubject(subjectRef) {
  const m = SUBJECT.exec(String(subjectRef || ""));
  return m ? { kind: m[1], id: m[2], hash: m[3] } : null;
}

/** The person confirmed this exact revision by typing the start of its content hash. */
export function confirmationMatches(subjectRef, typed) {
  const s = parseSubject(subjectRef);
  const t = String(typed || "").trim().toLowerCase();
  return Boolean(s) && t.length >= CONFIRM_CHARS && s.hash.startsWith(t);
}

/** The step-up sign-in URL, returning to this desk with the request to resume. */
export function stepUpUrl(loginUrl, approvalId) {
  const base = typeof loginUrl === "string" && loginUrl.startsWith("/v1/auth/login") ? loginUrl : "/v1/auth/login?stepUp=true";
  const back = `${DESK_PATH}?resume=${encodeURIComponent(approvalId)}`;
  return `${base}${base.includes("?") ? "&" : "?"}returnTo=${encodeURIComponent(back)}`;
}

/** Decide what to do with a stored pending decision once the person is back from signing in. */
export function resumeState(stored, resumeId, current) {
  if (!stored || !resumeId || stored.approvalId !== resumeId) return { kind: "none" };
  if (!current || current.status !== "pending") return { kind: "gone" };
  if (current.subjectRef !== stored.subjectRef) return { kind: "changed" };
  return { kind: "reconfirm", decision: stored.decision, note: stored.note || "" };
}

/** Problem codes from the API: Workspace flattens errors to {ok: false, code, message, loginUrl};
 *  FastAPI's default shape ({detail: {...}} or {detail: "text"}) is accepted too. */
export function problem(body) {
  if (!body || typeof body !== "object") return { code: "", message: "", loginUrl: "" };
  const d = body.detail && typeof body.detail === "object" ? body.detail : body;
  const message = typeof d.message === "string" ? d.message : typeof body.detail === "string" ? body.detail : "";
  return { code: typeof d.code === "string" ? d.code : "", message, loginUrl: typeof d.loginUrl === "string" ? d.loginUrl : "" };
}

export function shortHash(subjectRef) {
  const s = parseSubject(subjectRef);
  return s ? s.hash.slice(0, CONFIRM_CHARS) : "";
}

// --- browser wiring ---------------------------------------------------------------------------

async function api(method, path, body) {
  const init = { method, credentials: "same-origin", headers: { Accept: "application/json" } };
  if (body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }
  const res = await fetch(path, init);
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  return { status: res.status, data };
}

function el(id) { return document.getElementById(id); }

function text(node, value) { node.textContent = value == null ? "" : String(value); return node; }

function row(cells, action) {
  const tr = document.createElement("tr");
  for (const c of cells) {
    const td = document.createElement("td");
    if (c instanceof Node) td.append(c); else text(td, c);
    tr.append(td);
  }
  const td = document.createElement("td");
  if (action) td.append(action);
  tr.append(td);
  return tr;
}

function button(label, onClick, cls) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = label;
  if (cls) b.className = cls;
  b.addEventListener("click", onClick);
  return b;
}

function code(value) { const c = document.createElement("code"); c.textContent = value; return c; }

function notify(message, kind = "info") {
  const n = el("notice");
  n.hidden = !message;
  n.dataset.kind = kind;
  text(n, message);
}

function readPending() {
  try { return JSON.parse(sessionStorage.getItem(PENDING_KEY) || "null"); } catch { return null; }
}

function writePending(value) {
  try {
    if (value) sessionStorage.setItem(PENDING_KEY, JSON.stringify(value));
    else sessionStorage.removeItem(PENDING_KEY);
  } catch { /* storage unavailable: the person simply confirms again */ }
}

const state = { me: null, queue: [], current: null };

function fill(table, empty, items, render) {
  const body = el(table).querySelector("tbody");
  body.replaceChildren(...items.map(render));
  el(empty).hidden = items.length > 0;
}

function openReview(item, opts = {}) {
  state.current = item;
  el("review").hidden = false;
  el("resume-banner").hidden = !opts.resumed;
  text(el("r-title"), item.subjectTitle || "(untitled)");
  text(el("r-dimension"), item.dimension);
  text(el("r-requester"), item.requester);
  text(el("r-project"), item.projectId);
  text(el("r-when"), item.requestedAt);
  text(el("r-subject"), item.subjectRef);
  text(el("r-hash-hint"), shortHash(item.subjectRef).slice(0, 4));
  el("confirm").value = "";
  el("note").value = opts.note || "";
  el("approve").disabled = true;
  el("confirm").focus();
}

function closeReview() {
  state.current = null;
  el("review").hidden = true;
}

async function decide(decision) {
  const item = state.current;
  if (!item) return;
  const note = el("note").value;
  const body = { decision, note };
  if (decision === "approve") {
    if (!confirmationMatches(item.subjectRef, el("confirm").value)) {
      notify("The characters you typed do not match this revision's hash.", "error");
      return;
    }
    body.expectedSubjectRef = item.subjectRef;
  }
  const res = await api("POST", `/v1/research-approvals/requests/${encodeURIComponent(item.approvalId)}/decide`, body);
  const p = problem(res.data);
  if (res.status === 403 && p.code === "step-up-required") {
    writePending({ approvalId: item.approvalId, subjectRef: item.subjectRef, decision, note });
    notify("Approving needs a fresh sign-in with your second factor. Redirecting…");
    window.location.assign(stepUpUrl(p.loginUrl, item.approvalId));
    return;
  }
  writePending(null);
  if (res.status === 200) {
    notify(`${decision === "approve" ? "Approved" : decision === "reject" ? "Rejected" : "Revision requested"}: ${item.subjectTitle || item.approvalId}. Signed record ${(res.data.item.recordSha256 || "").slice(0, 12)}.`, "ok");
    closeReview();
    await refresh();
  } else if (res.status === 409 && p.code === "subject-changed") {
    notify(p.message, "error");
    closeReview();
    await refresh();
  } else if (res.status === 401) {
    showSignIn();
  } else {
    notify(p.message || `The decision was not recorded (HTTP ${res.status}).`, "error");
  }
}

function showSignIn() {
  el("signin").hidden = false;
  el("signout").hidden = true;
  text(el("who"), "");
}

async function refresh() {
  const [queue, mine, owned] = await Promise.all([
    api("GET", "/v1/research-approvals/requests?role=approver&status=pending"),
    api("GET", "/v1/research-approvals/requests?role=requester&status=any"),
    api("GET", "/v1/research-approvals/requests?role=owner&status=any"),
  ]);
  if ([queue, mine, owned].some((r) => r.status === 401)) return showSignIn();
  state.queue = queue.data ? queue.data.items : [];
  fill("queue", "queue-empty", state.queue, (it) => row(
    [it.subjectTitle || "(untitled)", it.dimension, it.requester, code(shortHash(it.subjectRef))],
    button("Review", () => openReview(it))));
  fill("mine", "mine-empty", mine.data ? mine.data.items : [], (it) => row(
    [it.subjectTitle || "(untitled)", it.dimension, it.status, code(shortHash(it.subjectRef))],
    it.status === "pending" ? button("Withdraw", async () => {
      const r = await api("POST", `/v1/research-approvals/requests/${encodeURIComponent(it.approvalId)}/withdraw`, {});
      notify(r.status === 200 ? "Request withdrawn." : problem(r.data).message || `HTTP ${r.status}`, r.status === 200 ? "ok" : "error");
      await refresh();
    }, "secondary") : null));
  fill("owned", "owned-empty", owned.data ? owned.data.items : [], (it) => row(
    [it.subjectTitle || "(untitled)", it.dimension, it.status, it.decider || "—"],
    it.recordSha256 ? code(it.recordSha256.slice(0, 12)) : null));
  return null;
}

async function start() {
  const me = await api("GET", "/v1/session");
  if (me.status !== 200 || !me.data || !me.data.authenticated) return showSignIn();
  state.me = me.data;
  text(el("who"), `Signed in · ${me.data.displayName || me.data.subject || ""}`);
  el("signout").hidden = false;
  await refresh();

  const resumeId = new URLSearchParams(window.location.search).get("resume");
  if (resumeId) {
    const stored = readPending();
    const current = state.queue.find((it) => it.approvalId === resumeId) || null;
    const next = resumeState(stored, resumeId, current);
    writePending(null);
    window.history.replaceState(null, "", DESK_PATH);
    if (next.kind === "reconfirm") openReview(current, { resumed: true, note: next.note });
    else if (next.kind === "changed") notify("The request now points to a different revision. Review it again before deciding.", "error");
    else if (next.kind === "gone") notify("That request is no longer waiting for your decision.", "error");
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    el("confirm").addEventListener("input", () => {
      el("approve").disabled = !(state.current && confirmationMatches(state.current.subjectRef, el("confirm").value));
    });
    el("decide").addEventListener("submit", (ev) => {
      ev.preventDefault();
      decide(ev.submitter ? ev.submitter.value : "approve");
    });
    el("close").addEventListener("click", closeReview);
    el("signout").addEventListener("click", async () => {
      const r = await api("POST", "/v1/auth/logout", {});
      window.location.assign((r.data && r.data.endSessionUrl) || DESK_PATH);
    });
    start().catch(() => notify("Workspace could not be reached. Try again.", "error"));
  });
}
