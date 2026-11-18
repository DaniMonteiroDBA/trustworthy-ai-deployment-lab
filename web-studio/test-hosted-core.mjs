import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createStudioCore } from "./lib/studio-core.js";

const fixtures = {
  scenarios: JSON.parse(readFileSync("./public/assets/scenarios.json", "utf8")),
  offlineEvaluation: JSON.parse(readFileSync("./public/assets/offline-evaluation.json", "utf8")),
};
let core = createStudioCore(null, fixtures);
let checks = 0;
async function get(path) { return core.dispatch(path, "GET", {}); }
async function post(path, value) { return core.dispatch(path, "POST", value); }
async function rejected(promise, status) {
  await assert.rejects(promise, e => e.status === status);
  checks += 1;
}
function equal(actual, expected) { assert.deepEqual(actual, expected); checks += 1; }

equal((await get("/api/clients")).length, 3);
equal((await get("/api/clients/fintrust-demo")).use_cases.length, 1);
equal((await get("/api/cases/civicdata-policy")).stage_states[1].status, "LOCKED");
await rejected(get("/api/clients/invalid"), 404);
await rejected(get("/api/evaluations/latest"), 404);
equal((await post("/api/evaluations/offline", {})).run_mode, "OFFLINE_DETERMINISTIC");
equal((await get("/api/evaluations/latest")).run_mode, "OFFLINE_DETERMINISTIC");

const noBasis = {
  stage: "DISCOVER", status: "GO", owner: "Fictional reviewer",
  rationale: "Fictional baseline has been reviewed and bounded.",
  evidence_ids: ["e-sim-004"], blockers: [], alternatives: ["Curated policy search"],
};
await rejected(post("/api/cases/civicdata-policy/decisions", noBasis), 409);
await post("/api/evidence/e-sim-004/review", {
  status: "VERIFIED", reviewer: "Fictional reviewer", rationale: "Invented policy source was reviewed only for this synthetic exercise.",
});
const go = await post("/api/cases/civicdata-policy/decisions", noBasis);
equal(go.status, "GO");
equal((await get("/api/cases/civicdata-policy")).stage_states[1].status, "NOT_STARTED");
await post("/api/evidence/e-sim-004/review", {
  status: "REJECTED", reviewer: "Fictional reviewer", rationale: "Fictional version is no longer suitable for the scenario.",
});
const invalidated = await get("/api/cases/civicdata-policy");
equal(invalidated.stage_states[0].status, "REWORK");
equal(invalidated.stage_states[1].status, "LOCKED");
equal(invalidated.decisions.some(d => d.decision_id === go.decision_id), true);
await rejected(post("/api/cases/civicdata-policy/decisions", {
  ...noBasis, stage: "ASSESS", status: "IN_REVIEW",
}), 409);
const added = await post("/api/cases/retailflow-discrepancy/evidence", {
  evidence_class: "DECLARED", source: "Invented scenario interview",
  summary: "Fictional operators described a possible inventory discrepancy.",
});
equal((await get("/api/cases/retailflow-discrepancy")).evidence.some(e => e.evidence_id === added.evidence_id), true);

const snapshot = core.snapshot();
core = createStudioCore(snapshot, fixtures);
equal((await get("/api/cases/civicdata-policy")).stage_states[0].status, "REWORK");
equal((await get("/api/cases/retailflow-discrepancy")).evidence.some(e => e.evidence_id === added.evidence_id), true);
const anotherUser = createStudioCore(null, fixtures);
equal((await anotherUser.dispatch("/api/cases/retailflow-discrepancy", "GET", {})).evidence.some(e => e.evidence_id === added.evidence_id), false);
const report = await get("/api/cases/civicdata-policy/executive-report");
equal(report.includes("REWORK"), true);
equal(report.includes("PRIVATE HOSTED DEMONSTRATION"), true);

const discovery = await post("/api/discovery/assessments", {
  synthetic: true, confirmed_fictional: true,
  client_id: "civicdata-demo", case_id: "civicdata-policy", sector: "Public sector",
  title: "Invented public information helper", risk_tier: "HIGH",
  business_owner: "Fictional sponsor", affected_users: "Fictional service analysts",
  problem: "Fictional teams struggle to locate a current policy citation.",
  current_workflow: "Invented manual policy lookup.", success_metric: "Illustrative answer verification rate",
  expected_benefit: "Unmeasured potential navigation time reduction.",
  non_ai_alternative: "Curated non-AI keyword lookup tool.",
  baseline_status: "UNKNOWN", value_status: "UNKNOWN", alternative_status: "NOT_COMPARED",
  data_permission: "UNKNOWN", data_quality: "UNKNOWN", feasibility: "UNKNOWN",
  adoption_readiness: "UNKNOWN", independent_review: "UNKNOWN", constraints: [],
});
equal(discovery.recommended_state, "DISCOVERY_HOLD");
equal((await get("/api/discovery/assessments")).length, 1);
equal((await get(`/api/discovery/assessments/${discovery.discovery_id}/report`)).includes("30/60/90"), true);

const dimensions = ["BUSINESS_VALUE", "DATA_GOVERNANCE", "SECURITY_PRIVACY", "AI_EVALUATION",
  "ECONOMICS", "HUMAN_OVERSIGHT", "ARCHITECTURE", "OPERATIONS", "COMPLIANCE"];
const assessment = await post("/api/adoption/assessments", {
  synthetic: true, confirmed_fictional: true, client_id: "civicdata-demo",
  case_id: "civicdata-policy", title: "Invented policy impact assessment",
  risk_tier: "HIGH", accountable_owner: "Fictional sponsor",
  non_ai_alternative: "Curated keyword search", blockers: [], evidence: [],
  checks: dimensions.map(dimension => ({dimension, status: "UNKNOWN",
    rationale: "No fictional assessment evidence was gathered.",
    next_action: "Gather fictional documentation.", evidence_ids: []})),
});
equal(assessment.recommended_state, "HOLD");
equal((await get("/api/adoption/assessments")).length, 1);
equal((await get(`/api/adoption/assessments/${assessment.assessment_id}/report`)).includes("HOLD"), true);

await rejected(post("/api/adoption/assessments", {
  ...assessment.scenario, confirmed_fictional: true, client_id: "retailflow-demo",
}), 422);

process.stdout.write(`Hosted Studio core: ${checks} assertions passed.\n`);
