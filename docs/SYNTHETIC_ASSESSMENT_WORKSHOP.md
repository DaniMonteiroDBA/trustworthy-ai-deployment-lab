# Synthetic AI Adoption Assessment Workshop — M4 reference slice

**Status:** implemented for local fictional demonstrations only. This is neither a customer intake portal nor an authenticated review or approval product.

## Purpose and boundary

The workshop lets an architect describe a **new fictional opportunity**, assess decision dimensions, attach **invented** evidence references, add blockers, and obtain a reproducible advisory recommendation. It exercises the same risk-aware `VALIDATE → ADOPT` policy as the four frozen fixtures without altering their input or the Studio's seven-stage simulated human decision history.

The service runs locally at `127.0.0.1`. **It has no login, enterprise tenant authorization, proven reviewer identity, confidentiality controls, data-retention policy, or production security hardening.** The `confirmed_fictional` checkbox is a declaration, not a data-loss-prevention mechanism. Do not paste actual names, employee information, customer documents, proprietary policies, financial figures, tokens, or other sensitive material. Do not deploy this workshop as a public writable service.

## Walkthrough

1. Run the [local Studio](../README.md#run-the-local-ai-value--adoption-studio) and select one of the three demo organizations, or enter an invented client ID ending in `-demo`.
2. Select **New fictional assessment**. Enter a title, a fictional use-case ID prefixed with the client stem (for `acme-demo`, use `acme-policy`), the risk tier, a fictional accountable owner, and a credible non-AI alternative.
3. Examine the eight core criteria: business value, non-AI alternative, data governance, AI evaluation, security/privacy, economics, operations and human accountability. `HIGH` risk includes a ninth independent-review criterion.
4. Each criterion defaults to `UNKNOWN`. Enter an explicit rationale and next action. If choosing `PASS`, supply a fictional evidence source and an appropriate evidence class; marking `SIMULATED_VERIFIED` simulates verification for **code-path testing**, not independent evidence of anything outside this lab. `AI_EVALUATION` and `ECONOMICS` require the invented `MEASURED` class for `PASS` to count in the demo.
5. Add any open blockers and label them `TERMINAL`, `AUTHORIZATION`, or `REMEDIABLE`.
6. Attest that all entries are fictional, save the assessment, and inspect the computed `NO_GO`, `HOLD`, `REWORK`, or `GO` recommendation. Download the deterministic Markdown executive brief if useful for a workshop rehearsal.

The form is a **new input**, not an editor of existing records. Repeating the workflow appends a distinct assessment with a new ID and snapshot. Up to 100 recent assessment summaries are listed locally; older entries are not deleted by that display limit.

## Risk decision semantics

| Input condition | Engine result | Meaning |
| --- | --- | --- |
| Any `FAIL` criterion or open `TERMINAL` blocker | `NO_GO` | Proposed path is unacceptable as stated |
| An `UNKNOWN` required criterion, unsupported `PASS`, or open `AUTHORIZATION` blocker | `HOLD` | Evidence or permission is missing |
| Any `GAP` criterion or open `REMEDIABLE` blocker | `REWORK` | A repair and new assessment are required |
| All mandatory criteria have simulated qualifying `PASS` support and no open blockers | `GO` | **Advisory branch only**, pending an actual decision |

Precedence is `NO_GO > HOLD > REWORK > GO`; there is deliberately **no global maturity score**. Evidence references are local to a single assessment, not reusable authenticated documents. `GO` does not promote a stage or trigger an action.

## Persisted contract and API

| Method | Endpoint | Behavior |
| --- | --- | --- |
| `POST` | `/api/adoption/assessments` | Pydantic-validates synthetic input, evaluates it, and appends a SQLite snapshot; returns `201` |
| `GET` | `/api/adoption/assessments` | Lists up to 100 most recently appended synthetic summaries |
| `GET` | `/api/adoption/assessments/{assessment_id}` | Retrieves an immutable-for-this-demo input/output snapshot |
| `GET` | `/api/adoption/assessments/{assessment_id}/report` | Deterministically renders a text/Markdown executive brief from the stored snapshot |

The `POST` request includes `synthetic: true`, `confirmed_fictional: true`, `title`, `client_id`, `case_id`, `risk_tier`, `accountable_owner`, `non_ai_alternative`, `checks`, `evidence` and `blockers`. Extra properties are rejected at the typed boundary. The server generates a new `scenario_id`; no caller-provided ID can overwrite a snapshot. References to nonexistent evidence fail validation. Real/invalid identifiers, malformed statuses and incomplete required fields return `422`.

SQLite stores the canonical JSON scenario, canonical recommendation, policy version, UTC timestamp and an input SHA-256. The brief includes each dimension, rationale, next action, linked fictional source and explicit integrity metadata. Saving **does not** write to the seven-stage `decisions` or `decision_invalidations` tables. The SHA-256 supports repeatable comparison of a stored input; it is **not** a signature, proof of source authenticity, or tamper-evident audit system against an administrator who can alter SQLite.

The policy output always includes:

```json
{
  "decision_authority": "ADVISORY_ONLY",
  "human_approval": "NOT_RECORDED",
  "release_authorized": false,
  "customer_readiness_verified": false
}
```

For implementation details see [`adoption/engine.py`](../adoption/engine.py), [`adoption/schemas.py`](../adoption/schemas.py), [`adoption/report.py`](../adoption/report.py), [`app/server.py`](../app/server.py), and [`tests/test_custom_adoption_workshop.py`](../tests/test_custom_adoption_workshop.py).

## Acceptance evidence and next boundary

Automated tests exercise deterministic policy states, storage append behavior, independent GET snapshots, SHA-256 provenance, malformed input rejection, missing/unverified support, distinct separation from human stage decisions, and Markdown-report safety. Run:

```bash
python -m unittest discover -s tests -q
node --check studio/app.js
```

Before any authorized business pilot, separately design: authenticated identities and roles; real organizational tenancy and authorization checks; data minimization and retention; independently verified and signed evidence; calibrated risk criteria and sector obligations; human approvals; approved price/budget inputs; operational monitoring and rollback; independent reviewer adjudication; and a private customer deployment. Those capabilities remain **out of scope and unverified** here.
