"""Execute local paired evaluations with an explicit opt-in for paid API calls.

Usage:
  python -m evals.run
  python -m evals.run --candidate openai --model MODEL_ID --allow-billed-api
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from evals.engine import CORPUS_PATH, DATASET_PATH, SafeRuleCandidate, digest, execute, load_fixtures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a synthetic-only, versioned AI evaluation")
    parser.add_argument("--candidate", choices=("rules", "openai"), default="rules")
    parser.add_argument("--model", help="Explicit OpenAI model ID, only for --candidate openai")
    parser.add_argument("--allow-billed-api", action="store_true", help="Explicit authorization for model API charges")
    parser.add_argument("--max-cases", type=int, help="Limit evaluated cases (1-30)")
    parser.add_argument("--output", type=Path, default=Path("evals/runs/latest.json"), help="Local JSON run artifact")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_cases is not None and not 1 <= args.max_cases <= 30:
        raise SystemExit("--max-cases must be between 1 and 30")
    if args.candidate == "openai":
        if not args.allow_billed_api:
            raise SystemExit("Live OpenAI evaluation requires --allow-billed-api")
        if not args.model:
            raise SystemExit("Live OpenAI evaluation requires --model MODEL_ID")
        if not os.environ.get("OPENAI_API_KEY"):
            raise SystemExit("OPENAI_API_KEY must be configured; never commit credentials")
        from evals.providers import OpenAIResponsesCandidate

        candidate = OpenAIResponsesCandidate(args.model)
    else:
        if args.model or args.allow_billed_api:
            raise SystemExit("--model and --allow-billed-api are only valid with --candidate openai")
        candidate = SafeRuleCandidate()

    dataset, corpus = load_fixtures()
    result = execute(dataset, corpus, candidate, limit=args.max_cases)
    result["dataset"]["sha256"] = digest(DATASET_PATH)
    result["corpus"]["sha256"] = digest(CORPUS_PATH)
    result["run_mode"] = "BILLED_API" if args.candidate == "openai" else "OFFLINE_DETERMINISTIC"
    result["estimated_cost_usd"] = None
    output = args.output.resolve()
    # Never place artifacts in the tracked fixtures or overwrite source files.
    if output in (DATASET_PATH.resolve(), CORPUS_PATH.resolve()):
        raise SystemExit("Cannot overwrite versioned evaluation inputs")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(output)
    for system in result["systems"]:
        s = system["summary"]
        print(f"{system['provider']}: {s['passed']}/{s['total']} checks passed; "
              f"{len(s['critical_failures'])} critical failures")
    print(f"Artifact: {output}")
    print("Gate: HUMAN_REVIEW_REQUIRED (this evaluation cannot authorize deployment)")
    # Any failure in the candidate causes nonzero exit for automation.
    return 1 if result["systems"][-1]["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
