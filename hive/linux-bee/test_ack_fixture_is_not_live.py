"""A stored fixture is not proof of a live Moto handshake."""
import json
import unittest
from pathlib import Path


class EvidenceTests(unittest.TestCase):
    def test_saved_probe_is_not_device_proof(self):
        result = json.loads((Path(__file__).parent / 'results' / 'temperature-bee-probe-001.result.json').read_text())
        self.assertEqual(result['status'], 'receiver-alive')
        self.assertNotIn('device_id', result)
        self.assertNotIn('device_timestamp', result)
        self.assertNotIn('verified_device_origin', result)


if __name__ == '__main__':
    unittest.main()
