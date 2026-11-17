"""M1: synthetic-only API integration and decision-gate tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.server import create_app


class StudioAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.client = TestClient(create_app(Path(self.temp.name) / "studio-test.db"))
        self.case_id = "fintrust-policy-action"

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def case(self):
        response = self.client.get(f"/api/cases/{self.case_id}")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def new_decision(self, stage="DISCOVER", status="GO", evidence_ids=None, blockers=None):
        return self.client.post(f"/api/cases/{self.case_id}/decisions", json={
            "stage": stage, "status": status, "owner": "Fictional reviewer",
            "rationale": "Documented synthetic design review with explicit remaining uncertainty.",
            "evidence_ids": ["e-sim-002"] if evidence_ids is None else evidence_ids,
            "blockers": [] if blockers is None else blockers,
            "alternatives": ["Non-AI document portal"],
        })

    def verify_document(self):
        response = self.client.post("/api/evidence/e-sim-002/review", json={
            "status": "VERIFIED", "reviewer": "Fictional policy reviewer",
            "rationale": "Reviewed synthetic placeholder for demo; not real policy evidence.",
        })
        self.assertEqual(response.status_code, 200)

    def test_homepage_health_and_three_synthetic_clients(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertIn("SYNTHETIC DATA ONLY", self.client.get("/").text)
        self.assertEqual(self.client.get("/assets/app.js").status_code, 200)
        self.assertEqual(self.client.get("/assets/styles.css").status_code, 200)
        self.assertEqual(self.client.get("/api/health").json()["mode"], "synthetic_local_demo")
        clients = self.client.get("/api/clients").json()
        self.assertEqual({c["client_id"] for c in clients}, {"fintrust-demo", "retailflow-demo", "civicdata-demo"})
        self.assertTrue(all(c["synthetic"] for c in clients))

    def test_seeded_case_is_in_review_and_other_stages_locked(self):
        record = self.case()
        self.assertEqual(record["stage_states"][0]["status"], "IN_REVIEW")
        self.assertEqual(record["stage_states"][1]["status"], "LOCKED")
        self.assertTrue(record["non_ai_alternative"])

    def test_go_requires_verified_evidence_and_no_blockers(self):
        self.assertEqual(self.new_decision().status_code, 409)
        self.verify_document()
        self.assertEqual(self.new_decision(blockers=["Unresolved risk"]).status_code, 409)
        self.assertEqual(self.new_decision().status_code, 201)
        record = self.case()
        self.assertEqual(record["stage_states"][0]["status"], "GO")
        self.assertEqual(record["stage_states"][1]["status"], "NOT_STARTED")

    def test_cannot_skip_stage(self):
        response = self.new_decision(stage="ASSESS", status="HOLD")
        self.assertEqual(response.status_code, 409)

    def test_cross_client_evidence_reference_rejected(self):
        self.verify_document()
        response = self.new_decision(evidence_ids=["e-sim-003"])
        self.assertEqual(response.status_code, 422)

    def test_new_evidence_cannot_claim_measurement_or_auto_verification(self):
        url = f"/api/cases/{self.case_id}/evidence"
        invalid = self.client.post(url, json={
            "evidence_class": "MEASURED", "source": "Fake metric run",
            "summary": "A fictional success score with no run.",
        })
        self.assertEqual(invalid.status_code, 422)
        valid = self.client.post(url, json={
            "evidence_class": "DOCUMENTED", "source": "Synthetic workshop notes",
            "summary": "A proposed stakeholder summary requiring verification.",
        })
        self.assertEqual(valid.status_code, 201)
        self.assertEqual(valid.json()["verification_status"], "UNVERIFIED")

    def test_validation_gate_rejects_go_without_measured_evidence(self):
        self.verify_document()
        for stage in ("DISCOVER", "ASSESS", "PRIORITIZE", "ARCHITECT"):
            self.assertEqual(self.new_decision(stage=stage).status_code, 201)
        self.assertEqual(self.new_decision(stage="VALIDATE").status_code, 409)
        self.assertEqual(self.case()["stage_states"][4]["status"], "NOT_STARTED")

    def test_prior_approval_can_be_revoked_and_later_stage_relocks(self):
        self.verify_document()
        self.assertEqual(self.new_decision(stage="DISCOVER").status_code, 201)
        self.assertEqual(self.new_decision(stage="ASSESS").status_code, 201)
        self.assertEqual(self.new_decision(stage="DISCOVER", status="HOLD").status_code, 201)
        record = self.case()
        self.assertEqual(record["stage_states"][1]["status"], "LOCKED")

    def test_executive_report_is_honest_about_synthetic_data(self):
        response = self.client.get(f"/api/cases/{self.case_id}/executive-report")
        self.assertEqual(response.status_code, 200)
        self.assertIn("SYNTHETIC DEMONSTRATION", response.text)
        self.assertIn("No measured operational or business outcomes", response.text)
        self.assertIn("Non-AI alternative", response.text)

    def test_unknown_resources_are_404(self):
        self.assertEqual(self.client.get("/api/clients/unknown").status_code, 404)
        self.assertEqual(self.client.get("/api/cases/unknown").status_code, 404)
        self.assertEqual(self.client.get("/api/cases/unknown/executive-report").status_code, 404)


if __name__ == "__main__":
    unittest.main()
