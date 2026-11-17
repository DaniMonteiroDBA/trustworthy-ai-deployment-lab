"""Typed boundary for explicitly fictional early-stage AI opportunity discovery."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class DiscoveryInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    synthetic: Literal[True]
    confirmed_fictional: Literal[True]
    client_id: str = Field(min_length=8, max_length=70, pattern=r"^[a-z0-9][a-z0-9-]*-demo$")
    case_id: str = Field(min_length=4, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    title: str = Field(min_length=8, max_length=120)
    sector: str = Field(min_length=3, max_length=80)
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    business_owner: str = Field(min_length=3, max_length=120)
    affected_users: str = Field(min_length=8, max_length=240)
    problem: str = Field(min_length=20, max_length=1500)
    current_workflow: str = Field(min_length=12, max_length=700)
    success_metric: str = Field(min_length=8, max_length=400)
    expected_benefit: str = Field(min_length=12, max_length=700)
    non_ai_alternative: str = Field(min_length=12, max_length=700)
    baseline_status: Literal["UNKNOWN", "SIMULATED_MEASURED"]
    baseline_source: str = Field(default="", max_length=240)
    value_status: Literal["UNKNOWN", "PLAUSIBLE_SIMULATED", "UNSUPPORTED"]
    alternative_status: Literal["NOT_COMPARED", "COMPARED_SIMULATED"]
    alternative_source: str = Field(default="", max_length=240)
    data_permission: Literal["UNKNOWN", "GRANTED_SIMULATED", "RESTRICTED", "DENIED"]
    permission_source: str = Field(default="", max_length=240)
    data_quality: Literal["UNKNOWN", "SUITABLE_SIMULATED", "GAP", "UNUSABLE"]
    feasibility: Literal["UNKNOWN", "FEASIBLE_SIMULATED", "GAP", "BLOCKED"]
    adoption_readiness: Literal["UNKNOWN", "PLAN_SIMULATED", "GAP"]
    independent_review: Literal["UNKNOWN", "PLANNED_SIMULATED"]
    constraints: list[Annotated[str, Field(min_length=8, max_length=300)]] = Field(default_factory=list, max_length=12)
