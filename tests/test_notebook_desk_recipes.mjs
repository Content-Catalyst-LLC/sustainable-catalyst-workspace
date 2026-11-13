// SC-SCI-01 notebook workspace recipes (pure helpers). Run: node --test tests/test_notebook_desk_recipes.mjs
import assert from "node:assert/strict";
import { test } from "node:test";

import {
  AGREEMENT_TEXT, RECIPES, STATE_TEXT, agreement, columns, csvRecords, dependents, describeEvidence, downstream,
  markdownCell, modelId, newNotebook, nextCellId, recordsBytes,
} from "../backend/app/static/notebook_desk/notebook-recipes.js";

const SHA = "a".repeat(64);
const DS = { datasetId: "erw-dose", revision: 2, artifactSha256: SHA };

test("R linear model cell binds the pinned dataset revision and declares its values and tolerance", () => {
  const { cell, model } = RECIPES["r-linear-model"].build({ projectId: "wexford-erw", cellId: "fit-1", dataset: DS,
    outcome: "cation_flux", predictors: ["rate"] });
  assert.equal(cell.type, "code");
  assert.equal(cell.language, "r");
  assert.equal(cell.execution.operation, "workspace.polyglot.r.linear-model");
  assert.deepEqual(cell.execution.payload, { datasetInput: { datasetId: "erw-dose", datasetRevision: 2, format: "json-records",
    artifactSha256: SHA }, outcome: "cation_flux", predictors: ["rate"] });
  assert.equal(cell.execution.modelRef.modelId, model.modelId);
  assert.equal(cell.source, "fit <- lm(cation_flux ~ rate, data = rows)");
  const rv = model.metadata.researchResultValues;
  assert.equal(rv.kind, "coefficient-table");
  assert.equal(rv.uncertaintyField, "stdError");
  assert.deepEqual(rv.tolerance, { relative: 1e-8, absolute: 1e-10 });
  assert.deepEqual(rv.rename, { "(Intercept)": "intercept" });
});

test("Julia least squares is an independent implementation over the same pinned bytes, with matching value names", () => {
  const { cell, model } = RECIPES["julia-least-squares"].build({ projectId: "wexford-erw", cellId: "check-1", dataset: DS,
    outcome: "cation_flux", predictors: "rate, temp" });
  assert.equal(cell.language, "julia");
  assert.equal(cell.execution.operation, "workspace.polyglot.julia.quadratic-optimize");
  assert.deepEqual(cell.execution.dependsOnCellIds, []);
  assert.deepEqual(cell.execution.payload.datasetInput.transform,
    { kind: "least-squares-normal-equations", outcome: "cation_flux", predictors: ["rate", "temp"] });
  assert.equal(cell.execution.payload.datasetInput.artifactSha256, SHA);
  assert.deepEqual(model.metadata.researchResultValues.names, ["intercept", "rate", "temp"]);
  const after = RECIPES["julia-least-squares"].build({ projectId: "p", cellId: "c", dataset: DS, outcome: "y", predictors: ["x"], after: "fit-1" });
  assert.deepEqual(after.cell.execution.dependsOnCellIds, ["fit-1"]);
});

test("scenario cell takes upstream verified results, never typed values", () => {
  const { cell, model } = RECIPES["scenario-from-fit"].build({ cellId: "scenario-1", primary: "fit-1", crossCheck: "check-1",
    slopeName: "rate", rates: "10, 25, x, 40" });
  assert.equal(model, null);
  assert.equal(cell.type, "decision-studio");
  assert.deepEqual(cell.execution.dependsOnCellIds, ["fit-1", "check-1"]);
  const u = cell.execution.payload.upstreamInput;
  assert.deepEqual(u.cells, [{ cellId: "fit-1", role: "primary" }, { cellId: "check-1", role: "cross-check" }]);
  assert.deepEqual(u.transform.rates, [10, 25, 40]);
  assert.deepEqual(u.transform.names, { intercept: "intercept", slope: "rate" });
  assert.deepEqual(Object.keys(cell.execution.payload), ["upstreamInput"]);
});

test("recipes refuse unpinned datasets and malformed columns", () => {
  const b = (o) => () => RECIPES["r-linear-model"].build({ projectId: "p", cellId: "c", dataset: DS, outcome: "y", predictors: ["x"], ...o });
  assert.throws(b({ dataset: { datasetId: "d", revision: 1, artifactSha256: null } }), /pinned bytes/);
  assert.throws(b({ dataset: { datasetId: "d", revision: "1", artifactSha256: SHA } }), /pinned bytes/);
  assert.throws(b({ outcome: "y; system('x')" }), /outcome/);
  assert.throws(b({ predictors: [] }), /predictor/);
  assert.throws(b({ predictors: ["y"] }), /outcome cannot/);
  assert.throws(() => RECIPES["scenario-from-fit"].build({ cellId: "s", primary: "", slopeName: "x", rates: "1" }), /verified fit/);
});

