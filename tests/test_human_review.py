"""Evaluation review protocol tests — reviewer declarations are never authenticated."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from evals.engine import CORPUS_PATH, DATASET_PATH, SafeRuleCandidate, digest, execute, load_fixtures
from evals.review import _write_new, prepare, read_run, run_sha256, summarize


class HumanReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run_path = Path(self.temporary.name) / "synthetic-run.json"
        dataset, corpus = load_fixtures()
        report = execute(dataset, corpus, SafeRuleCandidate())
        report["dataset"]["sha256"] = digest(DATASET_PATH)
        report["corpus"]["sha256"] = digest(CORPUS_PATH)
        report["run_mode"] = "OFFLINE_DETERMINISTIC"
        self.run_path.write_text(json.dumps(report), encoding="utf-8")
        self.report = read_run(self.run_path)
        self.run_digest = run_sha256(self.run_path)

    def filled(self, reviewer_id: str) -> dict:
        worksheet = prepare(self.report, self.run_digest, reviewer_id)
        for row in worksheet["cases"]:
            row["label_review"] = "ACCEPT"
            row["answer_review"] = "PASS"
            row["rationale"] = "Synthetic unit test only; no real reviewer participated."
        return worksheet

    def test_prepare_is_unreviewed_and_has_exact_provenance(self):
        worksheet = prepare(self.report, self.run_digest, "reviewer-demo-1")
        self.assertEqual(worksheet["source_run_sha256"], self.run_digest)
        self.assertEqual(worksheet["identity_status"], "SELF_DECLARED_UNVERIFIED")
        self.assertEqual(len(worksheet["cases"]), 13)
        self.assertTrue(all(row["answer_review"] == "UNREVIEWED" for row in worksheet["cases"]))
        self.assertTrue(all(row["label_review"] == "UNREVIEWED" for row in worksheet["cases"]))
        self.assertTrue(all(not row["rationale"] for row in worksheet["cases"]))

    def test_unreviewed_or_only_one_complete_sheet_cannot_be_calibrated(self):
        blank = prepare(self.report, self.run_digest, "reviewer-demo-1")
        result = summarize(self.report, self.run_digest, [blank])
        self.assertEqual(result["review_status"], "INCOMPLETE")
        self.assertEqual(result["complete_reviewer_count"], 0)
        self.assertIsNone(result["human_answer_agreement_rate"])
        complete = self.filled("reviewer-demo-1")
        result = summarize(self.report, self.run_digest, [complete])
        self.assertEqual(result["review_status"], "INCOMPLETE")
        self.assertEqual(result["complete_reviewer_count"], 1)
        self.assertEqual(result["release_decision"], "HUMAN_REVIEW_REQUIRED")

    def test_two_complete_self_declared_sheets_show_agreement_without_approving_release(self):
        first = self.filled("reviewer-demo-1")
        second = self.filled("reviewer-demo-2")
        result = summarize(self.report, self.run_digest, [first, second])
        self.assertEqual(result["review_status"], "TWO_SELF_DECLARED_REVIEWS")
        self.assertEqual(result["human_answer_agreement_rate"], 1.0)
        self.assertFalse(result["reviewer_identity_verified"])
        self.assertEqual(result["release_decision"], "HUMAN_REVIEW_REQUIRED")

    def test_disagreement_and_critical_human_failure_are_explicit(self):
        first = self.filled("reviewer-demo-1")
        second = self.filled("reviewer-demo-2")
        critical_row = next(row for row in second["cases"] if row["critical"])
        critical_row["answer_review"] = "FAIL"
        critical_row["label_review"] = "REJECT"
        result = summarize(self.report, self.run_digest, [first, second])
        self.assertLess(result["human_answer_agreement_rate"], 1.0)
        self.assertIn(critical_row["case_id"], result["critical_human_failure_case_ids"])
        self.assertIn(critical_row["case_id"], result["automated_human_disagreement_case_ids"])
        self.assertIn(critical_row["case_id"], result["expected_label_dispute_case_ids"])

    def test_rejects_tampered_evidence_and_foreign_or_short_reviews(self):
        valid = self.filled("reviewer-demo-1")
        modified = copy.deepcopy(valid)
        modified["cases"][0]["candidate_answer"] = "rewritten answer"
        with self.assertRaisesRegex(ValueError, "source evidence"):
            summarize(self.report, self.run_digest, [modified])
        modified = copy.deepcopy(valid)
        modified["source_run_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "exact synthetic run"):
            summarize(self.report, self.run_digest, [modified])
        modified = copy.deepcopy(valid)
        modified["cases"][0]["rationale"] = "ok"
        self.assertEqual(summarize(self.report, self.run_digest, [modified])["complete_reviewer_count"], 0)
        modified = copy.deepcopy(valid)
        modified["cases"][0]["case_id"] = "foreign"
        with self.assertRaisesRegex(ValueError, "Foreign"):
            summarize(self.report, self.run_digest, [modified])

    def test_rejects_duplicate_identity_and_run_with_wrong_digest(self):
        valid = self.filled("reviewer-demo-1")
        with self.assertRaisesRegex(ValueError, "distinct"):
            summarize(self.report, self.run_digest, [valid, copy.deepcopy(valid)])
        modified = copy.deepcopy(self.report)
        modified["corpus"]["sha256"] = "invalid"
        self.run_path.write_text(json.dumps(modified), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "fixture digests"):
            read_run(self.run_path)

    def test_refuses_to_overwrite_review_artifact(self):
        target = Path(self.temporary.name) / "review.json"
        _write_new(target, prepare(self.report, self.run_digest, "reviewer-demo-1"))
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            _write_new(target, {"different": "content"})


if __name__ == "__main__":
    unittest.main()
