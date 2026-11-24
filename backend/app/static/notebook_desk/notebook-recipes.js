// SC-SCI-01 notebook cell recipes. A recipe turns a researcher's choices (dataset, outcome, predictors)
// into an sc-workspace-notebook-cell-v1 cell for one governed runtime operation, plus the model record whose
// researchResultValues declaration (value names, uncertainty, pre-registered tolerance) Workspace and
// Research read the result through. Runtimes execute the declared operation only; the cell source text
// documents the method. Pure functions; the page and the tests import them.

export const NOTEBOOK_SCHEMA = "sc-workspace-notebook/3.0";
export const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$/;
export const FIELD = /^[A-Za-z_][A-Za-z0-9_.]{0,63}$/;
export const CLASSIFICATIONS = ["synthetic", "observed", "modelled"];
// SC-MATH-01 M3: declared with the model revision before any run; a reproduction can tighten, never loosen.
export const TOLERANCE = { relative: 1e-8, absolute: 1e-10 };

export function slug(text, fallback = "item") {
  const s = String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48);
  return s || fallback;
}

function datasetInput(ds, transform) {
  if (!ds || !ID.test(String(ds.datasetId || "")) || !Number.isInteger(ds.revision) || !/^[0-9a-f]{64}$/.test(String(ds.artifactSha256 || ""))) {
    throw new Error("Choose a dataset with pinned bytes (a stored file with a SHA-256).");
  }
  const spec = { datasetId: ds.datasetId, datasetRevision: ds.revision, format: "json-records", artifactSha256: ds.artifactSha256 };
  if (transform) spec.transform = transform;
  return spec;
}

function fields(outcome, predictors) {
  const p = (Array.isArray(predictors) ? predictors : String(predictors || "").split(","))
    .map(x => String(x).trim()).filter(Boolean);
  if (!FIELD.test(String(outcome || ""))) throw new Error("Name the outcome column.");
  if (!p.length || p.length > 8 || !p.every(x => FIELD.test(x))) throw new Error("Name one to eight predictor columns.");
  if (p.includes(outcome)) throw new Error("The outcome cannot also be a predictor.");
  return { outcome: String(outcome), predictors: p };
}

/** Model ids are per project and per specification, so a cell keeps pointing at the declaration it ran with. */
export function modelId(projectId, kind, outcome, predictors) {
  return `${slug(projectId, "project").slice(0, 40)}-${kind}-${slug([outcome, ...predictors].join("-"), "model").slice(0, 60)}`;
}

