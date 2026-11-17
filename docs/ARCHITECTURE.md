# AI Value & Adoption Studio — M1 Architecture

**Status:** local synthetic demonstration implemented; cloud deployment, authentication, enterprise tenant isolation, OpenAI integration, and production security controls are **not implemented**.

## Architecture boundary

```mermaid
flowchart TD
    B["Browser · Static Studio"] --> API["FastAPI · Synthetic API"]
    API --> DB["SQLite · Local demo records"]
    API --> RULES["Human decision / evidence rules"]
    RULES --> DB
    API --> REPORT["Deterministic executive Markdown"]
```

The frontend is static HTML/CSS/JavaScript. It uses same-origin calls to a FastAPI service. Each API request opens its own SQLite connection with parameterized queries and foreign-key constraints. The first initialization seeds three fictional organizations.

## Implemented API (local, non-production)

| Method | Endpoint | Behavior |
| --- | --- | --- |
| GET | `/api/health` | Explicitly identifies synthetic local mode |
| GET | `/api/clients` | Lists three fictional accounts |
| GET | `/api/clients/{client_id}` | Account and use-case portfolio |
| GET | `/api/cases/{case_id}` | Evidence, decision history and effective stage states |
| POST | `/api/cases/{case_id}/evidence` | Records unverified synthetic evidence; refuses manual `MEASURED` claims |
| POST | `/api/evidence/{evidence_id}/review` | Appends a simulated review with self-entered reviewer name |
| POST | `/api/cases/{case_id}/decisions` | Records gate outcome after consistency checks |
| GET | `/api/cases/{case_id}/executive-report` | Generates deterministic synthetic brief without fabricating metrics |

## Stage state and history

The stage order is `DISCOVER`, `ASSESS`, `PRIORITIZE`, `ARCHITECT`, `VALIDATE`, `ADOPT`, `MEASURE_IMPROVE`.

- A stage is unlocked only when all preceding gates have an effective `GO`.
- Review decisions are appended; prior records remain visible in `decisions` history.
- Rejecting cited evidence appends a durable `decision_invalidations` record for each affected `GO`. Even if evidence is later verified again, the recorded approval cannot silently reactivate: a new human review must be entered. Effective status becomes `REWORK` while the original `GO` remains in audit history.
- If an earlier stage loses `GO`, downstream stage approvals are **effectively locked** until the dependency is restored.
- A `GO` cannot cite evidence from another use case, bypass unresolved blockers, or rely solely on unverified/inferred material.
- `VALIDATE` and `MEASURE_IMPROVE` cannot receive `GO` until actual measured evidence is ingested by a future trusted integration.

The current code implements **application-level workflow checks**, not legal authority, technical accreditation, or identity-based authorization.

## Important risk boundaries

1. **No real authentication or identity verification.** Reviewer names are self-entered. Do not treat `GO` as a real organizational signoff.
2. **No enterprise tenant authorization.** The API exposes three public fictional accounts. Query filters by case ID prevent accidental cross-case evidence references, but do not protect real tenants.
3. **No real client or confidential data.** The demo server may accept arbitrary user-supplied text. Run locally with fictional content only and never publish it as a production service.
4. **No measured AI outcomes.** The only automated tests so far check workflow and contract behavior, not model output quality.
5. **No cloud release or data-retention process.** SQLite persists locally at `data/studio.db` and is excluded from Git.

## Planned architecture progression

- **M1 next:** review business schema and programmatic case templates; evaluate usability with a real human reviewer using only fictional data.
- **M2:** OpenAI model gateway, tenant-scoped retrieval, action approval machine, actual authenticated users and strict tenant authorization.
- **M3:** versioned eval runner, measured evidence ingestion, threat model, safe telemetry, repeatable release gates.
- **M4:** real deployment architecture, privacy and retention decisions, synthetic account analytics, operational readiness and handoff.

See [SCOPE](../SCOPE.md), [Decision Contract](DECISION_CONTRACT.md), and [traceability](../REQUIREMENTS_TRACEABILITY.md).
