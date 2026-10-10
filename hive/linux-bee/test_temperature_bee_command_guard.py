import json
import unittest
from temperature_bee_command_guard import validate_command, execute_probe


class StagingGuardTests(unittest.TestCase):
    def test_valid_probe(self):
        command = {"id": "temperature-bee-probe-001", "action": "repo_status"}
        self.assertEqual(validate_command(json.dumps(command)), command)
        result = execute_probe(command, lambda: "clean")
        self.assertEqual(result["status"], "clean")
        self.assertEqual(result["lane"], "temperature-bee-staging")

    def test_reject_write_and_execution(self):
        for action in ("git_sync", "run_repo_python", "codex_exec", "android_launch"):
            with self.assertRaises(ValueError):
                validate_command({"id": "temperature-bee-probe-001", "action": action})

    def test_reject_extra_fields(self):
        with self.assertRaises(ValueError):
            validate_command({"id": "temperature-bee-probe-001", "action": "repo_status", "allow_write": True})

    def test_reject_unscoped_id(self):
        with self.assertRaises(ValueError):
            validate_command({"id": "arbitrary", "action": "repo_status"})


if __name__ == "__main__":
    unittest.main()