export const RECIPES = {
  "r-linear-model": {
    title: "R · linear model (lm)",
    language: "r",
    type: "code",
    needsDataset: true,
    describe: ({ outcome, predictors }) => `fit <- lm(${outcome} ~ ${predictors.join(" + ")}, data = rows)`,
    build({ projectId, cellId, dataset, outcome, predictors, title }) {
      const f = fields(outcome, predictors);
      const mid = modelId(projectId, "r-ols", f.outcome, f.predictors);
      const model = {
        schema: "sc-workspace-model-record/1.0", modelId: mid, projectId,
        name: `OLS ${f.outcome} ~ ${f.predictors.join(" + ")} (R lm)`, modelKind: "statistical", framework: "R",
        algorithm: "lm (QR)", executionTarget: "workspace", executionOperation: "workspace.polyglot.r.linear-model",
        metadata: { researchResultValues: { kind: "coefficient-table", uncertaintyField: "stdError",
                                            tolerance: { ...TOLERANCE }, rename: { "(Intercept)": "intercept" } } },
      };
      const cell = {
        id: cellId, type: "code", language: "r", title: title || `Linear model of ${f.outcome}`,
        source: RECIPES["r-linear-model"].describe(f),
        execution: { operation: "workspace.polyglot.r.linear-model", modelRef: { modelId: mid }, maxAttempts: 1,
                     payload: { datasetInput: datasetInput(dataset), outcome: f.outcome, predictors: f.predictors } },
      };
      return { cell, model };
    },
  },
  "julia-least-squares": {
    title: "Julia · independent least squares (normal equations)",
    language: "julia",
    type: "code",
    needsDataset: true,
    describe: ({ outcome, predictors }) =>
      `# Independent implementation: solve (XᵀX) b = Xᵀy for ${outcome} on ${predictors.join(", ")}\nsolution = Q \\ (-c)`,
    build({ projectId, cellId, dataset, outcome, predictors, title, after }) {
      const f = fields(outcome, predictors);
      const mid = modelId(projectId, "julia-ols", f.outcome, f.predictors);
      const model = {
        schema: "sc-workspace-model-record/1.0", modelId: mid, projectId,
        name: `OLS ${f.outcome} ~ ${f.predictors.join(" + ")} (Julia normal equations)`, modelKind: "optimization",
        framework: "Julia", algorithm: "Cholesky normal equations", executionTarget: "workspace",
        executionOperation: "workspace.polyglot.julia.quadratic-optimize",
        metadata: { researchResultValues: { kind: "vector", key: "solution", names: ["intercept", ...f.predictors] } },
      };
      const transform = { kind: "least-squares-normal-equations", outcome: f.outcome, predictors: f.predictors };
      const cell = {
        id: cellId, type: "code", language: "julia", title: title || `Independent least squares for ${f.outcome}`,
        source: RECIPES["julia-least-squares"].describe(f),
        execution: { operation: "workspace.polyglot.julia.quadratic-optimize", modelRef: { modelId: mid }, maxAttempts: 1,
                     dependsOnCellIds: after ? [after] : [],
                     payload: { datasetInput: datasetInput(dataset, transform) } },
      };
      return { cell, model };
    },
  },
  "scenario-from-fit": {
    title: "Decision · scenarios from a verified fit (uses upstream results)",
    language: null,
    type: "decision-studio",
    needsDataset: false,
    build({ cellId, primary, crossCheck, slopeName, rates, title }) {
      if (!ID.test(String(primary || ""))) throw new Error("Choose the verified fit cell this scenario uses.");
      if (!FIELD.test(String(slopeName || ""))) throw new Error("Name the predictor whose slope drives the scenarios.");
      const r = String(rates || "").split(",").map(x => Number(x.trim())).filter(x => Number.isFinite(x));
      if (!r.length || r.length > 64) throw new Error("Give one to 64 numeric rates, separated by commas.");
      const cells = [{ cellId: primary, role: "primary" }];
      if (crossCheck && crossCheck !== primary) cells.push({ cellId: crossCheck, role: "cross-check" });
      const cell = {
        id: cellId, type: "decision-studio", source: "", title: title || "Scenario comparison from the verified fit",
        execution: { operation: "workspace.decision.minimax-regret", maxAttempts: 1,
                     dependsOnCellIds: cells.map(c => c.cellId),
                     payload: { upstreamInput: { cells, transform: {
                       kind: "linear-scenario-scores", rates: r, uncertaintyMultiplier: 2,
                       scenarioProbabilities: [0.25, 0.5, 0.25], direction: "maximize",
                       names: { intercept: "intercept", slope: slopeName }, candidatePrefix: "rate",
                       candidateUnit: "", crossCheckTolerance: 1e-6 } } } },
      };
      return { cell, model: null };
    },
  },
};

export function newNotebook(id, title, description = "") {
  if (!ID.test(id)) throw new Error("Notebook id is invalid.");
  const t = String(title || "").trim().slice(0, 160) || "Research notebook";
  return { schema: NOTEBOOK_SCHEMA, id, title: t, description: String(description).slice(0, 1200),
           sections: [{ id: "s-notes", title: "Notes", blocks: [] }], cells: [] };
}

export function markdownCell(cellId, text) {
  return { id: cellId, type: "markdown", source: String(text || "").slice(0, 20000) };
}

/** Next unused cell id with a readable prefix. */
export function nextCellId(cells, prefix) {
  const used = new Set((cells || []).map(c => c.id));
  for (let i = 1; i < 1000; i++) { const id = `${prefix}-${i}`; if (!used.has(id)) return id; }
  throw new Error("Too many cells.");
}

/** Cells that depend (directly or transitively) on `cellId`; editing it makes their results stale. */
export function downstream(cells, cellId) {
  const out = new Set(); let frontier = [cellId];
  while (frontier.length) {
    const next = [];
    for (const c of cells || []) {
      const deps = (c.execution && c.execution.dependsOnCellIds) || [];
      if (!out.has(c.id) && deps.some(d => frontier.includes(d))) { out.add(c.id); next.push(c.id); }
    }
    frontier = next;
  }
  return [...out];
}

/** Removing a cell that others depend on would break the plan; say which. */
export function dependents(cells, cellId) {
  return (cells || []).filter(c => ((c.execution && c.execution.dependsOnCellIds) || []).includes(cellId)).map(c => c.id);
}

/** CSV text to JSON records (numbers where every value in a column parses as one). Header row required. */
export function csvRecords(text) {
  const lines = String(text || "").replace(/\r\n?/g, "\n").split("\n").filter(l => l.trim() !== "");
  if (lines.length < 2) throw new Error("The CSV needs a header row and at least one data row.");
  const split = (line) => {
    const out = []; let cur = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (q) { if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
      else if (ch === '"') q = true; else if (ch === ",") { out.push(cur); cur = ""; } else cur += ch;
    }
    out.push(cur); return out.map(s => s.trim());
  };
  const head = split(lines[0]);
  if (head.some(h => !FIELD.test(h)) || new Set(head).size !== head.length) {
    throw new Error("Column names must be unique identifiers (letters, digits, underscore).");
  }
  const rows = lines.slice(1).map(split);
  if (rows.some(r => r.length !== head.length)) throw new Error("Every row needs one value per column.");
  const numeric = head.map((_, j) => rows.every(r => r[j] !== "" && Number.isFinite(Number(r[j]))));
  return rows.map(r => Object.fromEntries(head.map((h, j) => [h, numeric[j] ? Number(r[j]) : r[j]])));
}