test("model ids are stable per project and specification", () => {
  assert.equal(modelId("Wexford ERW", "r-ols", "y", ["x"]), modelId("Wexford ERW", "r-ols", "y", ["x"]));
  assert.notEqual(modelId("p", "r-ols", "y", ["x"]), modelId("p", "r-ols", "y", ["x", "z"]));
  assert.match(modelId("p".repeat(300), "r-ols", "y", ["x"]), /^[a-z0-9-]{1,160}$/);
});

test("notebooks, ids and dependency helpers", () => {
  const nb = newNotebook("nb-erw-1", "  Wexford ERW  ");
  assert.equal(nb.schema, "sc-workspace-notebook/3.0");
  assert.equal(nb.title, "Wexford ERW");
  assert.throws(() => newNotebook("../x", "t"));
  const cells = [{ id: "fit-1" }, { id: "check-1", execution: { dependsOnCellIds: ["fit-1"] } },
                 { id: "scenario-1", execution: { dependsOnCellIds: ["check-1"] } }, markdownCell("text-1", "hi")];
  assert.equal(nextCellId(cells, "fit"), "fit-2");
  assert.deepEqual(downstream(cells, "fit-1"), ["check-1", "scenario-1"]);
  assert.deepEqual(dependents(cells, "fit-1"), ["check-1"]);
  assert.deepEqual(dependents(cells, "scenario-1"), []);
});

test("CSV becomes canonical JSON records whose bytes are reproducible", () => {
  const recs = csvRecords('rate,flux,site\r\n10,1.5,"Wexford, A"\n20,2.0,B\n');
  assert.deepEqual(recs, [{ rate: 10, flux: 1.5, site: "Wexford, A" }, { rate: 20, flux: 2, site: "B" }]);
  assert.deepEqual(columns(recs), [{ name: "rate", numeric: true }, { name: "flux", numeric: true }, { name: "site", numeric: false }]);
  const a = new TextDecoder().decode(recordsBytes([{ b: 1, a: 2 }])), b = new TextDecoder().decode(recordsBytes([{ a: 2, b: 1 }]));
  assert.equal(a, b);
  assert.equal(a, '[{"a":2,"b":1}]');
  assert.throws(() => csvRecords("a,a\n1,2"), /unique/);
  assert.throws(() => csvRecords("a,b\n1"), /one value per column/);
  assert.throws(() => recordsBytes([]), /non-empty/);
});

const item = (cellId, language, values, extra = {}) => ({ cellId, language, state: "verified",
  run: { verification: { status: "executed-verified", inputLineage: "artifact-bound-verified", runtimeReceipts: [] },
         resultValues: { values, tolerance: { relative: 1e-8, absolute: 1e-10 } } }, ...extra });

test("agreement distinguishes independent agreement, replay, failed reproduction and unverified inputs", () => {
  const r = item("fit", "r", { intercept: 1.5, slope: 0.25 });
  const j = item("check", "julia", { intercept: 1.5 + 1e-12, slope: 0.25 });
  let out = agreement(r, j);
  assert.equal(out.status, "agrees-within-tolerance");
  assert.equal(out.independence, "independent-implementation");
  assert.equal(agreement(r, item("again", "r", { intercept: 1.5, slope: 0.25 })).independence, "replay");
  out = agreement(r, item("check", "julia", { intercept: 1.6, slope: 0.25 }));
  assert.equal(out.status, "disagrees");
  assert.deepEqual(out.rows.map(x => x.within), [false, true]);
  const unverified = item("check", "julia", { intercept: 1.5, slope: 0.25 });
  unverified.run.verification.inputLineage = "unrecorded";
  assert.equal(agreement(r, unverified).status, "agrees-unverified-inputs");
  assert.equal(agreement(r, { ...j, state: "stale" }).status, "not-comparable");
  for (const s of ["agrees-within-tolerance", "agrees-unverified-inputs", "disagrees", "not-comparable"]) assert.ok(AGREEMENT_TEXT[s]);
  assert.match(AGREEMENT_TEXT["agrees-unverified-inputs"], /not a reproduction/);
});

test("evidence text never calls a numerical check a proof and flags seeded replays", () => {
  const notes = describeEvidence({ run: { verification: { inputLineage: "artifact-bound-verified",
    runtimeReceipts: [{ language: "julia", runtime: "julia-simulation-numerical", runtimeVersion: "1.11.5" }] },
    resultValues: { identityCheck: { pointCount: 7, proof: false }, stochastic: { seed: 42 } } } });
  assert.ok(notes.some(n => /7 declared points — evidence, not a proof/.test(n)));
  assert.ok(notes.some(n => /seed 42.*not reproduction/.test(n)));
  assert.ok(notes.includes("inputs verified (pinned dataset bytes)"));
  assert.ok(!notes.some(n => /\bproven\b|\bproof\b(?!,)/.test(n.replace("not a proof", ""))));
  for (const s of ["not-run", "running", "failed", "unverified", "stale", "verified"]) assert.ok(STATE_TEXT[s]);
});
