"""Policy-state, evidence provenance and non-approval regression tests."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from adoption.engine import FIXTURE_PATH, evaluate, load_scenarios, sha256
from adoption.run import main, run
from app.server import create_app


class AdoptionDecisionTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_scenarios()
        self.scenarios = {s["scenario_id"]: s for s in self.bundle["scenarios"]}

    def test_four_states_are_evidence_linked_and_never_approve_release(self):
        expected = {
            "fintrust-hold": "HOLD", "retailflow-rework": "REWORK",
            "civicdata-no-go": "NO_GO", "fintrust-ideal-go": "GO",
        }
        self.assertEqual(set(self.scenarios), set(expected))
        for name, state in expected.items():
            with self.subTest(name=name):
                result = evaluate(self.scenarios[name])
                self.assertEqual(result["recommended_state"], state)
                self.assertFalse(result["release_authorized"])
                self.assertFalse(result["customer_readiness_verified"])
                self.assertEqual(result["decision_authority"], "ADVISORY_ONLY")
                self.assertEqual(result["human_approval"], "NOT_RECORDED")
                self.assertNotIn("readiness_score", result)
                self.assertTrue(result["synthetic"])

    def test_high_risk_missing_independent_review_is_hold(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["checks"] = [c for c in scenario["checks"] if c["dimension"] != "INDEPENDENT_REVIEW"]
        result = evaluate(scenario)
        self.assertEqual(result["recommended_state"], "HOLD")
        self.assertIn("MISSING_MANDATORY_CHECK", [reason["code"] for reason in result["reasons"]])

    def test_declared_or_unverified_source_cannot_satisfy_pass(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        source = next(e for e in scenario["evidence"] if e["id"] == "ft-ideal-eval")
        source["kind"] = "DECLARED"
        result = evaluate(scenario)
        self.assertEqual(result["recommended_state"], "HOLD")
        self.assertIn("INSUFFICIENT_EVIDENCE", [reason["code"] for reason in result["reasons"]])
        source["kind"] = "MEASURED"
        source["verification"] = "UNVERIFIED"
        self.assertEqual(evaluate(scenario)["recommended_state"], "HOLD")

    def test_rejected_source_blocks_pass_even_alongside_good_evidence(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["checks"][0]["evidence_ids"] = ["ft-ideal-brief", "ft-ideal-risk"]
        scenario["evidence"][1]["verification"] = "REJECTED"
        result = evaluate(scenario)
        self.assertEqual(result["recommended_state"], "HOLD")
        self.assertIn("INSUFFICIENT_EVIDENCE", [r["code"] for r in result["reasons"]])

    def test_evidence_reference_cannot_cross_outside_bundle(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["checks"][0]["evidence_ids"] = ["rf-brief"]
        with self.assertRaisesRegex(ValueError, "foreign or unknown evidence"):
            evaluate(scenario)
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["case_id"] = "retailflow-discrepancy"
        with self.assertRaisesRegex(ValueError, "matching fictional use case"):
            evaluate(scenario)

    def test_policy_can_apply_to_a_new_fictional_client_without_rewriting_rules(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["client_id"] = "newventure-demo"
        scenario["case_id"] = "newventure-internal-policy"
        scenario["scenario_id"] = "newventure-ideal"
        result = evaluate(scenario)
        self.assertEqual(result["client_id"], "newventure-demo")
        self.assertEqual(result["recommended_state"], "GO")
        self.assertFalse(result["release_authorized"])

    def test_terminal_blocker_overrides_simulated_perfect_score(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["blockers"] = [{
            "id": "test-blocker", "status": "OPEN", "severity": "TERMINAL",
            "summary": "Fictional data rights explicitly prohibited the proposed path",
            "next_action": "Stop this plan and seek another lawful approach",
        }]
        result = evaluate(scenario)
        self.assertEqual(result["recommended_state"], "NO_GO")
        self.assertEqual(result["reasons"][0]["code"], "OPEN_TERMINAL_BLOCKER")

    def test_resolved_blocker_requires_supported_documentary_reference(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["blockers"] = [{
            "id": "test-resolved", "status": "RESOLVED", "severity": "AUTHORIZATION",
            "summary": "Fictional sponsor authorized this synthetic scope",
            "next_action": "Inspect and record a real permission outside this training environment",
            "resolution_evidence_ids": ["ft-ideal-brief"],
        }]
        self.assertEqual(evaluate(scenario)["recommended_state"], "GO")
        scenario["evidence"][0]["verification"] = "UNVERIFIED"
        self.assertEqual(evaluate(scenario)["recommended_state"], "HOLD")

    def test_incomplete_and_duplicate_dimensions_are_never_silent(self):
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["checks"].append(copy.deepcopy(scenario["checks"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate(scenario)
        scenario = copy.deepcopy(self.scenarios["fintrust-ideal-go"])
        scenario["checks"] = []
        result = evaluate(scenario)
        self.assertEqual(result["recommended_state"], "HOLD")
        self.assertEqual(len(result["reasons"]), 9)

    def test_runner_reports_reproducible_fixture_provenance_and_refuses_overwrite(self):
        packet = run("fintrust-hold")
        self.assertEqual(packet["fixture"]["sha256"], sha256(FIXTURE_PATH))
        self.assertEqual(len(packet["recommendations"]), 1)
        self.assertEqual(packet["approval_status"], "NO_REAL_HUMAN_APPROVAL")
        with self.assertRaisesRegex(ValueError, "Unknown synthetic scenario"):
            run("not-a-scenario")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "decision.json"
            self.assertEqual(main(["--scenario", "fintrust-ideal-go", "--output", str(path)]), 0)
            result = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(result["recommendations"][0]["release_authorized"])
            with self.assertRaises(SystemExit):
                main(["--scenario", "fintrust-ideal-go", "--output", str(path)])

    def test_studio_exposes_frozen_synthetic_advisory_without_writing_decisions(self):
        with tempfile.TemporaryDirectory() as directory:
            with TestClient(create_app(Path(directory) / "studio.db")) as client:
                before = client.get("/api/cases/fintrust-policy-action").json()["decisions"]
                response = client.get("/api/adoption/scenarios")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()["recommendations"]), 4)
                ideal = client.get("/api/adoption/scenarios/fintrust-ideal-go")
                self.assertEqual(ideal.status_code, 200)
                self.assertEqual(ideal.json()["recommendations"][0]["recommended_state"], "GO")
                self.assertFalse(ideal.json()["recommendations"][0]["release_authorized"])
                self.assertEqual(client.get("/api/adoption/scenarios/unknown").status_code, 404)
                after = client.get("/api/cases/fintrust-policy-action").json()["decisions"]
                self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