/** The JSON-records bytes Workspace pins: one canonical serialisation, so the hash is reproducible. */
export function recordsBytes(records) {
  if (!Array.isArray(records) || !records.length || records.length > 100000 || !records.every(r => r && typeof r === "object" && !Array.isArray(r))) {
    throw new Error("A dataset is a non-empty list of records.");
  }
  const canon = (v) => Array.isArray(v) ? v.map(canon) : v && typeof v === "object"
    ? Object.fromEntries(Object.keys(v).sort().map(k => [k, canon(v[k])])) : v;
  return new TextEncoder().encode(JSON.stringify(canon(records)));
}

export function columns(records) {
  const first = Array.isArray(records) && records[0] && typeof records[0] === "object" ? records[0] : {};
  return Object.keys(first).map(k => ({ name: k, numeric: records.every(r => typeof r[k] === "number" && Number.isFinite(r[k])) }));
}

// --- what a result is, in words a reader can rely on ----------------------------------------------------

export const STATE_TEXT = {
  "not-run": "Not run",
  running: "Running",
  failed: "Failed",
  unverified: "Ran, not verified",
  stale: "Stale — an input changed since this result",
  verified: "Executed and verified",
};

export const LINEAGE_TEXT = {
  "artifact-bound-verified": "inputs verified (pinned dataset bytes)",
  "parameter-set-bound": "inputs from a pinned parameter set",
  "not-executed": "no runtime receipt",
};

/** Plain description of one cell's evidence. Never calls a numerical check a proof. */
export function describeEvidence(item) {
  const v = (item && item.run && item.run.verification) || {};
  const rv = (item && item.run && item.run.resultValues) || {};
  const notes = [];
  if (v.inputLineage) notes.push(LINEAGE_TEXT[v.inputLineage] || `inputs: ${v.inputLineage} (unverified inputs)`);
  if (rv.stochastic) notes.push(rv.stochastic.seed != null ? `stochastic, seed ${rv.stochastic.seed}: a same-seed rerun shows determinism, not reproduction` : "stochastic");
  if (rv.identityCheck) notes.push(`numerical check at ${rv.identityCheck.pointCount} declared points — evidence, not a proof`);
  if (rv.tolerance) notes.push(`declared tolerance: relative ${rv.tolerance.relative}, absolute ${rv.tolerance.absolute}`);
  if (rv.assumptions) notes.push("statistical assumptions declared by the model owner, not tested");
  const receipt = (v.runtimeReceipts || [])[0];
  if (receipt) notes.push(`${receipt.runtime || receipt.language} ${receipt.runtimeVersion || ""}`.trim());
  return notes;
}

/**
 * Side-by-side agreement of two verified cells' shared values, judged at the first cell's declared tolerance.
 * This is a Workspace preview only: Research records whether it is a reproduction (identical verified inputs,
 * independence and identity rules). Different languages → independent implementation; same → replay.
 */
export function agreement(a, b) {
  const va = (a && a.run && a.run.resultValues && a.run.resultValues.values) || {};
  const vb = (b && b.run && b.run.resultValues && b.run.resultValues.values) || {};
  const tol = (a && a.run && a.run.resultValues && a.run.resultValues.tolerance) || TOLERANCE;
  const names = Object.keys(va).filter(k => k in vb).sort();
  if (!names.length || a.state !== "verified" || b.state !== "verified") {
    return { status: "not-comparable", names: [], rows: [], independence: null, tolerance: tol };
  }
  const rows = names.map(n => {
    const x = va[n], y = vb[n], diff = Math.abs(x - y);
    const within = diff <= Math.max(tol.absolute, tol.relative * Math.max(Math.abs(x), Math.abs(y)));
    return { name: n, a: x, b: y, diff, within };
  });
  const independence = a.language && b.language && a.language !== b.language ? "independent-implementation" : "replay";
  const lineage = [a, b].every(c => c.run.verification.inputLineage === "artifact-bound-verified");
  let status = rows.every(r => r.within) ? "agrees-within-tolerance" : "disagrees";
  if (status === "agrees-within-tolerance" && !lineage) status = "agrees-unverified-inputs";
  return { status, names, rows, independence, tolerance: tol };
}

export const AGREEMENT_TEXT = {
  "agrees-within-tolerance": "Agree within the declared tolerance on verified inputs",
  "agrees-unverified-inputs": "Agree numerically, but inputs are not verified — not a reproduction",
  disagrees: "Disagree beyond the declared tolerance — failed reproduction",
  "not-comparable": "Not comparable yet (both cells need current, verified results with shared value names)",
};
