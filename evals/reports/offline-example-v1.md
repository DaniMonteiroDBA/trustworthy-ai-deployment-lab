# Offline evaluation checkpoint — synthetic fixture v1

**Observed:** November 17, 2026 (local Python 3.12 environment).  
**Command:** `python -m evals.run --output evals/runs/latest.json`  
**Mode:** `OFFLINE_DETERMINISTIC` — no model/API calls and no API charges.  
**Decision:** `HUMAN_REVIEW_REQUIRED`.

| System | Checks passed | Critical cases failed | Interpretation |
| --- | ---: | ---: | --- |
| Keyword-search baseline | 6 / 13 | 6 | Some supported answers succeed; unsupported, cross-tenant, action and injection cases expose weak guardrails. |
| Offline deterministic safety rules | 13 / 13 | 0 | The hand-authored rules satisfy the small hand-authored synthetic suite. **This is not a model score.** |

The suite includes grounded policy answers, a missing-information request, cross-tenant disclosure, unauthorized approval/payment, user and retrieved-document prompt injections, revoked policy text, and independent retailer/public-sector scenarios. Scoring is deterministic and restricted to required terms, citations, abstention, action markers and known forbidden strings; it **cannot** establish complete semantic correctness.

## Artifact identity

- Dataset: `fintrust_policy_v1.json` version `1.0.0`  
  SHA-256: `e5008702bd78123b43b3a483e8c9b442adce69cec350231aab497d38bbbc31a9`
- Corpus: `synthetic_policies_v1.json` version `1.0.0`  
  SHA-256: `343ffe31f42d28baf831247e7f69bf236e74e5aeddaad4e6e709bb45779cebdd`
- Evaluation engine: `0.2.0`
- Test suite at this checkpoint: **28 passing local tests** (including the broader M1 contracts).

This note records a local observation. It is not evidence of field adoption, commercial impact, independently human-reviewed labels, successful live OpenAI API use, production security, or an approved enterprise rollout. Re-run the command with the identified files to reproduce the counts; local latency numbers and execution timestamps will naturally differ.

**Known blocker:** remote GitHub Actions cannot currently allocate its hosted runners; see [tracking issue #6](https://github.com/DaniMonteiroDBA/trustworthy-ai-deployment-lab/issues/6). Local passing tests do not mean CI is green.
