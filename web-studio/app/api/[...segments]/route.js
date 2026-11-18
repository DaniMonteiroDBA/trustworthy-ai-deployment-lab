import { eq, desc } from "drizzle-orm";
import { getDb } from "../../../db";
import { studioSnapshots } from "../../../db/schema";
import { getChatGPTUser } from "../../chatgpt-auth";
import { createStudioCore } from "../../../lib/studio-core";
import scenarios from "../../../public/assets/scenarios.json";
import offlineEvaluation from "../../../public/assets/offline-evaluation.json";

export const dynamic = "force-dynamic";

const fixtures = Object.freeze({ scenarios, offlineEvaluation });
const NO_STORE = { "Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff" };

function respond(data, status = 200) {
  const plain = typeof data === "string";
  return new Response(plain ? data : JSON.stringify(data), {
    status,
    headers: {
      ...NO_STORE,
      "Content-Type": plain ? "text/plain; charset=utf-8" : "application/json; charset=utf-8",
    },
  });
}

function error(status, detail) {
  return respond({ detail }, status);
}

function boundedText(value, min, max) {
  return typeof value === "string" && value.trim().length >= min && value.length <= max;
}

function stringList(value, limit) {
  return Array.isArray(value) && value.length <= limit && value.every(x => boundedText(x, 1, 400));
}

function validateWrite(path, payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return "JSON object required.";
  if (/^\/api\/cases\/[^/]+\/evidence$/.test(path)) {
    if (!["DECLARED", "DOCUMENTED", "INFERRED"].includes(payload.evidence_class) ||
        !boundedText(payload.source, 4, 240) || !boundedText(payload.summary, 12, 2000))
      return "Provide a valid fictional evidence class, source and summary.";
  } else if (/^\/api\/evidence\/[^/]+\/review$/.test(path)) {
    if (!["VERIFIED", "REJECTED"].includes(payload.status) ||
        !boundedText(payload.reviewer, 3, 120) || !boundedText(payload.rationale, 10, 1000))
      return "Provide a valid evidence review and rationale.";
  } else if (/^\/api\/cases\/[^/]+\/decisions$/.test(path)) {
    if (!["DISCOVER", "ASSESS", "PRIORITIZE", "ARCHITECT", "VALIDATE", "ADOPT", "MEASURE_IMPROVE"].includes(payload.stage) ||
        !["IN_REVIEW", "GO", "REWORK", "HOLD", "NO_GO"].includes(payload.status) ||
        !boundedText(payload.owner, 3, 120) || !boundedText(payload.rationale, 12, 2000) ||
        !stringList(payload.evidence_ids, 50) || !stringList(payload.blockers, 30) ||
        !stringList(payload.alternatives, 30))
      return "Provide a valid stage review, evidence references and rationale.";
  } else if (path === "/api/adoption/assessments") {
    if (payload.synthetic !== true || payload.confirmed_fictional !== true ||
        !boundedText(payload.title, 5, 180) || !Array.isArray(payload.checks) ||
        !Array.isArray(payload.evidence) || !Array.isArray(payload.blockers) ||
        payload.checks.length > 10 || payload.evidence.length > 50 || payload.blockers.length > 25)
      return "Only bounded, explicitly fictional assessments are accepted.";
  } else if (path === "/api/discovery/assessments") {
    if (payload.synthetic !== true || payload.confirmed_fictional !== true ||
        !boundedText(payload.title, 5, 180) || !boundedText(payload.problem, 20, 1500) ||
        !boundedText(payload.non_ai_alternative, 12, 700))
      return "Only bounded, explicitly fictional discovery records are accepted.";
  }
  return null;
}

async function processApi(request, method) {
  const user = await getChatGPTUser();
  if (!user) return error(401, "Sign in with ChatGPT to access this private Studio.");

  const pathname = new URL(request.url).pathname;
  if (method === "POST") {
    const origin = request.headers.get("origin");
    if (origin && origin !== new URL(request.url).origin) return error(403, "Cross-origin writes are not allowed.");
    if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/json"))
      return error(415, "JSON content type required.");
  }

  let db;
  try { db = getDb(); }
  catch (e) { return error(503, "The hosted Studio database is unavailable."); }

  let latest;
  try {
    const rows = await db.select().from(studioSnapshots)
      .where(eq(studioSnapshots.userId, user.userId))
      .orderBy(desc(studioSnapshots.revision)).limit(1);
    latest = rows[0] || null;
  } catch (_) { return error(503, "The Studio database schema is not ready."); }

  let payload = {};
  if (method === "POST") {
    const raw = await request.text();
    if (raw.length > 65_536) return error(413, "This fictional request exceeds the size limit.");
    try { payload = JSON.parse(raw); }
    catch (_) { return error(400, "Invalid JSON request."); }
    const validation = validateWrite(pathname, payload);
    if (validation) return error(422, validation);
    if (latest && latest.revision >= 1000)
      return error(409, "The private demo has reached its 1,000-version safety limit.");
  }

  let core;
  try {
    core = createStudioCore(latest ? JSON.parse(latest.stateJson) : null, fixtures);
    const data = await core.dispatch(pathname, method, payload);
    if (method !== "POST") return respond(data);

    const nextRevision = (latest?.revision || 0) + 1;
    await db.insert(studioSnapshots).values({
      userId: user.userId,
      revision: nextRevision,
      actorId: user.userId,
      action: `${method} ${pathname}`.slice(0, 220),
      stateJson: JSON.stringify(core.snapshot()),
      createdAt: new Date().toISOString(),
    });
    return respond(data, 201);
  } catch (e) {
    if (e?.status && Number.isInteger(e.status)) return error(e.status, e.message);
    const msg = String(e?.message || "");
    if (/UNIQUE constraint failed|SQLITE_CONSTRAINT_UNIQUE|constraint failed/i.test(msg))
      return error(409, "A concurrent update was saved. Refresh the case before recording a new decision.");
    return error(500, "The synthetic Studio request could not be completed.");
  }
}

export async function GET(request) { return processApi(request, "GET"); }
export async function POST(request) { return processApi(request, "POST"); }
