"""Read-only staging probe for the existing Moto bridge command contract.

This validates command shape and documents safe expectations. It does NOT
publish to the production inbox or run commands on a phone.
"""
import json
import unittest

PROBE = {
    "id": "temperature-bee-staging-probe",
    "action": "repo_status",
}

class BridgeContractTest(unittest.TestCase):
    def test_probe_is_read_only(self):
        self.assertEqual(PROBE["action"], "repo_status")
        self.assertTrue(PROBE["id"].startswith("temperature-bee-"))
        self.assertNotIn("allow_write", PROBE)

    def test_probe_json_roundtrip(self):
        self.assertEqual(json.loads(json.dumps(PROBE)), PROBE)

if __name__ == "__main__":
    unittest.main()
