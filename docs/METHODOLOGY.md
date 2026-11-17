# Trusted AI Adoption Framework — Method v0.1

**Maturity:** proposed and not yet validated with a real client.  
**Application:** repeatable enterprise AI advisory, including the choice **not to use AI**.  
**Principle:** a decision must not claim more certainty than its evidence supports.

## Workflow and decision gates

| ID | Stage | Decision question | Minimum evidence expected | Output | Hold / no-go examples |
| --- | --- | --- | --- | --- | --- |
| D1 | Discover | Is the problem material, owned, and measurable? | Named sponsor; process description; baseline metric definition or explicit baseline gap | Discovery brief and success hypothesis | No business owner, no identified process, problem undefined |
| D2 | Assess | Are data, capabilities, and controls sufficient for an evaluation? | Data inventory and permissions; known limitations; security/privacy reviewer for sensitive cases | Current/target profile and risk register | Unauthorized data source, unknown legal basis, unacceptable exposure |
| D3 | Prioritize | Does this opportunity merit investment relative to alternatives? | Value hypothesis; implementation effort; dependency map; **non-AI baseline**; risk assumptions | Use-case portfolio and ranking rationale | No credible value hypothesis, cheaper simpler alternative not considered |
| D4 | Architect | Is the proposed design appropriate and operable? | Options and ADRs; identity/access model; integration, evaluation and operating plans | Architecture blueprint and implementation handoff | Uncontrolled tool permissions, no owner for critical integration |
| D5 | Validate | Did the proof of value meet predefined acceptance criteria? | Versioned test cases; baseline comparison; quality, safety, cost and latency observations; limitations | PoV report and human go/no-go decision | Critical auth leak, harmful action, unmeasured success claims |
| D6 | Adopt | Can people use and support it responsibly? | Training/adoption plan; operational owner; monitoring; rollback; support and escalation | Adoption roadmap and readiness record | No incident or rollback owner; users not enabled for material workflow |
| D7 | Measure & Improve | Is value sustained after launch? | Usage telemetry, outcome baseline and comparison, feedback, incident trends, review cadence | Executive value report and iteration backlog | No reliable impact data; unresolved critical production risk |

Evidence is **contextual**: a simple internal draft assistant and a financial decision agent will not have identical review depth or thresholds. Mandatory blockers are stated explicitly; an average score cannot cancel a critical safety failure.

## Human decision states

- `GO`: the accountable owner authorizes the next bounded stage based on documented evidence.
- `REWORK`: a specific missing or failed criterion can be addressed; do not advance before re-review.
- `HOLD`: a dependency or authorization is pending; work stops at the relevant boundary.
- `NO_GO`: the proposed path should not proceed; record alternative and reason.

Model outputs may recommend a state, but **only a designated human owner** records the authoritative decision.

**Executable reference slice:** the [Adoption Decision Engine](ADOPTION_DECISION_ENGINE.md) now recommends one of these states for the `VALIDATE → ADOPT` transition using eight evidence dimensions, an additional independent-review criterion for high-risk cases, and explicit blocker precedence. Its four example results are synthetic and **cannot become authorized stage approvals**. The other stage-transition policies remain conceptual.

**Earlier-stage reference slice:** [AI Discovery & Portfolio Triage](DISCOVERY_PORTFOLIO.md) structures a fictional business interview and returns one of four **non-authoritative investigation buckets** (`SHORTLIST_FOR_POV`, `REFINE_SCOPE`, `DISCOVERY_HOLD`, `DO_NOT_PURSUE`) plus a conditional 30/60/90-day plan. These are **not** authoritative seven-stage gate states, measurable cross-client rankings or permissions to begin a pilot.

## Evidence strength and provenance

Do not equate evidence type with truth:

- `DECLARED`: stakeholder statement or assumption; attributable, but not independently verified.
- `DOCUMENTED`: referenced artifact, policy, contract, system record, or design; provenance and applicability still need review.
- `MEASURED`: a reproducible observation with collection method, dataset/context, timestamp, and configuration.
- `INFERRED`: synthesis or hypothesis produced by an AI model or analyst; never automatically promoted to verified fact.

Each evidence item has a distinct `verification_status`: `UNVERIFIED`, `VERIFIED`, or `REJECTED`. A claim with only inferred or unverified evidence must be marked as uncertain and cannot independently satisfy a release gate.

## Minimum assessments by dimension

1. **Business value:** baseline, expected outcome, sponsor, alternatives, adoption incentives.
2. **Data fitness:** source authority, access, freshness, completeness, provenance, retention.
3. **Solution fitness:** model suitability, integration, failure behavior, operating cost.
4. **Trust and risk:** security, privacy, misuse, prompt injection, adverse impacts.
5. **Delivery readiness:** skills, ownership, testing, monitoring, rollback, deployment path.
6. **Adoption readiness:** workflow change, training, accessibility, user feedback, communication.

Use sector/use-case profiles to choose checks and approval requirements. **Do not** calculate one global readiness score or promise cross-industry comparability without validated weighting and calibration.

## Deliverable package per case

```text
case-id/
  discovery-brief.md
  current-target-profile.md
  opportunity-portfolio.md
  architecture-decisions.md
  evaluation-plan.md
  pov-results.md
  production-readiness.md
  adoption-roadmap.md
  executive-value-report.md
  decision-log.json
```

These names denote **planned templates**; generating them does not imply a real client delivery. Outputs should be dated, versioned, and linked to evidence. A proof-of-value report is marked `NOT_RUN` until evaluations actually execute.

## Implementation rules for the future Studio

1. Client scope is defined in application authorization, never inferred from model text.
2. Every field records whether its origin is a person, document, measurement, or AI inference.
3. Recommendations link to explicit evidence IDs, business owner, and alternatives.
4. Missing evidence stays missing. AI may ask questions or abstain; it must not fabricate documents or results.
5. Critical security, privacy, or authorization blockers are separate from optional improvement scores.
6. A reviewer can override a recommendation with an attributable rationale; the override is auditable.
7. A report never labels synthetic customer metrics as measured business outcomes.

## Validation strategy

Start with one synthetic full journey (FinTrust), then adapt the same stage contracts to RetailFlow and CivicData. Compare process completeness, reviewer understanding, time to decision, and false assumptions. Only after obtaining permission and clear IP/privacy arrangements should a real Kaspper engagement be considered.

## Source alignment

The NIST AI RMF `GOVERN`, `MAP`, `MEASURE`, and `MANAGE` functions inform risk-oriented stages. This framework adds commercial discovery, architecture selection, value demonstration, and sustained adoption; it does not claim NIST certification or endorsement.

Sources: [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) · [NIST Profiles](https://airc.nist.gov/airmf-resources/airmf/6-sec-profile/)
