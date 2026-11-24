// node --test backend/tests/js/approval_desk.test.mjs
import assert from "node:assert/strict";
import test from "node:test";

import {
  CONFIRM_CHARS, DESK_PATH, confirmationMatches, parseSubject, problem, resumeState, shortHash, stepUpUrl,
} from "../../app/static/approval_desk/approval-desk.js";

const HASH = "0123456789abcdef".repeat(4);
const SUBJECT = `research-object:obj_1#${HASH}`;

test("subject references parse into kind, id and content hash", () => {
  assert.deepEqual(parseSubject(SUBJECT), { kind: "object", id: "obj_1", hash: HASH });
  assert.equal(parseSubject(`research-area:a#${HASH}`).kind, "area");
  for (const bad of ["", null, "research-object:x#abc", `research-x:a#${HASH}`, `research-object:a b#${HASH}`]) {
    assert.equal(parseSubject(bad), null);
  }
});

test("approval needs the first 12 characters of this revision's hash", () => {
  assert.equal(CONFIRM_CHARS, 12);
  assert.ok(confirmationMatches(SUBJECT, HASH.slice(0, 12)));
  assert.ok(confirmationMatches(SUBJECT, ` ${HASH.slice(0, 12).toUpperCase()} `));
  assert.ok(confirmationMatches(SUBJECT, HASH));
  assert.ok(!confirmationMatches(SUBJECT, HASH.slice(0, 11)));
  assert.ok(!confirmationMatches(SUBJECT, "f" + HASH.slice(1, 12)));
  assert.ok(!confirmationMatches("not-a-subject", HASH.slice(0, 12)));
  assert.equal(shortHash(SUBJECT), HASH.slice(0, 12));
});

test("step-up sign-in returns to the desk with the request to resume", () => {
  const url = stepUpUrl("/v1/auth/login?stepUp=true", "approval_ab12");
  assert.equal(url, `/v1/auth/login?stepUp=true&returnTo=${encodeURIComponent(`${DESK_PATH}?resume=approval_ab12`)}`);
  // a login URL from anywhere else is never followed
  assert.ok(stepUpUrl("https://evil.example/login", "a").startsWith("/v1/auth/login?stepUp=true&returnTo="));
  assert.ok(stepUpUrl(undefined, "a").startsWith("/v1/auth/login?stepUp=true&returnTo="));
});

test("after step-up the same revision must be confirmed again; a changed one must be reviewed again", () => {
  const stored = { approvalId: "a1", subjectRef: SUBJECT, decision: "approve", note: "ok" };
  const pending = { approvalId: "a1", subjectRef: SUBJECT, status: "pending" };
  assert.deepEqual(resumeState(stored, "a1", pending), { kind: "reconfirm", decision: "approve", note: "ok" });
  assert.equal(resumeState(stored, "a1", { ...pending, subjectRef: `research-object:obj_1#${"f".repeat(64)}` }).kind, "changed");
  assert.equal(resumeState(stored, "a1", { ...pending, status: "approved" }).kind, "gone");
  assert.equal(resumeState(stored, "a1", null).kind, "gone");
  assert.equal(resumeState(stored, "a2", pending).kind, "none");
  assert.equal(resumeState(null, "a1", pending).kind, "none");
});

test("API problems are read from Workspace's flattened errors and FastAPI details", () => {
  assert.deepEqual(problem({ ok: false, code: "step-up-required", message: "m", loginUrl: "/v1/auth/login?stepUp=true" }),
    { code: "step-up-required", message: "m", loginUrl: "/v1/auth/login?stepUp=true" });
  assert.deepEqual(problem({ ok: false, message: "approval request is approved" }),
    { code: "", message: "approval request is approved", loginUrl: "" });
  assert.deepEqual(problem({ detail: { code: "step-up-required", message: "m", loginUrl: "/v1/auth/login?stepUp=true" } }),
    { code: "step-up-required", message: "m", loginUrl: "/v1/auth/login?stepUp=true" });
  assert.deepEqual(problem({ detail: "approval request is approved" }), { code: "", message: "approval request is approved", loginUrl: "" });
  assert.deepEqual(problem(null), { code: "", message: "", loginUrl: "" });
});
