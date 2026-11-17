# Trustworthy AI Deployment Lab — Scope v1.1

**Status:** design baseline; implementation and customer validation have not been completed.  
**Owner:** Dani Monteiro  
**Primary goal:** demonstrate a reusable method for taking enterprise AI opportunities from discovery through evidence-based deployment and measurable adoption.

## Product thesis

Enterprise AI adoption is not a model-selection problem alone. A defensible investment decision requires a business owner, an explicit alternative to AI, trustworthy data, an architecture, a risk decision, an evaluation baseline, an operating model, and an adoption plan.

The lab will connect three components:

1. **Trusted AI Adoption Framework:** reusable consulting method and decision gates.
2. **AI Architecture & Evaluation Lab:** one working technical reference case with API, retrieval, tools, tests, security boundaries, and reproducible evaluations.
3. **AI Value & Adoption Studio:** planned client-portfolio application to track discovery, priorities, architecture decisions, proof of value, readiness, adoption, and outcomes.

The framework is designed to be **vendor-neutral**. The public reference implementation may use OpenAI products to demonstrate applied AI skills; it will not imply that every client should choose those products.

## Users and responsibilities

| Persona | Decision responsibility | Expected use |
| --- | --- | --- |
| Business sponsor | Confirms problem, benefits, funding, and success definition | Reviews opportunity, value case, and adoption results |
| AI / solutions architect | Owns technical strategy and recommendation | Leads discovery, compares architectures, records trade-offs |
| Engineering / delivery lead | Owns implementation and technical handoff | Plans delivery and verifies engineering artifacts |
| Security / privacy lead | Reviews risk, access, and data-processing design | Records controls, blockers, and residual risks |
| Operational owner | Owns operation after release | Accepts monitoring, incident, rollback, and support arrangements |
| End-user champion | Represents affected users | Validates usability, training, and adoption barriers |

These are reference roles, not assertions about Kaspper's approved organization.

## Reference client portfolio

All three reference organizations and all associated stakeholders, documents, and business data are **fictional and synthetic**.

| Account | Sector | Reference problem | Scope of demonstration |
| --- | --- | --- | --- |
| FinTrust | Financial services | Policy interpretation and requests requiring approval | Full seven-stage method **and** deep technical runtime |
| RetailFlow | Retail | Investigating operational discrepancies and proposing corrections | Discovery, prioritization, architecture, and adoption plan |
| CivicData | Public sector | Policy-based service questions with insufficient or conflicting evidence | Discovery, risk profile, evaluation design, and technical account plan |

## Seven-stage decision journey

See [the methodology](docs/METHODOLOGY.md) for exact inputs, evidence requirements, and stop conditions.

1. **Discover:** Is there a business problem worth solving?
2. **Assess:** Are the organization, data, and controls ready enough for the proposed context?
3. **Prioritize:** Is this use case preferable to other opportunities or a non-AI alternative?
4. **Architect:** Is the chosen solution fit for purpose under its constraints?
5. **Validate:** Does a bounded proof of value demonstrate the required quality, risk, and economics?
6. **Adopt:** Are people, operations, and responsibilities prepared to use it safely?
7. **Measure & Improve:** Is value actually being sustained, and what should change?

Every stage ends with a recorded **GO**, **REWORK**, **HOLD**, or **NO_GO** decision and named human owner. These are local methodology states, not a certification of legal compliance or enterprise readiness.

## Core product capabilities — planned

### Adoption Studio

- Separate fictional client portfolios, use cases, stakeholders, decisions, and tasks.
- Configurable sector and use-case profiles instead of a single universal maturity score.
- Discovery interview records, evidence links, current/target gaps, and prioritized opportunities.
- Architecture alternatives, ADRs, risks, owners, dependencies, and implementation handoffs.
- Proof-of-value criteria and measured results with explicit baseline provenance.
- Adoption plans, training, usage metrics, blockers, and executive reporting.
- Tenant-scoped authorization and auditable review decisions.

### Technical reference runtime

