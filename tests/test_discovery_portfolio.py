"""Evidence-first early discovery policy, independent persistence, and no-approval tests."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.server import create_app


def discovery() -> dict:
    return {
        "synthetic": True, "confirmed_fictional": True,
        "client_id": "fintrust-demo", "case_id": "fintrust-policy-action",
        "title": "Fictional responsible policy assistant", "sector": "Financial services",
        "risk_tier": "HIGH", "business_owner": "Fictional procurement sponsor",
        "affected_users": "Fictional operations analysts and policy reviewers",
        "problem": "In this imaginary organization, employees cannot find the right policy version reliably.",
        "current_workflow": "Manual policy portal search with human escalation",
        "success_metric": "Percentage of supported policy references (not measured)",
        "expected_benefit": "Reduce fictional manual search effort without unauthorized decisions",
        "non_ai_alternative": "Maintain a curated portal and rule-based decision tree",
        "baseline_status": "UNKNOWN", "baseline_source": "",
        "value_status": "UNKNOWN", "alternative_status": "NOT_COMPARED", "alternative_source": "",
        "data_permission": "UNKNOWN", "permission_source": "",
        "data_quality": "UNKNOWN", "feasibility": "UNKNOWN", "adoption_readiness": "UNKNOWN",
        "independent_review": "UNKNOWN", "constraints": ["Fictional policy corpus incomplete"],
    }


def invented_best_case() -> dict:
    row = discovery()
    row.update({
        "baseline_status": "SIMULATED_MEASURED", "baseline_source": "Invented measured baseline worksheet",
        "value_status": "PLAUSIBLE_SIMULATED", "alternative_status": "COMPARED_SIMULATED",
        "alternative_source": "Imaginary non-AI options comparison note",
        "data_permission": "GRANTED_SIMULATED", "permission_source": "Fictional permission record only",
        "data_quality": "SUITABLE_SIMULATED", "feasibility": "FEASIBLE_SIMULATED",
        "adoption_readiness": "PLAN_SIMULATED", "independent_review": "PLANNED_SIMULATED",
    })
    return row


class FictionalDiscoveryPortfolioTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "studio.db"
        self.client = TestClient(create_app(self.path))
        self.addCleanup(self.client.close)

    def test_unknown_inputs_hold_with_specific_gap_actions_and_report(self):
        before = self.client.get("/api/cases/fintrust-policy-action").json()["decisions"]
        response = self.client.post("/api/discovery/assessments", json=discovery())
        self.assertEqual(response.status_code, 201, response.text)
        record = response.json()
        result = record["recommendation"]
        self.assertEqual(result["recommended_state"], "DISCOVERY_HOLD")
        self.assertTrue(any(r["key"] == "BASELINE" for r in result["reasons"]))
        self.assertTrue(any(r["key"] == "INDEPENDENT_REVIEW" for r in result["reasons"]))
        self.assertFalse(result["pov_authorized"])
        self.assertFalse(result["release_authorized"])
        self.assertEqual([row["window"] for row in result["roadmap"]],
                         ["DAYS_01_30", "DAYS_31_60", "DAYS_61_90"])
        self.assertNotIn("confirmed_fictional", record["input"])
        canonical = json.dumps(record["input"], sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(record["source_sha256"], hashlib.sha256(canonical.encode()).hexdigest())
        self.assertEqual(self.client.get("/api/cases/fintrust-policy-action").json()["decisions"], before)
        report = self.client.get(f"/api/discovery/assessments/{record['discovery_id']}/report")
        self.assertEqual(report.status_code, 200)
        self.assertIn("NO CUSTOMER VERIFICATION", report.text)
        self.assertIn("DAYS 01 30", report.text)
        self.assertIn(record["source_sha256"], report.text)

    def test_shortlist_is_not_an_approved_pilot_even_when_everything_is_invented(self):
        response = self.client.post("/api/discovery/assessments", json=invented_best_case())
        self.assertEqual(response.status_code, 201, response.text)
        result = response.json()["recommendation"]
        self.assertEqual(result["recommended_state"], "SHORTLIST_FOR_POV")
        self.assertEqual(result["decision_scope"], "EARLY_DISCOVERY_TRIAGE")
        self.assertEqual(result["human_approval"], "NOT_RECORDED")
        self.assertEqual(result["reasons"], [])
        self.assertFalse(result["customer_readiness_verified"])
        self.assertFalse(result["pov_authorized"])

    def test_terminal_data_denial_precedes_hold_and_refinement(self):
        candidate = discovery()
        candidate["data_permission"] = "DENIED"
        candidate["feasibility"] = "GAP"
        result = self.client.post("/api/discovery/assessments", json=candidate).json()["recommendation"]
        self.assertEqual(result["recommended_state"], "DO_NOT_PURSUE")
        self.assertEqual(result["reasons"][0]["state"], "DO_NOT_PURSUE")
        self.assertIn("Stop the current fictional AI path", result["roadmap"][1]["actions"][0])

    def test_high_risk_requires_independent_plan_but_low_risk_does_not(self):
        candidate = invented_best_case()
        candidate["independent_review"] = "UNKNOWN"
        high = self.client.post("/api/discovery/assessments", json=candidate).json()["recommendation"]
        self.assertEqual(high["recommended_state"], "DISCOVERY_HOLD")
        candidate["risk_tier"] = "LOW"
        low = self.client.post("/api/discovery/assessments", json=candidate).json()["recommendation"]
        self.assertEqual(low["recommended_state"], "SHORTLIST_FOR_POV")

    def test_extra_fields_cross_account_case_and_real_data_flags_are_rejected(self):
        for key, value in (
            ("confirmed_fictional", False), ("synthetic", False),
            ("client_id", "actual-client"), ("case_id", "othercompany-internal"),
        ):
            candidate = discovery()
            candidate[key] = value
            response = self.client.post("/api/discovery/assessments", json=candidate)
            self.assertEqual(response.status_code, 422, (key, response.text))
        candidate = discovery()
        candidate["secret_key"] = "do-not-persist"
        self.assertEqual(self.client.post("/api/discovery/assessments", json=candidate).status_code, 422)
        candidate = discovery()
        candidate["constraints"] = ["short"]
        self.assertEqual(self.client.post("/api/discovery/assessments", json=candidate).status_code, 422)
        self.assertEqual(self.client.get("/api/discovery/assessments").json(), [])

    def test_snapshot_history_persists_and_does_not_overwrite_prior_versions(self):
        first = self.client.post("/api/discovery/assessments", json=discovery()).json()
        changed = copy.deepcopy(discovery())
        changed["data_permission"] = "DENIED"
        second = self.client.post("/api/discovery/assessments", json=changed).json()
        self.assertNotEqual(first["discovery_id"], second["discovery_id"])
        self.assertEqual(self.client.get("/api/discovery/assessments").json()[0]["discovery_id"], second["discovery_id"])
        self.assertEqual(self.client.get(f"/api/discovery/assessments/{first['discovery_id']}").json(), first)
        with TestClient(create_app(self.path)) as restarted:
            self.assertEqual(restarted.get(f"/api/discovery/assessments/{second['discovery_id']}").json(), second)
        self.assertEqual(self.client.get("/api/discovery/assessments/no-such-id/report").status_code, 404)

    def test_markdown_cannot_inject_new_approval_heading_and_frontend_is_served(self):
        candidate = discovery()
        candidate["title"] = "Fictional policy question\n## Approved for production"
        response = self.client.post("/api/discovery/assessments", json=candidate)
        self.assertEqual(response.status_code, 201, response.text)
        record = response.json()
        report = self.client.get(f"/api/discovery/assessments/{record['discovery_id']}/report").text
        self.assertNotIn("\n## Approved for production", report)
        self.assertIn("**Release authorized:** NO", report)
        self.assertIn("FICTIONAL CONSULTING EXERCISE", report)
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn('id="discovery-create-button"', page.text)
        self.assertIn('id="discovery-form"', page.text)


if __name__ == "__main__":
    unittest.main()
