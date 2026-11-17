"""Evidence-linked, non-scored advisory decisions for fictional AI adoption cases.

This package does not authenticate reviewers, authorize deployments, or process
real client data. GO is a recommendation to a human, not an approved stage gate.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = ROOT / "fixtures" / "decision_scenarios_v1.json"
POLICY_VERSION = "0.1.0"
CORE = (
    "BUSINESS_VALUE", "NON_AI_ALTERNATIVE", "DATA_GOVERNANCE", "AI_EVALUATION",
    "SECURITY_PRIVACY", "ECONOMICS", "OPERATIONS", "HUMAN_ACCOUNTABILITY",
)
HIGH_RISK = ("INDEPENDENT_REVIEW",)
MEASURED_REQUIRED = {"AI_EVALUATION", "ECONOMICS"}
KIND = {"DECLARED", "DOCUMENTED", "MEASURED", "INFERRED"}
STATES = {"PASS", "UNKNOWN", "GAP", "FAIL"}
DEMO_CLIENT_ID = re.compile(r"[a-z0-9][a-z0-9-]{2,60}-demo")
USE_CASE_ID = re.compile(r"[a-z0-9][a-z0-9-]{3,100}")
PRIORITY = {"GO": 0, "REWORK": 1, "HOLD": 2, "NO_GO": 3}


def sha256(path: Path = FIXTURE_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_scenarios(path: Path = FIXTURE_PATH) -> dict:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    if bundle.get("synthetic") is not True or bundle.get("version") != "1.0":
        raise ValueError("Only versioned, explicitly synthetic decision scenarios are allowed")
    scenarios = bundle.get("scenarios")
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 30:
        raise ValueError("Expected 1–30 fictional decision scenarios")
    seen = set()
    for scenario in scenarios:
        identifier = scenario.get("scenario_id")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}", identifier):
            raise ValueError("Invalid synthetic scenario ID")
        if identifier in seen:
            raise ValueError("Duplicate scenario ID")
        seen.add(identifier)
        evaluate(scenario)
    return bundle


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not 3 <= len(value.strip()) <= 1200:
        raise ValueError(f"{name} must be substantive text")
    return value.strip()


def evaluate(scenario: dict) -> dict:
    """Compute an advisory state; no weighted score or automatic approval exists."""
    if not isinstance(scenario, dict) or scenario.get("synthetic") is not True:
        raise ValueError("This public engine accepts synthetic scenarios only")
    tenant = scenario.get("client_id")
    case_id = scenario.get("case_id")
    if (not isinstance(tenant, str) or DEMO_CLIENT_ID.fullmatch(tenant) is None
            or not isinstance(case_id, str) or USE_CASE_ID.fullmatch(case_id) is None
            or not case_id.startswith(tenant.removesuffix("-demo") + "-")):
        raise ValueError("Scenario requires a synthetic client and matching fictional use case")
    risk = scenario.get("risk_tier")
    if risk not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError("Unknown risk tier")
    _text(scenario.get("accountable_owner"), "Accountable owner")
    _text(scenario.get("non_ai_alternative"), "Non-AI alternative")
    identifier = _text(scenario.get("scenario_id"), "Scenario ID")
    name = _text(scenario.get("title"), "Scenario title")

    evidence = scenario.get("evidence")
    checks = scenario.get("checks")
    blockers = scenario.get("blockers")
    if not isinstance(evidence, list) or len(evidence) > 60:
        raise ValueError("Expected 0–60 synthetic evidence references")
    if not isinstance(checks, list) or len(checks) > 30 or not isinstance(blockers, list) or len(blockers) > 30:
        raise ValueError("Invalid checks or blocker list")

    index = {}
    for entry in evidence:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or entry["id"] in index:
            raise ValueError("Invalid or duplicate evidence ID")
        if (entry.get("synthetic") is not True or entry.get("kind") not in KIND
                or entry.get("verification") not in {"SIMULATED_VERIFIED", "UNVERIFIED", "REJECTED"}):
            raise ValueError("Invalid evidence class, synthetic flag or verification status")
        _text(entry.get("source"), "Evidence source")
        index[entry["id"]] = entry

    reasons = []
    dimensions = []

    def flag(state: str, code: str, dimension: str | None, detail: str, action: str) -> None:
        reasons.append({"state": state, "code": code, "dimension": dimension,
                        "detail": detail, "next_action": action})

    required = (*CORE, *(HIGH_RISK if risk == "HIGH" else ()))
    observed = {}
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("Malformed check")
        dimension = check.get("dimension")
        if dimension not in set(CORE) | set(HIGH_RISK) or dimension in observed:
            raise ValueError("Unknown or duplicate decision dimension")
        status = check.get("status")
        references = check.get("evidence_ids")
        if status not in STATES or not isinstance(references, list) or len(references) > 20:
            raise ValueError("Unknown check state or evidence reference list")
        if any(not isinstance(ref, str) or ref not in index for ref in references):
            raise ValueError("Check cites foreign or unknown evidence")
        if len(set(references)) != len(references):
            raise ValueError("Duplicate evidence reference")
        rationale = _text(check.get("rationale"), "Check rationale")
        action = _text(check.get("next_action"), "Check next action")
        observed[dimension] = check
        valid = any(
            index[ref]["verification"] == "SIMULATED_VERIFIED"
            and index[ref]["kind"] in ({"MEASURED"} if dimension in MEASURED_REQUIRED else {"DOCUMENTED", "MEASURED"})
            for ref in references
        )
        rejected = any(index[ref]["verification"] == "REJECTED" for ref in references)
        if status == "PASS" and (not valid or rejected):
            flag("HOLD", "INSUFFICIENT_EVIDENCE", dimension,
                 "PASS lacks supported evidence or cites a rejected source", action)
        elif status == "UNKNOWN":
            flag("HOLD", "UNKNOWN_CRITERION", dimension, rationale, action)
        elif status == "GAP":
            flag("REWORK", "CORRECTABLE_GAP", dimension, rationale, action)
        elif status == "FAIL":
            flag("NO_GO", "UNACCEPTABLE_CONDITION", dimension, rationale, action)
        dimensions.append({"dimension": dimension, "status": status,
                           "evidence_ids": references, "support_valid_for_demo": valid and not rejected,
                           "rationale": rationale, "next_action": action})

    for dimension in required:
        if dimension not in observed:
            flag("HOLD", "MISSING_MANDATORY_CHECK", dimension,
                 "Required risk-profile dimension has not been assessed",
                 "Document and assess this dimension with attributable evidence")

    seen_blockers = set()
    for blocker in blockers:
        if not isinstance(blocker, dict):
            raise ValueError("Malformed blocker")
        blocker_id = blocker.get("id")
        if not isinstance(blocker_id, str) or blocker_id in seen_blockers:
            raise ValueError("Invalid or duplicate blocker ID")
        seen_blockers.add(blocker_id)
        severity = blocker.get("severity")
        status = blocker.get("status")
        if severity not in {"TERMINAL", "AUTHORIZATION", "REMEDIABLE"} or status not in {"OPEN", "RESOLVED"}:
            raise ValueError("Invalid blocker severity or status")
        summary = _text(blocker.get("summary"), "Blocker summary")
        action = _text(blocker.get("next_action"), "Blocker next action")
        if status == "OPEN":
            mapping = {"TERMINAL": "NO_GO", "AUTHORIZATION": "HOLD", "REMEDIABLE": "REWORK"}
            flag(mapping[severity], "OPEN_" + severity + "_BLOCKER", None, summary, action)
        else:
            references = blocker.get("resolution_evidence_ids")
            if (not isinstance(references, list) or not references
                    or any(not isinstance(ref, str) or ref not in index for ref in references)):
                raise ValueError("Resolved blocker requires known evidence references")
            if (any(index[ref]["verification"] == "REJECTED" for ref in references)
                    or not any(index[ref]["verification"] == "SIMULATED_VERIFIED" and
                               index[ref]["kind"] in {"DOCUMENTED", "MEASURED"} for ref in references)):
                flag("HOLD", "UNSUPPORTED_BLOCKER_RESOLUTION", None, summary, action)

    recommended = max((reason["state"] for reason in reasons), key=lambda x: PRIORITY[x], default="GO")
    ordered = sorted(reasons, key=lambda reason: (-PRIORITY[reason["state"]], reason["dimension"] or "", reason["code"]))
    return {
        "schema_version": "1.0", "policy_version": POLICY_VERSION, "synthetic": True,
        "scenario_id": identifier, "title": name, "client_id": tenant,
        "case_id": scenario["case_id"], "risk_tier": risk,
        "target_transition": "VALIDATE_TO_ADOPT",
        "recommended_state": recommended,
        "rationale": ("Every mandatory demo criterion has supplied simulated support; "
                       "human confirmation is still mandatory." if recommended == "GO" else
                       f"{len(ordered)} explicit issue(s) require a human decision before advancing."),
        "reasons": ordered, "dimensions": dimensions,
        "mandatory_dimensions": list(required), "accountable_owner": scenario["accountable_owner"],
        "non_ai_alternative": scenario["non_ai_alternative"],
        "decision_authority": "ADVISORY_ONLY", "human_approval": "NOT_RECORDED",
        "release_authorized": False, "customer_readiness_verified": False,
        "evidence_limitations": (
            "All evidence and apparent verification are fictional simulations. "
            "No independent identity, business measurement, customer approval or real deployment is verified."
        ),
    }