- A runnable **Enterprise Policy & Action Assistant** with synthetic policy documents.
- Grounded answers, evidence identification, clarification, and abstention.
- Structured outputs and least-privilege tool integrations.
- App-enforced identity, tenant isolation, authorization, and human approval for sensitive actions.
- Reproducible evaluation runs covering correctness, groundedness, abstention, tool behavior, security, latency, and cost.
- CI checks, release decisions, monitoring, and a documented rollback procedure.

### Product adoption playbooks

- Real OpenAI API integration in the technical reference runtime.
- Documented adoption scenarios for ChatGPT Enterprise and Codex; **no claim of actual enterprise deployment** without verified access and evidence.
- An agentic workflow with authorization, human review, and evaluation.
- Business/technical executive briefings, implementation handoff, and adoption roadmap.

## Decision and evidence contract

Each recommendation must identify the claim, the evidence supporting it, confidence/limitations, alternatives, decision owner, and next review date. A model suggestion or a stakeholder assertion cannot silently become a verified measurement.

Evidence classes are `DECLARED`, `DOCUMENTED`, `MEASURED`, and `INFERRED`. Verification status is tracked **separately** from class. The full rules and schema are in [the decision contract](docs/DECISION_CONTRACT.md).

## Explicit exclusions

- Real company or client data without a separate authorized engagement.
- Claims of certification, production compliance, customer ROI, or completed implementation based on a demo.
- Universal readiness percentages that obscure severe security or evidence gaps.
- Automatic approvals of business-critical actions based only on model output.
- A full commercial multi-tenant SaaS before method validation.
- Any implication of endorsement by OpenAI, NIST, Microsoft, or Kaspper.

## Public/private boundary

This repository is an **independent public reference**. A potential Kaspper pilot is only an **unapproved proposal** at this stage. A corporate extension would require written agreement on scope, IP rights, permission to reuse public components, data handling, environments, costs, and any case-study publication. No confidential material is to be uploaded here.

## Milestones and acceptance criteria

| Milestone | Planned output | Evidence needed for completion |
| --- | --- | --- |
| **M0 — Define** | Method, decision contract, synthetic portfolio, job traceability, ordered backlog | Reviewed docs, valid example records, reproducible contract checks |
| **M1 — Demonstrate** | Adoption Studio minimum vertical slice + reference API | Executable walkthrough of one synthetic client and automated API tests |
| **M2 — Verify** | Evals, risk controls, and CI release gates | Versioned cases, repeatable execution, published failures and results |
| **M3 — Adopt** | Adoption dashboards and technical account plans | Synthetic adoption scenario explicitly marked simulated; actual telemetry marked measured |
| **M4 — Share** | Public demo, deployment guide, executive and technical walkthroughs | Accessible deployment, runbook, limitations, handoff, verified link and presentation |

Completion dates, quality figures, and adoption outcomes will be recorded only when supported by observed evidence.

## Working definition of done

- [ ] One synthetic account completed through all seven stages with stage decisions and evidence.
- [ ] Two additional clients show configurable cross-sector profiles.
- [ ] One technical use case runs locally and demonstrates bounded tool use.
- [ ] Security and tenant boundaries are tested, not merely documented.
- [ ] Evaluation data, baselines, and results are versioned and reproducible.
- [ ] A real integration produces **measured** quality, latency, and cost records.
- [ ] The studio provides a traceable executive recommendation and account plan.
- [ ] Adoption measures distinguish demonstration data from actual telemetry.
- [ ] A deployment can be verified, monitored, and rolled back.
- [ ] The README and CV claim only artifacts actually demonstrated.

## References

- [OpenAI — Applied AI Architect (Brazil)](https://openai.com/careers/applied-ai-architect-%28brazil%29-sao-paulo/)
- [NIST AI Risk Management Framework](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)
- [NIST AI RMF Profiles](https://airc.nist.gov/airmf-resources/airmf/6-sec-profile/)

This project is informed by these sources, but is **not** an official implementation of their requirements.
