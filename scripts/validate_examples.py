"""Validate the v0.1 synthetic decision-record contract using only stdlib.

This is a limited structural and consistency validator, *not* a security,
business-readiness, or JSON Schema certification.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


CLASSES = {"DECLARED", "DOCUMENTED", "MEASURED", "INFERRED"}
VERIFICATIONS = {"UNVERIFIED", "VERIFIED", "REJECTED"}
STAGES = {"DISCOVER", "ASSESS", "PRIORITIZE", "ARCHITECT", "VALIDATE", "ADOPT", "MEASURE_IMPROVE"}
STATUSES = {"NOT_STARTED", "IN_REVIEW", "GO", "REWORK", "HOLD", "NO_GO"}


def validate(record: object) -> list[str]:
    """Return descriptive contract errors without mutating the input."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["Root must be an object"]

    if record.get("schema_version") != "0.1":
        errors.append("schema_version must be 0.1")

    client = record.get("client")
    if not isinstance(client, dict) or client.get("synthetic") is not True:
        errors.append("client.synthetic must be true in the public repository")
    elif not client.get("client_id") or not client.get("sector"):
        errors.append("client requires client_id and sector")

    use_case = record.get("use_case")
    if not isinstance(use_case, dict):
        errors.append("use_case must be an object")
    else:
        for field in ("use_case_id", "problem", "business_owner", "success_metric", "non_ai_alternative"):
            if not isinstance(use_case.get(field), str) or not use_case[field].strip():
                errors.append(f"use_case.{field} is required")

    evidence = record.get("evidence")
    ids: set[str] = set()
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
        evidence = []

    by_id: dict[str, dict] = {}
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{index}] must be an object")
            continue
        identifier = item.get("evidence_id")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"evidence[{index}].evidence_id is required")
            continue
        if identifier in ids:
            errors.append(f"Duplicate evidence_id: {identifier}")
        ids.add(identifier)
        by_id[identifier] = item
        if item.get("class") not in CLASSES:
            errors.append(f"Invalid evidence class: {identifier}")
        if item.get("verification_status") not in VERIFICATIONS:
            errors.append(f"Invalid verification status: {identifier}")
        for field in ("source", "summary"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"Missing {field}: {identifier}")

    decision = record.get("decision")
    if not isinstance(decision, dict):
        return errors + ["decision must be an object"]
    if not decision.get("decision_id"):
        errors.append("decision_id is required")
    if decision.get("stage") not in STAGES or record.get("stage") != decision.get("stage"):
        errors.append("decision.stage must be a known stage matching record.stage")
    if decision.get("status") not in STATUSES:
        errors.append("decision.status invalid")
    for field in ("owner", "rationale"):
        if not isinstance(decision.get(field), str) or not decision[field].strip():
            errors.append(f"decision.{field} is required")
    refs = decision.get("evidence_ids")
    if not isinstance(refs, list):
        errors.append("decision.evidence_ids must be an array")
        refs = []
    for ref in refs:
        if ref not in by_id:
            errors.append(f"Unknown evidence reference: {ref}")
    for field in ("blockers", "alternatives"):
        if not isinstance(decision.get(field), list):
            errors.append(f"decision.{field} must be an array")
    if decision.get("status") == "GO":
        verified_basis = any(
            by_id[ref].get("verification_status") == "VERIFIED"
            and by_id[ref].get("class") in {"DOCUMENTED", "MEASURED"}
            for ref in refs if ref in by_id
        )
        if not verified_basis:
            errors.append("GO requires at least one verified DOCUMENTED or MEASURED evidence item")
        if decision.get("blockers"):
            errors.append("GO may not contain unresolved blockers")
    return errors


def main(paths: list[str]) -> int:
    if not paths:
        print("Usage: python -m scripts.validate_examples examples/*.json", file=sys.stderr)
        return 2
    failures = 0
    for path_string in paths:
        path = Path(path_string)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            problems = validate(record)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            problems = [str(error)]
        if problems:
            failures += 1
            print(f"FAIL {path}: " + "; ".join(problems))
        else:
            print(f"PASS {path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
