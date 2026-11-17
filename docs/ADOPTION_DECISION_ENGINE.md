# Adoption Decision Engine — Reference Policy v0.1

**Status:** implemented as a **read-only synthetic decision-support example**. This is not a certified risk methodology, an authorization workflow, a client score, or a substitute for expert review.

## Decision being modeled

> Should an enterprise AI use case move from **VALIDATE** to **ADOPT**, or must the team stop, repair, or redesign the proposed path?

This is **one transition** in the seven-stage Trusted AI Adoption Framework, not an implementation of all seven transition policies. It is reusable as a template because the decision dimensions, risk profile, evidence requirements, and precedence rules are separate from client-specific data.

The engine intentionally computes **no global maturity score**. A high average cannot compensate for a denied data-use permission, a critical security defect, or a missing independent review in a high-risk case.

## Decision contract

Inputs: one explicitly fictional scenario containing client/use-case identity, risk tier, accountable owner, non-AI alternative, evidence register, dimension-specific checks, and declared blockers. Evidence is classified as `DECLARED`, `DOCUMENTED`, `MEASURED`, or `INFERRED` and tagged `SIMULATED_VERIFIED`, `UNVERIFIED`, or `REJECTED`.

The policy logic accepts additional fictitious `client_id` values ending in `-demo` and matching case IDs (for example, `newventure-demo` / `newventure-internal-policy`); adding a client does **not** require changing the policy code. This naming check does not provide real tenant isolation or proof that user-entered material is synthetic.

Each check has:

- `dimension`: a requirement named below;
- `status`: `PASS`, `UNKNOWN`, `GAP`, or `FAIL`;
- `evidence_ids`: references within the **same** synthetic assessment;
- `rationale` and `next_action`: explicit justification and remediation.

The eight core requirements are:

| Dimension | Decision question | Expected evidence |
| --- | --- | --- |
| `BUSINESS_VALUE` | Is there a bounded problem, owner, baseline and plausible benefit? | Documentary decision record |
| `NON_AI_ALTERNATIVE` | Was a less complex solution fairly considered? | Options/comparison record |
| `DATA_GOVERNANCE` | Is data fit, authorized, current and attributable? | Data inventory, permissions and authority |
| `AI_EVALUATION` | Does a predeclared evaluation demonstrate useful and safe behavior? | **Measurement** and contextual method |
| `SECURITY_PRIVACY` | Are security, access and privacy constraints addressed? | Reviewed threat and data-flow evidence |
| `ECONOMICS` | Is the chosen solution supportable relative to alternatives? | **Measurement** of cost, not just estimate |
| `OPERATIONS` | Can it be monitored, supported and rolled back? | Operations/incident/rollback records |
| `HUMAN_ACCOUNTABILITY` | Who owns the next bounded decision and exceptions? | Named responsibility and escalation record |

`HIGH` risk additionally requires `INDEPENDENT_REVIEW`. The illustrative `MEDIUM`/`LOW` profiles use the eight core checks. These profiles are **design proposals**. A real customer must choose and validate profile thresholds, severity definitions, approval authorities and applicable local obligations.

## Deterministic precedence

| Condition | Advisory recommendation | Why |
| --- | --- | --- |
| An open `TERMINAL` blocker, or a `FAIL` check | `NO_GO` | The current proposed path has an unacceptable condition |
| An open `AUTHORIZATION` blocker, unknown mandatory check, or unsupported `PASS` | `HOLD` | Evidence, permission or trusted verification is not established |
| An open `REMEDIABLE` blocker or a `GAP` check | `REWORK` | A correctable issue must be addressed and reassessed |
| Every required check has `PASS` with qualifying synthetic support; no open blockers | `GO` | Candidate for **human review of the next bounded stage only** |

When multiple conditions apply, precedence is **`NO_GO` > `HOLD` > `REWORK` > `GO`**. This intentionally errs toward stopping a proposed path. A `PASS` without any `SIMULATED_VERIFIED` documentary or measured support becomes `HOLD`; `AI_EVALUATION` and `ECONOMICS` specifically require `MEASURED` evidence. Evidence references outside the assessed use case cause an input validation error.

`SIMULATED_VERIFIED` means **fictional verification for testing the algorithm**. It is *not* proof of actual model quality, spending, access rights, stakeholder validation or identity. An invented measurement is never a measured business outcome. A check citing any **rejected** source cannot pass, even if it also cites a simulated-verified item.

## Repeatable reference demonstration

```bash
python -m adoption.run --scenario fintrust-hold
python -m adoption.run --scenario retailflow-rework
python -m adoption.run --scenario civicdata-no-go
python -m adoption.run --scenario fintrust-ideal-go
```

Omit `--scenario` to inspect all four. For a local new JSON artifact:

```bash
python -m adoption.run --output adoption/runs/checkpoint.json
```

The CLI records a SHA-256 of the versioned fixture and refuses to overwrite an existing output. Every scenario is fully fictional; the ideal `GO` fixture deliberately uses invented, synthetic evidence to exercise a **code branch**, not to claim customer readiness. The output always includes:

```json
{
  "recommended_state": "GO",
  "decision_authority": "ADVISORY_ONLY",
  "human_approval": "NOT_RECORDED",
  "release_authorized": false,
  "customer_readiness_verified": false
}
```

The Studio's new **M3 Adoption Decision Engine** panel displays all four frozen examples. Its read-only endpoints are `GET /api/adoption/scenarios` and `GET /api/adoption/scenarios/{scenario_id}`. **They do not read or modify the editable case decisions in SQLite.** This separation prevents example outputs from silently becoming authoritative approval records.

## Human decision and next evidence

The recommendation should be reviewed by a real accountable sponsor, technical owner, data/security reviewers and operational owner as relevant to the context. Before any real `GO`, a private production-quality implementation needs verified identities and access controls; source evidence, quality, risks and cost measured in the intended environment; a reviewed non-AI comparator; independent judgment for critical cases; documented residual risk and rollback; and explicit recorded authority for the next stage.

**This public lab currently has none of those real-world signoffs.** The original [Decision Contract](DECISION_CONTRACT.md) still controls simulated human stage records; the [Human Review Protocol](HUMAN_REVIEW_PROTOCOL.md) governs the separate evaluation calibration worksheet. Neither is secretly connected to this demonstration engine.

## Known limitations and next milestones

1. Risk-tier checklists and blocker severities need stakeholder calibration and independent challenge.
2. There is no verification of data-source authenticity, reviewer identity or factual correctness of check status.
3. The recommendation engine reads versioned fictional scenario files only; editable customer assessments, secure tenant authorization and user roles remain unimplemented.
4. No real model run, approved cost ceiling, budget enforcement or adoption outcome is measured.
5. A future trusted adapter must bind authenticated, source-verified evidence and actual test outputs to an auditable human decision. It must **never** convert an advisory `GO` into production approval automatically.

This design supports the [seven-stage methodology](METHODOLOGY.md), [evaluation factory](EVALUATION_FACTORY.md), and [architecture](ARCHITECTURE.md).
