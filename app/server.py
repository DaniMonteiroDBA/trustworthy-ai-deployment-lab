"""AI Value & Adoption Studio: local, synthetic-only FastAPI vertical slice.

WARNING: no user authentication, corporate authorization, or production-grade
tenant isolation is implemented. This app must not be exposed with real data.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.store import STAGES, StudioStore


ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "studio"


class EvidenceInput(BaseModel):
    # MEASURED will be recorded only by the future evaluation/runtime pipeline.
    evidence_class: Literal["DECLARED", "DOCUMENTED", "INFERRED"]
    source: str = Field(min_length=4, max_length=240)
    summary: str = Field(min_length=12, max_length=2000)


class EvidenceReviewInput(BaseModel):
    status: Literal["VERIFIED", "REJECTED"]
    reviewer: str = Field(min_length=3, max_length=120)
    rationale: str = Field(min_length=10, max_length=1000)


class DecisionInput(BaseModel):
    stage: Literal["DISCOVER", "ASSESS", "PRIORITIZE", "ARCHITECT", "VALIDATE", "ADOPT", "MEASURE_IMPROVE"]
    status: Literal["IN_REVIEW", "GO", "REWORK", "HOLD", "NO_GO"]
    owner: str = Field(min_length=3, max_length=120)
    rationale: str = Field(min_length=12, max_length=2000)
    evidence_ids: list[str] = Field(default_factory=list, max_length=50)
    blockers: list[str] = Field(default_factory=list, max_length=30)
    alternatives: list[str] = Field(default_factory=list, max_length=30)


def _clean_list(items: list[str]) -> list[str]:
    return [s.strip() for s in items if isinstance(s, str) and s.strip()]


def make_executive_report(record: dict) -> str:
    """Render a transparent deterministic report, not an LLM summary."""
    evidence = {e["evidence_id"]: e for e in record["evidence"]}
    latest = {row["stage"]: row["decision"] for row in record["stage_states"] if row["decision"]}
    lines = [
        f"# {record['client_name']} — AI Opportunity Brief",
        "",
        "> SYNTHETIC DEMONSTRATION — NOT A REAL CUSTOMER ASSESSMENT OR DEPLOYMENT.",
        "",
        f"**Use case:** {record['title']}",
        f"**Sector:** {record['sector']}",
        f"**Business owner (fictional):** {record['business_owner']}",
        f"**Risk profile (illustrative):** {record['risk_tier']}",
        "",
        "## Business opportunity",
        "",
        record["problem"],
        "",
        f"**Proposed success measure:** {record['success_metric']}",
        f"**Non-AI alternative:** {record['non_ai_alternative']}",
        "",
        "## Stage decisions",
        "",
    ]
    for stage in STAGES:
        decision = latest.get(stage)
        if decision is None:
            lines.extend([f"### {stage} — NOT APPROVED", "", "No effective human review decision is available.", ""])
            continue
        lines.extend([
            f"### {stage} — {decision['status']}", "",
            f"**Reviewer name (unverified, demo only):** {decision['owner']}",
            f"**Rationale:** {decision['rationale']}",
            f"**Open blockers:** {', '.join(decision['blockers']) or 'None recorded'}",
            "",
        ])
        for identifier in decision["evidence_ids"]:
            item = evidence.get(identifier)
            if item:
                lines.append(
                    f"- `{identifier}` [{item['evidence_class']}, {item['verification_status']}]: {item['summary']}"
                )
        lines.append("")
    lines.extend([
        "## Current assessment limitations", "",
        "- All organization details, stakeholder names and records are synthetic.",
        "- Human reviewer names are self-entered in an unauthenticated local demonstration.",
        "- No measured operational or business outcomes have been captured.",
        "- No AI runtime, production approval, real customer onboarding or compliance certification is implied.",
        "- A valid stage decision authorizes only the next bounded step in the demo methodology.",
        "",
    ])
    return "\n".join(lines)


def create_app(database_path: Path | str | None = None) -> FastAPI:
    path = Path(database_path or os.environ.get("STUDIO_DB_PATH", str(ROOT / "data" / "studio.db")))
    store = StudioStore(path)
    application = FastAPI(title="Trustworthy AI Adoption Studio", version="0.1.0")
    application.state.store = store

    @application.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "mode": "synthetic_local_demo", "version": "0.1.0"}

    @application.get("/api/clients")
    def clients() -> list[dict]:
        return store.clients()

    @application.get("/api/clients/{client_id}")
    def client(client_id: str) -> dict:
        result = store.client(client_id)
        if result is None:
            raise HTTPException(404, "Synthetic client not found")
        return result

    @application.get("/api/cases/{case_id}")
    def case(case_id: str) -> dict:
        result = store.case(case_id)
        if result is None:
            raise HTTPException(404, "Use case not found")
        return result

    @application.post("/api/cases/{case_id}/evidence", status_code=201)
    def add_evidence(case_id: str, payload: EvidenceInput) -> dict:
        if store.case(case_id) is None:
            raise HTTPException(404, "Use case not found")
        # Users can only add unverified synthetic declarations, documents or inferences.
        return store.add_evidence(case_id, payload.evidence_class, payload.source.strip(), payload.summary.strip())

    @application.post("/api/evidence/{evidence_id}/review")
    def review_evidence(evidence_id: str, payload: EvidenceReviewInput) -> dict:
        if store.evidence(evidence_id) is None:
            raise HTTPException(404, "Evidence not found")
        # Self-entered reviewer: local demonstration only; not an identity proof.
        return store.review_evidence(
            evidence_id, payload.status, payload.reviewer.strip(), payload.rationale.strip()
        )

    @application.post("/api/cases/{case_id}/decisions", status_code=201)
    def decide(case_id: str, payload: DecisionInput) -> dict:
        record = store.case(case_id)
        if record is None:
            raise HTTPException(404, "Use case not found")

        stage_state = next(s for s in record["stage_states"] if s["stage"] == payload.stage)
        if stage_state["status"] == "LOCKED":
            raise HTTPException(409, "Previous stage has not received a GO decision")

        refs = list(dict.fromkeys(payload.evidence_ids))
        evidence = {e["evidence_id"]: e for e in record["evidence"]}
        unknown = [identifier for identifier in refs if identifier not in evidence]
        if unknown:
            raise HTTPException(422, f"Evidence does not belong to this case: {unknown}")

        blockers = _clean_list(payload.blockers)
        alternatives = _clean_list(payload.alternatives)
        if payload.status == "GO":
            if blockers:
                raise HTTPException(409, "Resolve recorded blockers before GO")
            verified_basis = any(
                evidence[eid]["verification_status"] == "VERIFIED"
                and evidence[eid]["evidence_class"] in ("DOCUMENTED", "MEASURED")
                for eid in refs
            )
            if not verified_basis:
                raise HTTPException(409, "GO requires referenced, verified documentary or measured evidence")
            if payload.stage in ("VALIDATE", "MEASURE_IMPROVE"):
                # Real measurement ingestion belongs to M2/M3, not this demo.
                if not any(
                    evidence[eid]["evidence_class"] == "MEASURED"
                    and evidence[eid]["verification_status"] == "VERIFIED"
                    for eid in refs
                ):
                    raise HTTPException(409, "This gate requires measured evidence; no evaluation engine is connected yet")

        return store.add_decision(
            case_id, payload.stage, payload.status, payload.owner.strip(), payload.rationale.strip(),
            refs, blockers, alternatives,
        )

    @application.get("/api/cases/{case_id}/executive-report", response_class=PlainTextResponse)
    def executive_report(case_id: str) -> str:
        record = store.case(case_id)
        if record is None:
            raise HTTPException(404, "Use case not found")
        return make_executive_report(record)

    application.mount("/assets", StaticFiles(directory=str(STATIC_DIR)), name="assets")

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    return application


app = create_app()
