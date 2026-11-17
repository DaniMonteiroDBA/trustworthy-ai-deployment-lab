# Delivery Backlog — phased, evidence-first

**Scope baseline:** [SCOPE.md](SCOPE.md) · [Methodology](docs/METHODOLOGY.md) · [Traceability](REQUIREMENTS_TRACEABILITY.md).

Backlog items are planned until their acceptance evidence is linked. No completion dates or velocity have been claimed.

## P0 — Method and contract (first milestone)

**Goal:** a testable, reviewable methodology baseline, not a polished sales deck.

- [x] Document seven decision gates, evidence types, and escalation rules.
- [x] Define the proposed scope and public/private boundary.
- [x] Map OpenAI role requirements to proof artifacts.
- [x] Create a synthetic discovery decision record.
- [ ] Run and link contract validation evidence; add negative scenarios.
- [ ] Review the initial method with at least one human stakeholder and record changes.

**Acceptance:** the synthetic example is machine-checked; a reviewer can identify every decision, underlying evidence and unresolved blocker.

## P1 — One end-to-end client journey

- [ ] Complete FinTrust's seven stages using **synthetic** documents and explicit review decisions.
- [x] Seed three synthetic organizations and reference use-case profiles for FinTrust, RetailFlow and CivicData.
- [x] Build the first local Adoption Studio: client, case, evidence, decision, blockers and status.
- [x] Implement an append-only decision history, review records and stage unlock rules.
- [x] Generate deterministic synthetic executive opportunity briefs.
- [ ] Add role-based access design, privacy inventory and threat boundaries.
- [ ] Produce the complete technical account plan and interview templates.

**Acceptance:** a demo user can follow a fictional opportunity from discovery through planned rollout without invented metrics, hidden evidence, or unowned gates.

## P2 — Technical runtime and reproducibility

- [ ] Implement synthetic tenant-scoped documents and a FastAPI backend.
- [ ] Integrate OpenAI API with explicit timeouts, bounded retries and safe logging.
- [ ] Build grounded answer, missing-evidence abstention and structured output flows.
- [ ] Implement proposed actions with allowlisted tools and human authorization.
- [ ] Test tenant separation, malformed inputs and failed external calls.

**Acceptance:** a local testable API handles valid, unsupported, and unauthorized scenarios; all claimable behavior is covered by tests.

## P3 — Evaluation, risk and operations

- [x] Define versioned **proposed** evaluation cases; independent human criteria review remains pending.
- [x] Benchmark simple non-AI search against an **offline deterministic** safety-rules candidate; this is not an AI model benchmark.
- [x] Execute synthetic adversarial cases for prompt injection, cross-tenant access and unauthorized action.
- [ ] Measure live AI task quality and approved cost; offline runtime/heuristic scores and version provenance are implemented.
- [ ] Add GitHub Actions quality and security checks with release blockers.
- [ ] Document production-readiness gaps, rollback procedure and incident responsibilities.

**Acceptance:** at least one reproducible evaluation run includes failures and limitations; critical authorization regressions block release.

**Current evidence:** `python -m evals.run` creates a local, versioned offline artifact; the Studio exposes the same synthetic run. The OpenAI Responses adapter has a mocked test and is never called by default. CI runner allocation is tracked in [issue #6](https://github.com/DaniMonteiroDBA/trustworthy-ai-deployment-lab/issues/6).

## P4 — Adoption and external demonstration

- [ ] Add synthetic account portfolio and adoption progress views.
- [ ] Develop ChatGPT Enterprise and Codex adoption playbooks without false deployment claims.
- [ ] Create a decision-ready executive report and implementation handoff.
- [ ] Deploy a public synthetic-data demo and verify HTTPS and domain availability.
- [ ] Record a five-minute executive and fifteen-minute engineering walkthrough in English.
- [ ] Update the README and CV only with verified, observed capabilities.

**Acceptance:** visitors can reproduce the reference case or review evidence; all public claims have explicit status.

## Proposed Kaspper pilot — separate approval track

**Status: PROPOSED / NOT AUTHORIZED.** First confirm sponsorship, actual customer need, project scope, confidentiality, data permissions, IP/reuse terms and budget. Prefer one bounded diagnostic/proof of value using approved customer material or synthetic stand-ins. No corporate records or production integration belong in this public repository.

## Prioritization rule

Any change that improves traceability, evidence quality, authorization, or honest reporting outranks decorative dashboards. A single completed technical vertical slice is preferable to multiple mockups claiming enterprise adoption.
