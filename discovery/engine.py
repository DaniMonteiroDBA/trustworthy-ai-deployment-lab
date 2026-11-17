"""Deterministic, non-scored discovery triage and conditional 30/60/90 actions."""

from __future__ import annotations

import re


POLICY_VERSION = "0.1.0"
PRIORITY = {"SHORTLIST_FOR_POV": 0, "REFINE_SCOPE": 1, "DISCOVERY_HOLD": 2, "DO_NOT_PURSUE": 3}


def evaluate(candidate: dict) -> dict:
    """Evaluate a fictional opportunity. SHORTLIST is NOT a production/pilot approval."""
    if candidate.get("synthetic") is not True:
        raise ValueError("Only synthetic opportunities are accepted")
    client = candidate.get("client_id")
    case = candidate.get("case_id")
    if (not isinstance(client, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}-demo", client)
            or not isinstance(case, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{3,100}", case)
            or not case.startswith(client.removesuffix("-demo") + "-")):
        raise ValueError("Use a fictional client ID and matching use-case prefix")

    reasons: list[dict] = []

    def flag(state: str, key: str, issue: str, action: str) -> None:
        reasons.append({"state": state, "key": key, "issue": issue, "next_action": action})

    if candidate["data_permission"] == "DENIED":
        flag("DO_NOT_PURSUE", "DATA_PERMISSION", "Data use is prohibited in this fictional design", "Choose an authorized data path or stop")
    elif candidate["data_permission"] == "RESTRICTED":
        flag("DISCOVERY_HOLD", "DATA_PERMISSION", "Restrictions are not resolved", "Document lawful purpose, permissions and constraints")
    elif candidate["data_permission"] == "UNKNOWN":
        flag("DISCOVERY_HOLD", "DATA_PERMISSION", "Data authority is not established", "Identify an accountable source owner and obtain approval")
    elif len(candidate["permission_source"].strip()) < 8:
        flag("DISCOVERY_HOLD", "DATA_PERMISSION", "Simulated permission lacks an attributable source", "Describe the fictional permission record")

    if candidate["data_quality"] == "UNUSABLE":
        flag("DO_NOT_PURSUE", "DATA_QUALITY", "Available data is unsuitable for this proposed path", "Use another authorized approach or stop")
    elif candidate["data_quality"] == "GAP":
        flag("REFINE_SCOPE", "DATA_QUALITY", "Source coverage or fitness requires repair", "Define sampling, profiling and remediation criteria")
    elif candidate["data_quality"] == "UNKNOWN":
        flag("DISCOVERY_HOLD", "DATA_QUALITY", "Data fitness has not been assessed", "Document provenance, coverage, freshness and permitted use")

    if candidate["feasibility"] == "BLOCKED":
        flag("DO_NOT_PURSUE", "FEASIBILITY", "Delivery path is blocked", "Choose a different feasible scope")
    elif candidate["feasibility"] == "GAP":
        flag("REFINE_SCOPE", "FEASIBILITY", "Integration or operating dependency is unresolved", "Plan a bounded feasibility spike and accountable owners")
    elif candidate["feasibility"] == "UNKNOWN":
        flag("DISCOVERY_HOLD", "FEASIBILITY", "Delivery feasibility has not been assessed", "Map integrations, operating requirements and dependencies")

    if candidate["value_status"] == "UNSUPPORTED":
        flag("DO_NOT_PURSUE", "VALUE", "No credible value hypothesis remains for the proposed scope", "Prefer the non-AI alternative or revisit the problem")
    elif candidate["value_status"] == "UNKNOWN":
        flag("DISCOVERY_HOLD", "VALUE", "Benefit hypothesis is not yet supported", "Validate impact with a fictional sponsor and user baseline")

    if candidate["baseline_status"] == "UNKNOWN" or len(candidate["baseline_source"].strip()) < 8:
        flag("DISCOVERY_HOLD", "BASELINE", "A comparable measured baseline is not established, even in the simulation", "Define baseline method, population and source")
    if candidate["alternative_status"] == "NOT_COMPARED" or len(candidate["alternative_source"].strip()) < 8:
        flag("DISCOVERY_HOLD", "NON_AI_COMPARATOR", "The non-AI option has no documented comparative evaluation", "Compare cost, quality and complexity against the current workflow")
    if candidate["adoption_readiness"] == "GAP":
        flag("REFINE_SCOPE", "ADOPTION", "Change, enablement or ownership gaps are recorded", "Create accountable enablement and support plan")
    elif candidate["adoption_readiness"] == "UNKNOWN":
        flag("DISCOVERY_HOLD", "ADOPTION", "Adoption ownership and readiness are unknown", "Identify impacted teams, owners and training needs")
    if candidate["risk_tier"] == "HIGH" and candidate["independent_review"] != "PLANNED_SIMULATED":
        flag("DISCOVERY_HOLD", "INDEPENDENT_REVIEW", "High-risk evaluation lacks an independent-review plan", "Name a reviewer role independent from delivery")

    reasons.sort(key=lambda reason: (-PRIORITY[reason["state"]], reason["key"]))
    recommendation = max((r["state"] for r in reasons), key=lambda s: PRIORITY[s], default="SHORTLIST_FOR_POV")
    issues = {reason["key"] for reason in reasons}

    first = [
        "Confirm the fictional sponsor, user journey, opportunity boundary and non-AI comparator.",
        "Document the proposed success metric, test population, baseline method and data-use authority.",
    ]
    if "DATA_PERMISSION" in issues or "DATA_QUALITY" in issues:
        first.append("Resolve the recorded data permission/fitness questions before any model or workflow access.")
    if "BASELINE" in issues or "NON_AI_COMPARATOR" in issues:
        first.append("Collect comparable simulated baseline and non-AI alternative evidence for a new review.")

    if recommendation == "DO_NOT_PURSUE":
        second = ["Stop the current fictional AI path and examine a compliant or simpler alternative.",
                  "Revisit the opportunity only after the terminal conditions materially change."]
        third = ["Record the fictional closure rationale and residual risks.",
                 "Review whether the non-AI path solves the original problem, without claiming measured impact."]
    elif recommendation == "DISCOVERY_HOLD":
        second = ["Complete missing discovery evidence, resolve permissions and reassess feasibility and value.",
                  "Prepare a bounded offline test design only if the data and security owners authorize it."]
        third = ["Re-run the discovery gates and decide with a human whether a proof of value is justified.",
                 "Define any future training, monitoring and rollback responsibilities before rollout planning."]
    else:
        second = ["Design a bounded proof of value with predeclared baseline, failure tests and evaluation criteria.",
                  "Use permitted fictional fixtures; obtain separate human approval before any real-data test."]
        if recommendation == "REFINE_SCOPE":
            second.insert(0, "Repair the documented quality, feasibility or change-management gaps and reassess.")
        third = ["Compare proof-of-value evidence to the non-AI option and review failures independently.",
                 "If humans approve a next step, plan enablement, monitoring, budget and rollback before deployment."]

    return {
        "schema_version": "1.0", "policy_version": POLICY_VERSION, "synthetic": True,
        "client_id": client, "case_id": case, "risk_tier": candidate["risk_tier"],
        "recommended_state": recommendation, "portfolio_bucket": recommendation,
        "decision_scope": "EARLY_DISCOVERY_TRIAGE", "decision_authority": "ADVISORY_ONLY",
        "human_approval": "NOT_RECORDED", "pov_authorized": False, "release_authorized": False,
        "customer_readiness_verified": False, "reasons": reasons,
        "basis": "Self-declared simulated inputs, not authenticated source verification or observed business outcome.",
        "roadmap": [
            {"window": "DAYS_01_30", "focus": "Discovery and evidence", "actions": first},
            {"window": "DAYS_31_60", "focus": "Conditional design or scope repair", "actions": second},
            {"window": "DAYS_61_90", "focus": "Human decision and handoff", "actions": third},
        ],
    }
