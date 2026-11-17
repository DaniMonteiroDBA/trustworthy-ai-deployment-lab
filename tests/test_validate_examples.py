"""Contract tests: positive synthetic example and critical negative paths."""

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_examples import validate


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "examples/fintrust_discovery.json").read_text(encoding="utf-8"))


class ContractTests(unittest.TestCase):
    def test_synthetic_discovery_example(self):
        self.assertEqual(validate(EXAMPLE), [])

    def test_reject_real_client_record(self):
        record = copy.deepcopy(EXAMPLE)
        record["client"]["synthetic"] = False
        self.assertTrue(any("synthetic" in error for error in validate(record)))

    def test_reject_unreferenced_evidence(self):
        record = copy.deepcopy(EXAMPLE)
        record["decision"]["evidence_ids"] = ["does-not-exist"]
        self.assertTrue(any("Unknown evidence" in error for error in validate(record)))

    def test_inference_cannot_authorize_go(self):
        record = copy.deepcopy(EXAMPLE)
        record["decision"]["status"] = "GO"
        record["decision"]["blockers"] = []
        record["evidence"][0]["class"] = "INFERRED"
        record["evidence"][0]["verification_status"] = "VERIFIED"
        self.assertTrue(any("GO requires" in error for error in validate(record)))

    def test_go_cannot_override_blockers(self):
        record = copy.deepcopy(EXAMPLE)
        record["decision"]["status"] = "GO"
        record["evidence"][1]["verification_status"] = "VERIFIED"
        self.assertTrue(any("unresolved blockers" in error for error in validate(record)))


if __name__ == "__main__":
    unittest.main()
