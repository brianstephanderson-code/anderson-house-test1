"""Bridge-safe regression runner for warehouse/function_candidate_state.py."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "warehouse" / "function_candidate_state.py"
spec = importlib.util.spec_from_file_location("function_candidate_state", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

for state in ("DISCOVERED", "TESTED", "REJECTED", "NEEDS-MORE-EVIDENCE"):
    result = mod.promotion_decision({"state": state})
    assert result["decision"] == "QUARANTINE", (state, result)

assert mod.promotion_decision({"state": "VERIFIED"})["decision"] == "PROMOTE"
assert mod.promotion_decision({"state": "looks-good"})["decision"] == "QUARANTINE"
assert mod.promotion_decision(None)["decision"] == "QUARANTINE"
print("warehouse candidate state gate: PASS")
