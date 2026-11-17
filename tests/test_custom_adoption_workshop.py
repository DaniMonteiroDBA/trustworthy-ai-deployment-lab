"""Local workshop persistence, trust-boundary and executive-report checks."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from adoption.engine import load_scenarios
from app.server import create_app


class CustomAdoptionWorkshopTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.client = TestClient(create_app(Path(self.temporary.name) / "studio.db"))
        self.addCleanup(self.client.close)
        self.examples = {s["scenario_id"]: s for s in load_scenarios()["scenarios"]}

    def draft(self, name="fintrust-hold"):
        candidate = copy.deepcopy(self.examples[name])
        candidate.pop("scenario_id")
        candidate["confirmed_fictional"] = True
        return candidate

    def test_create_persists_immutable_snapshot_separate_from_stage_decisions(self):
        before = self.client.get("/api/cases/fintrust-policy-action").json()["decisions"]
        result = self.client.post("/api/adoption/assessments", json=self.draft())
        self.assertEqual(result.status_code, 201, result.text)
        record = result.json()
        self.assertEqual(record["recommendation"]["recommended_state"], "HOLD")
        self.assertFalse(record["recommendation"]["release_authorized"])
        self.assertEqual(record["recommendation"]["human_approval"], "NOT_RECORDED")
        self.assertNotIn("confirmed_fictional", record["scenario"])
        serialized = json.dumps(record["scenario"], sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(record["source_sha256"], hashlib.sha256(serialized.encode("utf-8")).hexdigest())
        same = self.client.get(f"/api/adoption/assessments/{record['assessment_id']}")
        self.assertEqual(same.status_code, 200)
        self.assertEqual(same.json(), record)
        self.assertEqual(self.client.get("/api/cases/fintrust-policy-action").json()["decisions"], before)

    def test_repeat_creates_a_distinct_record_not_a_silent_overwrite(self):
        first = self.client.post("/api/adoption/assessments", json=self.draft()).json()
        second = self.client.post("/api/adoption/assessments", json=self.draft()).json()
        self.assertNotEqual(first["assessment_id"], second["assessment_id"])
        self.assertNotEqual(first["scenario"]["scenario_id"], second["scenario"]["scenario_id"])
        listing = self.client.get("/api/adoption/assessments").json()
        self.assertEqual(len(listing), 2)
        self.assertEqual(listing[0]["assessment_id"], second["assessment_id"])
        self.assertEqual(self.client.get(f"/api/adoption/assessments/{first['assessment_id']}").json(), first)

    def test_simulated_go_is_still_not_customer_ready_or_approved(self):
        response = self.client.post("/api/adoption/assessments", json=self.draft("fintrust-ideal-go"))
        self.assertEqual(response.status_code, 201, response.text)
        decision = response.json()["recommendation"]
        self.assertEqual(decision["recommended_state"], "GO")
        self.assertEqual(decision["decision_authority"], "ADVISORY_ONLY")
        self.assertFalse(decision["customer_readiness_verified"])
        self.assertFalse(decision["release_authorized"])

    def test_unverified_pass_and_missing_sources_are_hold(self):
        draft = self.draft("fintrust-ideal-go")
        for source in draft["evidence"]:
            source["verification"] = "UNVERIFIED"
        response = self.client.post("/api/adoption/assessments", json=draft)
        self.assertEqual(response.status_code, 201, response.text)
        result = response.json()["recommendation"]
        self.assertEqual(result["recommended_state"], "HOLD")
        self.assertTrue(any(r["code"] == "INSUFFICIENT_EVIDENCE" for r in result["reasons"]))
        draft = self.draft("fintrust-ideal-go")
        draft["evidence"] = []
        for check in draft["checks"]:
            check["evidence_ids"] = []
            check["status"] = "UNKNOWN"
        self.assertEqual(self.client.post("/api/adoption/assessments", json=draft).json()["recommendation"]["recommended_state"], "HOLD")

    def test_open_blocker_precedence_is_explicit_for_new_workshop_inputs(self):
        draft = self.draft("fintrust-ideal-go")
        draft["blockers"] = [
            {"id": "stop-demo", "severity": "TERMINAL", "status": "OPEN",
             "summary": "Fictional prohibited data use", "next_action": "Abandon prohibited input"},
            {"id": "auth-demo", "severity": "AUTHORIZATION", "status": "OPEN",
             "summary": "No fictional sponsor permission", "next_action": "Request documented approval"},
            {"id": "fix-demo", "severity": "REMEDIABLE", "status": "OPEN",
             "summary": "Illustrative monitoring absent", "next_action": "Document monitoring plan"},
        ]
        response = self.client.post("/api/adoption/assessments", json=draft)
        self.assertEqual(response.status_code, 201, response.text)
        result = response.json()["recommendation"]
        self.assertEqual(result["recommended_state"], "NO_GO")
        self.assertEqual([r["state"] for r in result["reasons"]], ["NO_GO", "HOLD", "REWORK"])

    def test_high_risk_without_independent_review_must_hold(self):
        draft = self.draft("fintrust-ideal-go")
        draft["checks"] = [c for c in draft["checks"] if c["dimension"] != "INDEPENDENT_REVIEW"]
        response = self.client.post("/api/adoption/assessments", json=draft)
        self.assertEqual(response.status_code, 201, response.text)
        result = response.json()["recommendation"]
        self.assertEqual(result["recommended_state"], "HOLD")
        self.assertTrue(any(r["code"] == "MISSING_MANDATORY_CHECK" and
                            r["dimension"] == "INDEPENDENT_REVIEW" for r in result["reasons"]))

    def test_saved_assessment_survives_app_recreation(self):
        record = self.client.post("/api/adoption/assessments", json=self.draft()).json()
        with TestClient(create_app(Path(self.temporary.name) / "studio.db")) as reopened:
            self.assertEqual(
                reopened.get(f"/api/adoption/assessments/{record['assessment_id']}").json(), record
            )

    def test_rejects_nonfictional_attestation_extra_fields_and_foreign_reference(self):
        draft = self.draft()
        for key, value in (("confirmed_fictional", False), ("synthetic", False), ("client_id", "real-company")):
            invalid = copy.deepcopy(draft)
            invalid[key] = value
            self.assertEqual(self.client.post("/api/adoption/assessments", json=invalid).status_code, 422)
        invalid = copy.deepcopy(draft)
        invalid["private_access_token"] = "not-allowed"
        self.assertEqual(self.client.post("/api/adoption/assessments", json=invalid).status_code, 422)
        invalid = copy.deepcopy(draft)
        invalid["checks"][0]["evidence_ids"] = ["foreign-tenant-asset"]
        self.assertEqual(self.client.post("/api/adoption/assessments", json=invalid).status_code, 422)
        self.assertEqual(self.client.get("/api/adoption/assessments").json(), [])

    def test_report_is_traceable_and_never_claims_real_approval(self):
        draft = self.draft()
        draft["title"] = "Fictional evaluation\n## APPROVED BY BOARD"
        response = self.client.post("/api/adoption/assessments", json=draft)
        self.assertEqual(response.status_code, 201, response.text)
        record = response.json()
        report = self.client.get(f"/api/adoption/assessments/{record['assessment_id']}/report")
        self.assertEqual(report.status_code, 200)
        self.assertIn("SYNTHETIC DEMONSTRATION", report.text)
        self.assertIn("NOT A HUMAN APPROVAL", report.text)
        self.assertIn(record["source_sha256"], report.text)
        self.assertIn("DATA GOVERNANCE", report.text)
        self.assertIn("**Simulated evidence support:** NOT ESTABLISHED", report.text)
        self.assertIn("NOT A CUSTOMER ASSESSMENT", report.text)
        self.assertNotIn("\n## APPROVED BY BOARD", report.text)
        self.assertEqual(self.client.get("/api/adoption/assessments/no-such-id/report").status_code, 404)


if __name__ == "__main__":
    unittest.main()
