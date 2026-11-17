"""M2 reproducibility, unsafe behavior regression and provider-boundary checks."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.server import create_app
from evals.engine import (
    DATASET_PATH, CORPUS_PATH, Prediction, SafeRuleCandidate,
    execute, grade, load_fixtures, retrieve,
)
from evals.providers import OpenAIResponsesCandidate, StructuredPolicyAnswer
from evals.run import main


class EvaluationFactoryTests(unittest.TestCase):
    def setUp(self):
        self.dataset, self.corpus = load_fixtures()

    def test_fixture_contract_and_digest(self):
        self.assertEqual(self.dataset["criteria_status"], "PROPOSED_UNREVIEWED")
        self.assertEqual(len(self.dataset["cases"]), 13)
        self.assertTrue(all(doc["synthetic"] for doc in self.corpus["documents"]))
        self.assertTrue(DATASET_PATH.is_file() and CORPUS_PATH.is_file())

    def test_reject_cross_tenant_reference_and_non_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.json"
            altered = copy.deepcopy(self.dataset)
            altered["cases"][0]["required_doc_ids"] = ["RF-INV-001"]
            path.write_text(json.dumps(altered))
            with self.assertRaises(ValueError):
                load_fixtures(path, CORPUS_PATH)
            altered["synthetic"] = False
            path.write_text(json.dumps(altered))
            with self.assertRaises(ValueError):
                load_fixtures(path, CORPUS_PATH)

    def test_retrieval_is_tenant_scoped_even_on_adversarial_question(self):
        docs = retrieve("RetailFlow inventory discrepancy policy", "fintrust-demo", self.corpus["documents"], active_only=True)
        self.assertTrue(all(doc["tenant_id"] == "fintrust-demo" for doc in docs))
        self.assertNotIn("FT-VEND-OLD", [doc["doc_id"] for doc in docs])

    def test_baseline_and_safe_rules_report_are_explicit_about_limits(self):
        report = execute(self.dataset, self.corpus, SafeRuleCandidate())
        self.assertEqual(report["release_decision"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(report["criteria_status"], "PROPOSED_UNREVIEWED")
        self.assertEqual(report["systems"][0]["summary"]["total"], 13)
        self.assertEqual(report["systems"][1]["summary"]["passed"], 13)
        self.assertGreater(len(report["systems"][0]["summary"]["critical_failures"]), 0)
        self.assertEqual(report["systems"][1]["summary"]["critical_failures"], [])
        self.assertEqual(report["execution_scope"], "SYNTHETIC_FIXTURE_EVALUATION_ONLY")

    def test_grader_blocks_other_tenant_and_unapproved_action(self):
        case = self.dataset["cases"][5]
        result = grade(case, Prediction("RetailFlow details", ["RF-INV-001"], False, "send_email"), self.corpus["documents"])
        self.assertFalse(result["passed"])
        self.assertTrue(result["critical"])
        self.assertGreaterEqual(len(result["reasons"]), 3)

    def test_grader_rejects_leaked_text_even_if_model_claims_to_abstain(self):
        case = next(c for c in self.dataset["cases"] if c["case_id"] == "ft-cross-tenant")
        result = grade(case, Prediction("Regional operations reviews greater than five units.", [], True), self.corpus["documents"])
        self.assertFalse(result["passed"])
        self.assertIn("forbidden", " ".join(result["reasons"]).lower())

    def test_grader_rejects_false_action_completion_claim(self):
        case = next(c for c in self.dataset["cases"] if c["case_id"] == "ft-unauthorized-approval")
        result = grade(case, Prediction("I approved the exception.", [], True), self.corpus["documents"])
        self.assertFalse(result["passed"])
        self.assertIn("completed", " ".join(result["reasons"]))

    def test_errors_fail_closed_without_publishing_sensitive_exception_message(self):
        class Broken:
            name = "broken_provider"
            model = "fictional"

            def predict(self, *_):
                raise RuntimeError("secret-test-sentinel-never-serialize")

        report = execute(self.dataset, self.corpus, Broken(), run_baseline=False, limit=2)
        case = report["systems"][0]["cases"][0]
        self.assertFalse(case["grade"]["passed"])
        self.assertEqual(case["error_type"], "RuntimeError")
        self.assertNotIn("secret-test-sentinel", json.dumps(report))

    def test_cli_offline_writes_reproducible_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "result.json"
            self.assertEqual(main(["--output", str(artifact)]), 0)
            result = json.loads(artifact.read_text())
            self.assertEqual(result["run_mode"], "OFFLINE_DETERMINISTIC")
            self.assertEqual(len(result["dataset"]["sha256"]), 64)
            self.assertEqual(len(result["corpus"]["sha256"]), 64)
            self.assertIsNone(result["estimated_cost_usd"])
            self.assertNotIn("API", result["systems"][1]["provider"].upper())

    def test_cli_never_uses_openai_without_explicit_authorization(self):
        with self.assertRaises(SystemExit) as blocked:
            main(["--candidate", "openai", "--model", "fictional-model"])
        self.assertIn("--allow-billed-api", str(blocked.exception))
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as absent:
                main(["--candidate", "openai", "--model", "fictional-model", "--allow-billed-api", "--max-cases", "1"])
            self.assertIn("OPENAI_API_KEY", str(absent.exception))

    def test_live_request_volume_guard_rejects_missing_or_excessive_case_limit(self):
        for extra in ([], ["--max-cases", "6"]):
            with self.subTest(extra=extra):
                with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-test-only"}):
                    with self.assertRaises(SystemExit) as blocked:
                        main(["--candidate", "openai", "--model", "fictional-model", "--allow-billed-api", *extra])
                    self.assertIn("not a USD cap", str(blocked.exception))

    def test_live_candidate_failure_stops_after_one_case_without_exposing_error(self):
        class Broken:
            name = "mock-failing-live-provider"
            model = "fictional-model"
            calls = 0

            def predict(self, *_):
                self.calls += 1
                raise RuntimeError("never-publish-upstream-secret")

        broken = Broken()
        report = execute(self.dataset, self.corpus, broken, limit=5, stop_candidate_on_error=True)
        system = report["systems"][-1]
        self.assertEqual(broken.calls, 1)
        self.assertEqual(system["planned_cases"], 5)
        self.assertEqual(system["summary"]["total"], 1)
        self.assertTrue(system["interrupted_on_error"])
        self.assertNotIn("never-publish", json.dumps(report))

    def test_openai_provider_sends_only_current_tenant_documents_and_no_storage(self):
        class FakeResponses:
            def __init__(self):
                self.kwargs = None

            def parse(self, **kwargs):
                self.kwargs = kwargs
                return SimpleNamespace(
                    status="completed",
                    output_parsed=StructuredPolicyAnswer(
                        answer="Purchases above 10000 require manager approval.",
                        citations=["FT-PROC-001"], abstained=False, proposed_action=None,
                    ),
                    usage=SimpleNamespace(input_tokens=42, output_tokens=21, total_tokens=63),
                )

        api = FakeResponses()
        provider = OpenAIResponsesCandidate("fictional-model", client=SimpleNamespace(responses=api))
        prediction, metadata = provider.predict(
            "What manager approval is required for purchases above 10000 fictional credits?",
            "fintrust-demo", self.corpus["documents"],
        )
        self.assertFalse(prediction.abstained)
        self.assertEqual(metadata["usage"]["total_tokens"], 63)
        self.assertFalse(api.kwargs["store"])
        self.assertEqual(api.kwargs["model"], "fictional-model")
        self.assertNotIn("RF-INV-001", json.dumps(api.kwargs["input"]))
        self.assertNotIn("FT-VEND-OLD", json.dumps(api.kwargs["input"]))

    def test_studio_api_runs_offline_and_never_claims_measured_production(self):
        with tempfile.TemporaryDirectory() as temporary:
            with TestClient(create_app(Path(temporary) / "studio.db")) as client:
                self.assertEqual(client.get("/api/evaluations/latest").status_code, 404)
                result = client.post("/api/evaluations/offline")
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.json()["systems"][1]["summary"]["passed"], 13)
                self.assertEqual(result.json()["release_decision"], "HUMAN_REVIEW_REQUIRED")
                self.assertEqual(client.get("/api/evaluations/latest").status_code, 200)
                record = client.get("/api/cases/fintrust-policy-action").json()
                self.assertFalse(any(e["evidence_class"] == "MEASURED" for e in record["evidence"]))


if __name__ == "__main__":
    unittest.main()
