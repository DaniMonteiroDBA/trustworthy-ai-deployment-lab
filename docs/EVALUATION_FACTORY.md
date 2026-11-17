# Evaluation Factory — M2 runner and M3 review checkpoint

**Status:** first offline evaluation vertical slice and an unverified-identity human-review **protocol/tooling** are executable and unit-tested. Live OpenAI integration is coded behind an explicit opt-in, but **no live model call or genuine human calibration has been performed**. No real customer data, production authorization, or user authentication exists.

## Evaluation question

Can a policy-navigation component identify when it has sufficient active evidence to answer, when it should abstain, and when it must reject an attempted action or cross-tenant request?

This is a controlled technical example for FinTrust, RetailFlow, and CivicData, three **fictional** organizations. It does not establish that any real enterprise has improved its operations or adopted AI.

## Baseline and candidate controls

| System | Implementation | What it establishes | What it does **not** establish |
| --- | --- | --- | --- |
| `keyword_search_baseline` | Exact token overlap, first matching excerpt, no AI calls | A simple non-AI alternative and its known weaknesses | A well-designed production search engine |
| `offline_safe_rules` | Conservative deterministic rules, tenant-scoped active-document filtering, abstention | Unit-testable security and abstention controls | LLM correctness, semantic reasoning or real deployment value |
| `openai_responses` | Optional Responses API call with Pydantic structured output, `store=False`, SDK timeout and bounded retries | An integration path testable with a mocked SDK | Live compatibility, model quality, actual pricing or availability before a paid run |

The deterministic candidate is hand-built for a small illustrative scenario. Its fixture score **must not** be presented as an AI model benchmark. Hand-authored examples and assertions have **not** been independently reviewed or held out for statistical assessment.

## Run and reproduce

Python 3.12+:

```bash
python -m pip install -r requirements.txt
python -m evals.run
python -m unittest discover -s tests -v
```

By default, the runner performs zero model API calls and writes `evals/runs/latest.json` (excluded from Git). Alternatively launch the Studio and click **Run offline evaluation**; results persist locally at `data/eval_runs/latest.json`.

Optional **paid**, explicitly authorized API run, once credentials and a suitable model ID have been configured:

```bash
python -m pip install -r requirements-openai.txt
# Configure OPENAI_API_KEY in your own environment; never write it into this repo.
python -m evals.run --candidate openai --model YOUR_APPROVED_MODEL_ID --allow-billed-api --max-cases 3
```

The CLI refuses a paid run without an explicit flag, a model ID, an environment-provided key and `--max-cases` between 1 and 5. A paid candidate run **stops on its first provider error**; the baseline still runs locally. No live calls are made by the web UI. The SDK uses an approximately 20-second timeout, at most two built-in retries, no persistence of Responses via API (`store=False`), and a maximum of 600 output tokens per case. This bounds the test request volume; **it does not enforce a monetary budget**. Charges, rate limits, and availability depend on your account and selected model; the tool does not guess dollar costs. **Use synthetic fixtures only.**

## Human review: a deliberately unapproved checkpoint

The `evals.review` CLI provides blank, run-bound reviewer worksheets and a comparison report. This is an **inspection protocol**, not fabricated evidence of human validation:

```bash
python -m evals.run
python -m evals.review prepare --run evals/runs/latest.json --reviewer-id reviewer-a --output evals/reviews/reviewer-a.json
python -m evals.review prepare --run evals/runs/latest.json --reviewer-id reviewer-b --output evals/reviews/reviewer-b.json
# Once two actual reviewers fill in their own worksheets:
python -m evals.review summarize --run evals/runs/latest.json \
  --review evals/reviews/reviewer-a.json --review evals/reviews/reviewer-b.json \
  --output evals/reviews/calibration-summary.json
```

`prepare` creates **zero prefilled human judgments**. Reviewers independently assess the reference label and candidate behavior with written reasons. The command checks exact SHA-256 run provenance, immutable source text, distinct self-declared IDs, allowed verdicts, rationale length, and full case coverage. The summary exposes reviewer agreement, rejected gold labels, automated-versus-human disagreements, and critical human failures. Even two complete worksheets cannot authenticate identities, guarantee independence, or approve a release. Consult the [full human-review rubric and limitations](HUMAN_REVIEW_PROTOCOL.md).

## What an artifact contains

- Schema and engine versions, UTC execution time, `synthetic=true`, and execution mode.
- Dataset/corpus version identifiers and SHA-256 content digests.
- Per-system, per-case predictions, citations, abstention flags, elapsed local request time, and error type.
- When supplied by the API, observed input/output token counts. Dollar cost remains `null` without a reviewed price schedule.
- Test-specific pass/fail reasons, critical-failure IDs, observed case counts and pass rates.
- `release_decision: HUMAN_REVIEW_REQUIRED` independent of aggregate score.
- Explicit `planned_cases` and `interrupted_on_error` fields prevent misreading a partial paid run as a completed benchmark.

No human reviewer has signed off on a release. The local heuristic grader does **not** prove semantic correctness. A model can pass the string assertions yet still be incorrect or unsafe in other ways. Error artifacts intentionally omit upstream exception messages, which may contain sensitive prompt material.

## Critical failure policy

Cases marked `critical=true` cover cross-tenant requests, unauthorized actions, prompt injections (including in retrieved material), and stale policy versions. Any critical failure is highlighted separately from the average pass rate. A successful aggregate score **never automatically authorizes** the next deployment stage.

The `offline_safe_rules` candidate is required to abstain on unsupported questions and prohibited requests. It cannot execute any tool. For the OpenAI candidate, **no tools are exposed**. Therefore an attempted action cannot be executed by this integration; however, the model can still generate false claims of having done so, which are explicit grader failure conditions.

The offline demonstration also tests:

- Unverified or revoked evidence cannot serve as current citation authority.
- Tenant filtering happens before document context is assembled for an API request.
- Citation IDs must refer to active documents belonging to the case tenant.
- Known forbidden text markers and simulated action-completion claims fail the grader.
- Error paths fail closed and disclose only exception types.

## Current gaps to close before a real pilot

1. **Actually performed** independent human annotation, adjudication and reviewed scoring rubric; more varied held-out and adversarial data. Blank self-declared worksheets are now implemented, not real reviews.
2. Actual live Responses API test (currently mocked), model-specific behavior and refusal handling.
3. Semantic groundedness, relevant/complete citation checks, calibration of automatic versus human grading.
4. Authenticated users and true tenant authorization; separate storage and retrieval security tests.
5. Approved token-price snapshots, real cost measurement, rate limits and enforceable client-dollar budgets. A five-case limit is not budget enforcement.
6. Safe measured-evidence ingestion into the adoption gate after a reviewed run. **Offline fixture scores do not become automatically verified `MEASURED` evidence.**
7. Repeatability studies across runs, CI infrastructure recovery, release criteria, monitoring, incident response and rollback.

## Official references used for the integration design

- [OpenAI — Text generation with the Responses API](https://developers.openai.com/api/docs/guides/text)
- [OpenAI — Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [OpenAI — Error handling](https://developers.openai.com/api/docs/guides/error-codes)

The OpenAI documentation available in November 2026 describes retirement of its legacy Evals platform. This project therefore owns its evaluation harness and does not depend on that legacy service. Future API changes must be verified against current official documentation.
