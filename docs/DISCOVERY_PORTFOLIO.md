# AI Adoption Discovery & Portfolio Triage — M5 reference slice

**Status:** implemented as a **local, synthetic-only consultation rehearsal**. Neither a commercial client diagnostic nor a verified readiness assessment. This procedure precedes the separate [validation-to-adoption policy](ADOPTION_DECISION_ENGINE.md).

## Purpose: discovery before proposing a solution

The same questions can structure an early interview in a fictional financial, retail or public-service opportunity:

1. **Why now?** Who owns the business problem, which users experience it, and what is the current workflow?
2. **How will success be established?** What measure and population would be compared to the existing process? Is a baseline actually available?
3. **Why AI?** Which credible non-AI alternative would solve the problem more simply? Was that alternative compared?
4. **May data be used?** Who owns the sources, what restrictions exist, and is there attributable permission?
5. **Can it work and be operated?** What data-fitness, integration, feasibility, workforce and enablement gaps remain?
6. **Who challenges the decision?** High-risk opportunities require an independent-review *plan*, even for fictional shortlisting. A plan is not an actual review.

The form collects a problem, current workflow, fictional sponsor/users, success measure, expected benefit **hypothesis**, non-AI comparator, and categorical statuses for baseline, value, comparison, data permission, data fitness, feasibility, adoption and independent review. Fictional source descriptions are required to support simulated baseline, comparator and permission claims. Input fields do **not** upload real documents.

## Triage, without a magic score

| Advisory bucket | Trigger | Proposed action |
| --- | --- | --- |
| `DO_NOT_PURSUE` | Denied data permission, unusable data, blocked feasibility, or unsupported value | Stop this proposed path; examine a safe or non-AI option |
| `DISCOVERY_HOLD` | Unknown or restricted permission, unknown data fitness/feasibility/value, absent baseline/comparator source, unknown adoption owner, or missing high-risk review plan | Gather missing evidence and reassess; do not start a pilot |
| `REFINE_SCOPE` | Correctable data, feasibility or adoption gap without a higher-priority issue | Repair scope and explicitly reassess |
| `SHORTLIST_FOR_POV` | All required **fictional** discovery conditions have appropriate simulated support | Candidate for **human discussion of a bounded proof-of-value proposal only** |

Policy precedence: `DO_NOT_PURSUE > DISCOVERY_HOLD > REFINE_SCOPE > SHORTLIST_FOR_POV`. The engine sorts reasons by severity and criterion. No numerical ROI, percentage maturity, business-value measurement, or cross-sector ranking is calculated. Two shortlisted use cases are **not automatically ranked** against each other: a real decision maker must compare resource availability, constraints, expected value and risk using verified evidence.

`GRANTED_SIMULATED`, `SIMULATED_MEASURED`, `PLAUSIBLE_SIMULATED` and analogous statuses are intentionally **fictional code-path inputs**. They cannot establish real consent, data quality, financial impact or operational readiness.

## Conditional 30 / 60 / 90-day plan

Every saved discovery produces a deterministic Markdown brief and a three-window proposed plan. These are **relative windows**, not booked dates or delivery commitments.

| Window | Focus | What changes with the evidence |
| --- | --- | --- |
| Days 01–30 | Discover and qualify | Define sponsor and success metric, compare current/non-AI process, identify baseline/data authority; include remediation when recorded gaps exist |
| Days 31–60 | Conditional design or repair | If blocked: stop/reframe. If on hold: collect evidence. If eligible: propose an evaluation with acceptance criteria and independent review |
| Days 61–90 | Accountable decision and handoff | Review findings with authorized humans; prepare operations, change and rollback *only if* separately authorized |

**No plan action executes automatically.** In particular, there is no API call that authorizes a paid model request, access to a customer's records, a purchase, or a deployment.

## Local Studio and repeatability

Run the Studio as described in [README](../README.md#run-the-local-ai-value--adoption-studio). Open **New discovery**. The form starts from the selected fictional case but accepts new client IDs ending in `-demo` and matching `case_id` prefixes. Unknown conditions are the safe defaults. Confirm invented-only input before saving.

| Method | Local endpoint | Result |
| --- | --- | --- |
| `POST` | `/api/discovery/assessments` | Strict Pydantic input validation, deterministic policy and new SQLite snapshot (`201`) |
| `GET` | `/api/discovery/assessments` | Up to 200 latest snapshots in descending insertion order |
| `GET` | `/api/discovery/assessments/{id}` | Exact immutable-through-API input and recommendation |
| `GET` | `/api/discovery/assessments/{id}/report` | Deterministic text/Markdown executive brief and conditional roadmap |

The portfolio board displays the **latest** snapshot for each fictional client/use-case pair, grouped into four explanatory categories. Previous snapshots remain in SQLite for audit comparison (up to 200 are exposed by the list endpoint). Each saved input is canonically JSON-serialized and fingerprinted with SHA-256. This fingerprint is not a signature or tamper-proof ledger: local DB administrators can edit files.

The table and API remain separate from:

- the seven-stage, unauthenticated **simulated human decisions**;
- the M3 **fixed adoption fixtures**;
- the M4 **validation-to-adoption custom assessments**.

Outputs always include `decision_authority: ADVISORY_ONLY`, `human_approval: NOT_RECORDED`, `pov_authorized: false`, `release_authorized: false`, and `customer_readiness_verified: false`. An early shortlist can never become a final production `GO`.

## Human roles for an authorized future engagement

| Role | What must be independently established outside this lab |
| --- | --- |
| Business sponsor | Materiality, real baseline, funding, expected return, success acceptance |
| Process/users representative | Existing workflow, user burden, accessibility, change concerns |
| Data owner | Provenance, permitted purpose, quality, retention, intellectual-property and privacy rights |
| Security/privacy lead | Risk profile, controls, jurisdictional obligations, third-party processing |
| AI/solutions architect | Alternative designs, feasibility, limitations and evidence gaps |
| Delivery/operations owner | Skills, dependencies, evaluation, incidents, rollback, ongoing cost |
| Independent reviewer (risk-dependent) | Critical challenge and recorded disagreement before authorized next step |

## Security and readiness limitations

The local app has **no authentication, organization-scoped authorization, protected evidence storage, DLP, retention policy, secure upload, identity verification, legal validation, budget enforcement or deployed operational controls**. The fictional checkbox cannot detect confidential text. Never paste customer records or use it as a public intake endpoint. A possible Kaspper application must be handled as a **separate authorized private engagement** after confirming sponsor, scope, confidential-data rules and IP/reuse rights; this public repository does not claim corporate endorsement.

## Evidence and tests

See [`discovery/engine.py`](../discovery/engine.py), [`discovery/schemas.py`](../discovery/schemas.py), [`discovery/report.py`](../discovery/report.py), and [`tests/test_discovery_portfolio.py`](../tests/test_discovery_portfolio.py). Automated checks cover each terminal/hold/shortlist condition, high-risk review, foreign-tenant case rejection, strict synthetic input, append-only persistence, non-approval state, report provenance, and the served form. The test suite does **not** establish real-world method validity.
