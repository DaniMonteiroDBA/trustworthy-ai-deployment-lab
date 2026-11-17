"""Executive-readable, non-generative brief from a frozen fictional discovery record."""

from __future__ import annotations

from adoption.report import clean, sentence


def executive_markdown(record: dict) -> str:
    source = record["input"]
    result = record["recommendation"]
    lines = [
        "# AI Opportunity Discovery Brief — SYNTHETIC DEMONSTRATION", "",
        "> FICTIONAL CONSULTING EXERCISE. NO CUSTOMER VERIFICATION, HUMAN APPROVAL OR DEPLOYMENT AUTHORIZATION.", "",
        f"**Snapshot:** `{clean(record['discovery_id'])}`",
        f"**Opportunity:** {clean(source['title'])}",
        f"**Fictional client:** {clean(source['client_id'])} · **Sector:** {clean(source['sector'])}",
        f"**Use case:** {clean(source['case_id'])} · **Risk:** {clean(source['risk_tier'])}",
        f"**Sponsor (self-entered):** {clean(source['business_owner'])}",
        f"**Affected users:** {clean(source['affected_users'])}", "",
        "## Problem and alternatives", "",
        f"**Problem:** {clean(source['problem'])}",
        f"**Current workflow:** {clean(source['current_workflow'])}",
        f"**Success measure to verify:** {clean(source['success_metric'])}",
        f"**Expected benefit (hypothesis, NOT measured impact):** {clean(source['expected_benefit'])}",
        f"**Non-AI alternative:** {clean(source['non_ai_alternative'])}", "",
        "## Discovery triage", "",
        f"**{clean(result['recommended_state'])} — ADVISORY ONLY.**",
        "**Portfolio position:** a categorical bucket, not a score or a rank among peers.",
        "**Human approval:** NOT RECORDED. **Proof-of-value authorized:** NO. **Release authorized:** NO.", "",
    ]
    if result["reasons"]:
        for reason in result["reasons"]:
            lines.append(f"- **{clean(reason['state'])} / {clean(reason['key'])}:** "
                         f"{sentence(reason['issue'])} **Next:** {sentence(reason['next_action'])}")
    else:
        lines.append("- All **invented** discovery assumptions satisfy this illustrative shortlist policy. Actual evidence and human review remain absent.")
    lines.extend(["", "## Declared discovery evidence (not independently authenticated)", ""])
    for field, label in (
        ("baseline_status", "Baseline status"), ("baseline_source", "Baseline source"),
        ("value_status", "Value status"), ("alternative_status", "Non-AI comparison status"),
        ("alternative_source", "Non-AI comparison source"),
        ("data_permission", "Data permission"), ("permission_source", "Permission source"),
        ("data_quality", "Data fitness"), ("feasibility", "Delivery feasibility"),
        ("adoption_readiness", "Adoption readiness"),
        ("independent_review", "Independent-review plan"),
    ):
        lines.append(f"- **{label}:** {clean(source[field]) or 'Not provided'}")
    if source["constraints"]:
        lines.extend(["", "**Illustrative constraints:**"])
        lines.extend(f"- {clean(item)}" for item in source["constraints"])
    lines.extend(["", "## Conditional 30 / 60 / 90-day discovery plan", ""])
    for step in result["roadmap"]:
        lines.append(f"### {clean(step['window'].replace('_', ' '))} — {clean(step['focus'])}")
        lines.append("")
        lines.extend(f"- {clean(action)}" for action in step["actions"])
        lines.append("")
    lines.extend([
        "## Provenance and authority boundaries", "",
        f"- **Frozen input SHA-256:** `{clean(record['source_sha256'])}`",
        f"- **Policy version:** `{clean(record['policy_version'])}`",
        f"- **Created (UTC):** {clean(record['created_at'])}",
        "- The SHA-256 is a local input fingerprint, not a tamper-proof signature or document authentication.",
        "- All alleged measurements and permissions are fictional statuses with user-entered descriptions.",
        "- This report does not approve a pilot, a deployment, a spend or any change in human stage gates.",
        "- A real account portfolio requires verified inputs and accountable human prioritization; tied buckets are not ranked.",
        "",
    ])
    return "\n".join(lines)
