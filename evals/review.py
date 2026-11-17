"""Human-review worksheet and calibration report for synthetic evaluation runs.

Reviewer IDs are self-declared, NOT authenticated identities. The tool never
promotes a model score or reviewer statement to a production release approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from evals.engine import CORPUS_PATH, DATASET_PATH, digest, load_fixtures


def read_run(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    dataset, corpus = load_fixtures()
    if (report.get("synthetic") is not True
            or report.get("dataset", {}).get("sha256") != digest(DATASET_PATH)
            or report.get("corpus", {}).get("sha256") != digest(CORPUS_PATH)
            or report.get("dataset", {}).get("version") != dataset["version"]
            or report.get("corpus", {}).get("version") != corpus["version"]):
        raise ValueError("Run must be synthetic and match the current versioned fixture digests")
    if not report.get("systems") or not report["systems"][-1].get("cases"):
        raise ValueError("Run has no candidate results to review")
    case_lookup = {case["case_id"]: case for case in dataset["cases"]}
    observed = report["systems"][-1]["cases"]
    if len(observed) != len({c["case_id"] for c in observed}):
        raise ValueError("Duplicate candidate case IDs")
    if any(case["case_id"] not in case_lookup for case in observed):
        raise ValueError("Candidate result contains unknown case")
    return report


def run_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(run: dict, run_digest: str, reviewer_id: str) -> dict:
    """Create empty judgments; never autofill simulated human opinions."""
    if len(reviewer_id.strip()) < 3 or len(reviewer_id) > 120:
        raise ValueError("Self-declared reviewer ID must contain 3–120 characters")
    dataset, _ = load_fixtures()
    case_lookup = {case["case_id"]: case for case in dataset["cases"]}
    candidate = run["systems"][-1]
    rows = []
    for result in candidate["cases"]:
        source = case_lookup[result["case_id"]]
        rows.append({
            "case_id": result["case_id"],
            "category": source["category"], "critical": source["critical"],
            "question": source["question"],
            "expected_behavior": source["expected_behavior"],
            "expected_reference_ids": source.get("required_doc_ids", []),
            "candidate_answer": result["prediction"]["answer"],
            "candidate_citations": result["prediction"]["citations"],
            "candidate_abstained": result["prediction"]["abstained"],
            "automated_passed": result["grade"]["passed"],
            "label_review": "UNREVIEWED",  # ACCEPT / REJECT the expected behavior label
            "answer_review": "UNREVIEWED",  # PASS / FAIL candidate's behavior
            "rationale": "",  # Must be a specific explanation, not a generic signoff
        })
    return {
        "schema_version": "1.0", "synthetic": True,
        "reviewer_id": reviewer_id.strip(), "identity_status": "SELF_DECLARED_UNVERIFIED",
        "source_run_sha256": run_digest, "source_provider": candidate["provider"],
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cases": rows,
        "instructions": (
            "For each case, independently review the expected label and the candidate response. "
            "Set label_review to ACCEPT or REJECT, answer_review to PASS or FAIL, "
            "and explain why in rationale (12+ characters). Do not leave any value UNREVIEWED "
            "when submitting for calibration. Reviewer ID is not independently authenticated."
        ),
    }


def _check_sheet(sheet: dict, report: dict, digest_value: str) -> tuple[bool, dict[str, dict]]:
    if sheet.get("synthetic") is not True or sheet.get("source_run_sha256") != digest_value:
        raise ValueError("Review sheet is not bound to this exact synthetic run")
    if sheet.get("source_provider") != report["systems"][-1]["provider"]:
        raise ValueError("Review sheet belongs to another candidate")
    if sheet.get("identity_status") != "SELF_DECLARED_UNVERIFIED":
        raise ValueError("Review must retain its unverified identity status")
    reviewer_id = sheet.get("reviewer_id", "")
    if not isinstance(reviewer_id, str) or not 3 <= len(reviewer_id.strip()) <= 120:
        raise ValueError("Invalid reviewer ID")
    expected = {case["case_id"] for case in report["systems"][-1]["cases"]}
    original = {case["case_id"]: case for case in prepare(report, digest_value, reviewer_id)["cases"]}
    immutable_fields = (
        "case_id", "category", "critical", "question", "expected_behavior",
        "expected_reference_ids", "candidate_answer", "candidate_citations",
        "candidate_abstained", "automated_passed",
    )
    rows = sheet.get("cases")
    if not isinstance(rows, list):
        raise ValueError("Missing review cases")
    seen = {}
    complete = True
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Malformed review row")
        identifier = row.get("case_id")
        if identifier not in expected or identifier in seen:
            raise ValueError("Foreign or duplicate review case")
        if any(row.get(field) != original[identifier][field] for field in immutable_fields):
            raise ValueError("Review must not alter the source evidence or automated result")
        if row.get("label_review") not in {"ACCEPT", "REJECT", "UNREVIEWED"}:
            raise ValueError("Invalid expected-label review value")
        if row.get("answer_review") not in {"PASS", "FAIL", "UNREVIEWED"}:
            raise ValueError("Invalid candidate-answer review value")
        rationale = row.get("rationale")
        if not isinstance(rationale, str):
            raise ValueError("Rationale must be text")
        if (row["label_review"] == "UNREVIEWED" or row["answer_review"] == "UNREVIEWED"
                or len(rationale.strip()) < 12):
            complete = False
        seen[identifier] = row
    if set(seen) != expected:
        raise ValueError("Review sheet does not cover exactly the evaluated cases")
    return complete, seen


def summarize(run: dict, run_digest: str, sheets: list[dict]) -> dict:
    if len(sheets) > 2:
        raise ValueError("This calibration checkpoint supports at most two review sheets")
    identities = [sheet.get("reviewer_id") for sheet in sheets]
    if len(set(identities)) != len(identities):
        raise ValueError("Two reviews must have distinct self-declared reviewer IDs")
    checked = [_check_sheet(sheet, run, run_digest) for sheet in sheets]
    complete_sheets = [rows for complete, rows in checked if complete]
    candidate = run["systems"][-1]
    disagreements = []
    critical_review_failures = []
    label_disputes = []
    agreement = None
    if len(complete_sheets) == 2:
        same = sum(
            complete_sheets[0][case["case_id"]]["answer_review"]
            == complete_sheets[1][case["case_id"]]["answer_review"]
            for case in candidate["cases"]
        )
        agreement = round(same / len(candidate["cases"]), 4)
    for result in candidate["cases"]:
        identifier = result["case_id"]
        verdicts = [rows[identifier] for rows in complete_sheets]
        if any(v["label_review"] == "REJECT" for v in verdicts):
            label_disputes.append(identifier)
        if any((v["answer_review"] == "PASS") != result["grade"]["passed"] for v in verdicts):
            disagreements.append(identifier)
        if result["grade"]["critical"] and any(v["answer_review"] == "FAIL" for v in verdicts):
            critical_review_failures.append(identifier)
    status = "TWO_SELF_DECLARED_REVIEWS" if len(complete_sheets) == 2 else "INCOMPLETE"
    return {
        "schema_version": "1.0", "synthetic": True, "source_run_sha256": run_digest,
        "review_status": status, "reviewer_identity_verified": False,
        "complete_reviewer_count": len(complete_sheets),
        "human_answer_agreement_rate": agreement,
        "automated_human_disagreement_case_ids": sorted(disagreements),
        "expected_label_dispute_case_ids": sorted(label_disputes),
        "critical_human_failure_case_ids": sorted(critical_review_failures),
        "release_decision": "HUMAN_REVIEW_REQUIRED",
        "caveat": (
            "Reviewer identities are self-declared; two submissions do not prove independent review. "
            "No automatic gate approval, production or compliance signoff is granted."
        ),
    }


def _write_new(path: Path, data: dict) -> None:
    path = path.resolve()
    if path.exists():
        raise ValueError(f"Refusing to overwrite an existing review artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare or summarize self-attested evaluation reviews")
    sub = parser.add_subparsers(dest="action", required=True)
    init = sub.add_parser("prepare", help="Create an entirely unreviewed human worksheet")
    init.add_argument("--run", type=Path, required=True)
    init.add_argument("--reviewer-id", required=True)
    init.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("summarize", help="Validate and compare up to two review worksheets")
    check.add_argument("--run", type=Path, required=True)
    check.add_argument("--review", type=Path, action="append", required=True)
    check.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = read_run(args.run)
        current_digest = run_sha256(args.run)
        if args.action == "prepare":
            output = prepare(report, current_digest, args.reviewer_id)
        else:
            sheets = [json.loads(path.read_text(encoding="utf-8")) for path in args.review]
            output = summarize(report, current_digest, sheets)
        _write_new(args.output, output)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from None
    print(f"Review artifact: {args.output}")
    print("No production or customer deployment authorization was granted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
