# Applied AI Architect — Requirements Traceability

**Source:** [OpenAI Applied AI Architect (Brazil)](https://openai.com/careers/applied-ai-architect-%28brazil%29-sao-paulo/).  
**Purpose:** document what the independent lab can demonstrate. **It is not a claim that any feature is implemented or that the author has accomplished client outcomes via this lab.**

**Status key:** `DESIGNED` = documented proposal; `PLANNED` = not yet designed in detail; `IMPLEMENTED` = code and runnable demo observed; `VERIFIED` = test or other supporting evidence available. Status should advance only after review.

| ID | OpenAI role responsibility / capability | Lab artifact or functionality | Required evidence before claim | Status |
| --- | --- | --- | --- | --- |
| R01 | Own technical strategy for client portfolio | Synthetic multi-account case list and technical account plans | Three account plans with sponsors, use cases, risks, milestones and adoption paths | DESIGNED |
| R02 | Executive and technical discovery | Discover/Assess interviews and current/target profile | Versioned briefs with decisions, constraints, and owners | DESIGNED |
| R03 | Prioritize use cases by business value | Prioritization portfolio with non-AI alternative | Comparison criteria, assumptions, rationale and human decision | DESIGNED |
| R04 | Design applied AI architecture end-to-end | Architecture blueprints, ADRs, controls and handoff | Diagram, tradeoffs, integration, identity, cost and resilience decisions | PLANNED |
| R05 | Demonstrate APIs/SDKs and coding fluency | FastAPI local Studio; opt-in OpenAI Responses adapter and Pydantic structured output | API integration test with mocked SDK in `tests/test_evaluation_factory.py`; live model call still pending | IMPLEMENTED |
| R06 | Evaluate models, RAG and agentic workflows | Versioned synthetic dataset, baseline search, deterministic candidate, abstention/citation/adversarial grader | Local `python -m evals.run` and tests are reproducible; **real model, RAG and agentic evaluations remain pending** | DESIGNED |
| R07 | Guide safe production adoption | Production readiness, security/privacy controls, rollback | Threat model, verified isolation/authorization tests, runbooks | PLANNED |
| R08 | Coordinate delivery specialists and handoffs | Roles, decision owners, dependency and handoff packages | Responsibility matrix and documented signoffs in synthetic demo | DESIGNED |
| R09 | Track technical account health and impact | Adoption and value dashboard | Usage, blockers, observed costs and outcome metrics with data provenance | PLANNED |
| R10 | Communicate with CTO/CIO/CISO/engineering | Executive and engineering walkthroughs | Demo scripts, design review, separate audience narratives | PLANNED |
| R11 | Enable ChatGPT Enterprise adoption | Enterprise governance and enablement playbook | Scenario plan; no implied admin deployment without access | PLANNED |
| R12 | Enable Codex adoption | Development workflow and adoption playbook | Documented and tested workflow where authorized | PLANNED |
| R13 | Build agentic solutions and technical prototypes | Controlled tool-using reference workflow | Human approval, authorization, trace and adversarial test evidence | PLANNED |
| R14 | Translate field insights to reusable practices | Decision log, pattern library and feedback report | Consolidated insights from explicitly synthetic cases | PLANNED |

## Coverage boundaries

Project artifacts can demonstrate **reasoning and implementation ability**, not substitute for independent verification of commercial client success, executive relationships, negotiation, or real-world adoption. Those claims belong to the author's verified professional history, not to synthetic outcomes generated for this repository.

The lab should show **a complete journey for one fictional client**, with two additional sector profiles demonstrating transferability. Do not build three extensive runtimes merely to fill the matrix.

## Evidence publishing rule

Before changing any row to `IMPLEMENTED` or `VERIFIED`, link the code path, test result, reviewed artifact, report, or verified deployment that supports the exact claim. A checked checkbox, screenshot, or model-generated report by itself is insufficient evidence of production readiness.

**M2 scope note (2026-11-17):** `R05 IMPLEMENTED` means an integration adapter and mocked request-contract test exist; it is **not** a claim of successfully executing a paid API request. `R06 DESIGNED` remains partial because the current run benchmarks deterministic fixture controls, not actual model or agent quality. See [`docs/EVALUATION_FACTORY.md`](docs/EVALUATION_FACTORY.md).
