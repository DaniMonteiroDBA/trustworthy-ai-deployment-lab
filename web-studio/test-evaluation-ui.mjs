import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const js = readFileSync(new URL("./public/assets/app.js", import.meta.url), "utf8");
const start = js.indexOf("  async function runEvaluation() {");
const end = js.indexOf("\n  function openModal(", start);
assert.ok(start >= 0 && end > start, "Offline evaluation handler must be present");

function setup(apiImpl) {
  const button = { disabled: false, textContent: "Run offline evaluation ▶" };
  const calls = { requests: [], results: [], toasts: [] };
  const context = {
    $: id => {
      assert.equal(id, "eval-run-button");
      return button;
    },
    api: async (path, options) => {
      calls.requests.push({ path, options });
      return apiImpl(path, options);
    },
    renderEvaluation: result => calls.results.push(result),
    toast: (...args) => calls.toasts.push(args),
  };
  runInNewContext(js.slice(start, end), context);
  return { button, calls, run: context.runEvaluation };
}

let finish;
const pending = setup(() => new Promise(resolve => { finish = resolve; }));
const operation = pending.run();
assert.equal(pending.button.disabled, true, "Button is disabled during evaluation");
assert.equal(pending.calls.requests.length, 1);
const request = pending.calls.requests[0];
assert.equal(request.path, "/api/evaluations/offline");
assert.equal(request.options.method, "POST");
assert.equal(request.options.body, "{}", "POST must send a valid JSON body");
assert.deepEqual(JSON.parse(request.options.body), {});
const fixture = { run_mode: "OFFLINE_DETERMINISTIC" };
finish(fixture);
await operation;
assert.equal(pending.button.disabled, false);
assert.equal(pending.button.textContent, "Run offline evaluation ▶");
assert.equal(pending.calls.results[0], fixture);
assert.match(pending.calls.toasts[0][0], /completed/);

const failing = setup(async () => { throw new Error("Simulated service outage"); });
await failing.run();
assert.equal(failing.button.disabled, false, "Button resets after errors");
assert.equal(failing.calls.results.length, 0);
assert.equal(failing.calls.toasts[0][0], "Simulated service outage");
assert.equal(failing.calls.toasts[0][1], true);

console.log("Offline evaluation UI: valid JSON request, successful rendering and error reset passed.");
