"""Deterministic, synthetic-only executive report from a persisted snapshot."""

from __future__ import annotations


def clean(value: object) -> str:
    """Flatten user-entered Markdown so headings/links cannot impersonate approval."""
    result = " ".join(str(value or "").split())
    for marker in ("\\", "`", "*", "_", "[", "]", "<", ">", "|"):
        result = result.replace(marker, " ")
    return result


def sentence(value: object) -> str:
    result = clean(value).rstrip(" .")
    return f"{result}." if result else ""


def executive_markdown(record: dict) -> str:
    scenario = record["scenario"]
    decision = record["recommendation"]
    evidence = {item["id"]: item for item in scenario["evidence"]}
    lines = [
        "# AI Adoption Decision Brief — SYNTHETIC DEMONSTRATION",
        "",
        "> NOT A CUSTOMER ASSESSMENT. NOT A HUMAN APPROVAL. NOT A PRODUCTION RELEASE.",
        "",
        f"**Assessment ID:** `{clean(record['assessment_id'])}`",
        f"**Fictional opportunity:** {clean(scenario['title'])}",
        f"**Synthetic client:** {clean(scenario['client_id'])}",
        f"**Synthetic use case:** {clean(scenario['case_id'])}",
        f"**Risk profile:** {clean(scenario['risk_tier'])}",
        f"**Accountable owner (self-entered, unverified):** {clean(scenario['accountable_owner'])}",
        f"**Non-AI alternative:** {clean(scenario['non_ai_alternative'])}",
        "",
        "## Advisory recommendation",
        "",
        f"**{decision['recommended_state']} — ADVISORY ONLY.**",
        "",
        clean(decision["rationale"]),
        "",
        "**Human approval:** NOT RECORDED. **Release authorized:** NO.",
        "",
        "## Conditions requiring action",
        "",
    ]
    if decision["reasons"]:
        for reason in decision["reasons"]:
            lines.append(
                f"- **{clean(reason['state'])} / {clean(reason['dimension'] or reason['code'])}:** "
                f"{sentence(reason['detail'])} **Next:** {sentence(reason['next_action'])}"
            )
    else:
        lines.append("- No outstanding issues were entered in this **fictional** scenario. This does not verify actual readiness.")
    lines.extend(["", "## Dimension-level traceability", ""])
    for check in decision["dimensions"]:
        lines.extend([
            f"### {clean(check['dimension'])} — {clean(check['status'])}", "",
            clean(check["rationale"]), "",
            f"**Simulated evidence support:** {'QUALIFYING FICTIONAL SOURCE' if check['support_valid_for_demo'] else 'NOT ESTABLISHED'}",
            f"**Next action:** {clean(check['next_action'])}",
        ])
        if check["evidence_ids"]:
            for identifier in check["evidence_ids"]:
                source = evidence[identifier]
                lines.append(
                    f"- `{clean(identifier)}`: {clean(source['kind'])}, "
                    f"{clean(source['verification'])} — {clean(source['source'])}"
                )
        else:
            lines.append("- No evidence attached.")
        lines.append("")
    lines.extend([
        "## Integrity and limitations", "",
        f"- **Frozen input SHA-256:** `{clean(record['source_sha256'])}`",
        f"- **Policy version:** `{clean(record['policy_version'])}`",
        f"- **Snapshot created (UTC):** {clean(record['created_at'])}",
        "- Source data and claimed verification are fictional and self-declared; no independent reviewer identity is authenticated.",
        "- The result is a recommendation, not a stage decision and not evidence of any actual deployment or cost.",
        "- This assessment was saved separately from the Studio's human-decision history.",
        "- A real pilot requires separately authorized customer data, reviews, ownership, thresholds and budgets.",
        "",
    ])
    return "\n".join(lines)
