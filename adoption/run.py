"""Run synthetic adoption recommendations without model/API calls or approvals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from adoption.engine import FIXTURE_PATH, evaluate, load_scenarios, sha256


def run(scenario_id: str | None = None) -> dict:
    bundle = load_scenarios()
    chosen = [s for s in bundle["scenarios"] if scenario_id is None or s["scenario_id"] == scenario_id]
    if not chosen:
        raise ValueError("Unknown synthetic scenario")
    return {
        "schema_version": "1.0", "synthetic": True,
        "fixture": {"version": bundle["version"], "sha256": sha256(FIXTURE_PATH)},
        "recommendations": [evaluate(s) for s in chosen],
        "approval_status": "NO_REAL_HUMAN_APPROVAL",
        "scope": "TRAINING_ONLY_NO_CUSTOMER_DECISION",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate fictional, risk-aware AI adoption readiness")
    parser.add_argument("--scenario", help="Named synthetic scenario; omit to evaluate all")
    parser.add_argument("--output", type=Path, help="Optional new JSON artifact path")
    args = parser.parse_args(argv)
    try:
        packet = run(args.scenario)
        output = json.dumps(packet, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            path = args.output.resolve()
            if path == FIXTURE_PATH.resolve() or path.exists():
                raise ValueError("Refusing to overwrite source fixtures or existing reports")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output, encoding="utf-8")
            print(f"Synthetic advisory artifact: {path}")
        else:
            print(output, end="")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
