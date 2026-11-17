# Decision & Evidence Contract — v0.1

This is the *behavioral contract* for recommendations and stage gates. It is a design artifact, not a production authorization system.

## Required fields

| Entity | Required fields | Invariant |
| --- | --- | --- |
| Client | `client_id`, `sector`, `synthetic` | Public repo clients must be synthetic |
| Use case | `use_case_id`, `problem`, `business_owner`, `success_metric`, `non_ai_alternative` | AI is an option, not the default conclusion |
| Evidence | `evidence_id`, `class`, `verification_status`, `source`, `summary` | Evidence is attributable and typed |
| Decision | `decision_id`, `stage`, `status`, `owner`, `rationale`, `evidence_ids`, `blockers`, `alternatives` | A human owner is required; references must exist |
| Measurement | `metric_id`, `value`, `unit`, `method`, `context`, `observed_at`, `source` | Never record invented ROI or quality values as measured |

## State changes

`NOT_STARTED -> IN_REVIEW -> GO | REWORK | HOLD | NO_GO`

Only an authorized human role can change a stage decision from `IN_REVIEW` to a terminal state. Changing an earlier decision invalidates dependent later-stage approvals until reviewed again.

## Gate invariants

1. No `GO` without a human owner and a rationale.
2. No `GO` from AI-inferred evidence alone. A model-generated summary must cite underlying sources, which a reviewer must examine.
3. Critical `authorization`, `cross_tenant_exposure`, or `unapproved_external_action` blockers prevent `GO` for validation/production gates even if average test scores are high.
4. Technical evaluation results are never marked `MEASURED` until an actual run yields versioned output and contextual metadata.
5. No real customer data may be committed to the public repository.
6. The decision log is append-oriented: revisions retain prior outcome, timestamp, and author.
7. Human-approved `GO` means approval for **the next bounded stage**, never an unrestricted production certificate.

## Example data

See [`examples/fintrust_discovery.json`](../examples/fintrust_discovery.json). All entities and statements in it are fictional; its `IN_REVIEW` decision does not assert any validation or approval.

## Security questions for implementation

- Who creates and verifies a client organization and user identity?
- Which role can approve a PoV, production release, external tool call, or override?
- How are business/legal constraints recorded without exposing sensitive text in model prompts or traces?
- How are evidence items retained, revised, revoked, and traced into executive reports?
- How are an organization and its private evidence isolated from others across storage, search, caching, and logs?

These decisions must be resolved in architecture and tested before any customer-facing deployment.
