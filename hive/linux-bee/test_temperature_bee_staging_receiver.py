"""Offline replay of the isolated staging receiver (no phone or network)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import temperature_bee_staging_receiver as receiver

COMMAND_PATH = "hive/linux-bee/commands/temperature-bee-probe-001.command.json"
COMMAND = '{"id":"temperature-bee-probe-001","action":"repo_status"}'


class ReceiverReplayTests(unittest.TestCase):
    def test_one_command_is_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            def fake_git(*args):
                if args[0] == "ls-tree":
                    return COMMAND_PATH + "\n"
                if args[0] == "show":
                    return COMMAND
                return ""
            with patch.object(receiver, "RESULT_DIR", directory), \
                 patch.object(receiver, "SEEN", directory / "seen.jsonl"), \
                 patch.object(receiver, "git", side_effect=fake_git):
                self.assertEqual(receiver.run_once(), 1)
                self.assertEqual(receiver.run_once(), 0)
                result = json.loads((directory / "temperature-bee-probe-001.result.json").read_text())
                self.assertEqual(result["lane"], "temperature-bee-staging")

    def test_reject_unsafe_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            def fake_git(*args):
                if args[0] == "ls-tree":
                    return COMMAND_PATH + "\n"
                if args[0] == "show":
                    return '{"id":"temperature-bee-probe-001","action":"codex_exec"}'
                return ""
            with patch.object(receiver, "RESULT_DIR", directory), \
                 patch.object(receiver, "SEEN", directory / "seen.jsonl"), \
                 patch.object(receiver, "git", side_effect=fake_git):
                self.assertEqual(receiver.run_once(), 0)
                self.assertFalse((directory / "seen.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
