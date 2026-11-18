import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const js = readFileSync(new URL("./public/assets/app.js", import.meta.url), "utf8");
const html = readFileSync(new URL("./public/studio/index.html", import.meta.url), "utf8");
const css = readFileSync(new URL("./public/assets/styles.css", import.meta.url), "utf8");
const start = js.indexOf("  async function onDecisionSubmit(event) {");
const end = js.indexOf("  async function openReport()", start);
assert.ok(start >= 0 && end > start, "Decision submit handler must be present");
assert.match(html, /id="decision-error"[^>]*role="alert"/);
assert.match(css, /\.form-error\[hidden\]\{display:none\}/);

function setup(apiImpl, reloadImpl = async () => {}) {
  const button = { disabled: false, textContent: "Save decision" };
  const box = { hidden: true, textContent: "", focusCount: 0, focus() { this.focusCount++; } };
  const dialog = { open: true };
  const attributes = new Map();
  const form = {
    dataset: {},
    querySelector(selector) { assert.equal(selector, 'button[type="submit"]'); return button; },
    setAttribute(key, value) { attributes.set(key, value); },
    removeAttribute(key) { attributes.delete(key); }
  };
  const fields = { status: "GO", owner: "Fictional reviewer", rationale: "A fictional decision for testing.", evidence_ids: ["e-demo-001"], blockers: "", alternatives: "Fictional manual process" };
  const calls = { api: 0, close: 0, reload: 0, toast: [] };
  class FakeFormData {
    constructor(receivedForm) { assert.equal(receivedForm, form); }
    get(key) { return fields[key]; }
    getAll(key) { return fields[key]; }
  }
  const context = {
    FormData: FakeFormData,
    state: { stageIndex: 0, record: { case_id: "fictional-case" } },
    STAGES: [{ id: "DISCOVER" }],
    $: id => ({ "decision-error": box, "decision-dialog": dialog })[id],
    listLines: value => String(value || "").split("\n").filter(Boolean),
    api: async (...args) => { calls.api++; return apiImpl(...args); },
    closeModal: () => { calls.close++; dialog.open = false; },
    selectCase: async () => { calls.reload++; await reloadImpl(); },
    toast: (...args) => { calls.toast.push(args); }
  };
  runInNewContext(js.slice(start, end), context);
  return { button, box, form, attributes, calls, submit: () => context.onDecisionSubmit({ preventDefault() {}, currentTarget: form }) };
}

const messages = [
  ["A simulated GO requires referenced, reviewed documentary evidence.", "add a DOCUMENTED fictional evidence"],
  ["Resolve blockers before a simulated GO.", "choose HOLD, REWORK or NO GO"],
  ["This gate requires measured evidence. Browser preview has no such pipeline.", "cannot produce them"]
];

for (const [message, guidance] of messages) {
  const ui = setup(async () => { throw new Error(message); });
  await ui.submit();
  assert.equal(ui.box.hidden, false);
  assert.match(ui.box.textContent, /Decision not saved:/);
  assert.ok(ui.box.textContent.includes(message));
  assert.ok(ui.box.textContent.includes(guidance));
  assert.equal(ui.box.focusCount, 1);
  assert.equal(ui.calls.close, 0);
  assert.equal(ui.calls.api, 1);
  assert.equal(ui.button.disabled, false);
  assert.equal(ui.button.textContent, "Save decision");
  assert.equal(ui.attributes.has("aria-busy"), false);
  assert.equal(ui.calls.toast.length, 0, "Error must not be hidden in the page toast");
}

let release;
const pending = setup(() => new Promise(resolve => { release = resolve; }));
const saving = pending.submit();
assert.equal(pending.button.disabled, true);
assert.equal(pending.button.textContent, "Validating…");
assert.equal(pending.attributes.get("aria-busy"), "true");
await pending.submit();
assert.equal(pending.calls.api, 1, "Repeated submission must not send a second request");
release({});
await saving;
assert.equal(pending.calls.close, 1);
assert.equal(pending.calls.reload, 1);
assert.equal(pending.box.hidden, true);
assert.equal(pending.button.disabled, false);
assert.equal(pending.button.textContent, "Save decision");

const stale = setup(async () => ({}), async () => { throw new Error("offline"); });
await stale.submit();
assert.equal(stale.box.hidden, true, "A successful save must not be described as a rejected decision");
assert.equal(stale.calls.close, 1);
assert.match(stale.calls.toast[0][0], /Decision saved, but the Studio could not refresh: offline/);

console.log("Decision dialog UI: error guidance, focus, busy state and duplicate-submit checks passed.");
