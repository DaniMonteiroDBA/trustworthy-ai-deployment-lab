"""Validated input boundary for a local-only, synthetic assessment workshop."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DraftEvidence(StrictModel):
    id: str = Field(min_length=3, max_length=80, pattern=r"^[a-z0-9][a-z0-9-]*$")
    kind: Literal["DECLARED", "DOCUMENTED", "MEASURED", "INFERRED"]
    verification: Literal["UNVERIFIED", "SIMULATED_VERIFIED", "REJECTED"]
    synthetic: Literal[True]
    source: str = Field(min_length=3, max_length=240)


class DraftCheck(StrictModel):
    dimension: Literal[
        "BUSINESS_VALUE", "NON_AI_ALTERNATIVE", "DATA_GOVERNANCE",
        "AI_EVALUATION", "SECURITY_PRIVACY", "ECONOMICS", "OPERATIONS",
        "HUMAN_ACCOUNTABILITY", "INDEPENDENT_REVIEW",
    ]
    status: Literal["PASS", "UNKNOWN", "GAP", "FAIL"]
    evidence_ids: list[str] = Field(max_length=20)
    rationale: str = Field(min_length=12, max_length=1200)
    next_action: str = Field(min_length=10, max_length=1200)


class DraftBlocker(StrictModel):
    id: str = Field(min_length=3, max_length=80, pattern=r"^[a-z0-9][a-z0-9-]*$")
    severity: Literal["TERMINAL", "AUTHORIZATION", "REMEDIABLE"]
    status: Literal["OPEN", "RESOLVED"]
    summary: str = Field(min_length=12, max_length=1200)
    next_action: str = Field(min_length=10, max_length=1200)
    resolution_evidence_ids: list[str] | None = Field(default=None, max_length=20)


class SyntheticAssessmentInput(StrictModel):
    synthetic: Literal[True]
    confirmed_fictional: Literal[True]
    title: str = Field(min_length=8, max_length=120)
    client_id: str = Field(min_length=8, max_length=70, pattern=r"^[a-z0-9][a-z0-9-]*-demo$")
    case_id: str = Field(min_length=4, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    accountable_owner: str = Field(min_length=3, max_length=120)
    non_ai_alternative: str = Field(min_length=8, max_length=500)
    evidence: list[DraftEvidence] = Field(default_factory=list, max_length=60)
    checks: list[DraftCheck] = Field(min_length=1, max_length=30)
    blockers: list[DraftBlocker] = Field(default_factory=list, max_length=30)
