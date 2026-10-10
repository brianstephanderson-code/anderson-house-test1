"""Reusable, local-only Temperature Bee collector; no cloud credentials or production writes."""
import json
import subprocess
from pathlib import Path
from moto_battery_adapter import convert


def collect(readings_file, battery_status=None):
    """Collect once; append only a validated sensor envelope, return that envelope."""
    if battery_status is None:
        result = subprocess.run(
            ["termux-battery-status"], check=True, capture_output=True, text=True, timeout=30
        )
        battery_status = json.loads(result.stdout)
    reading = convert(battery_status)
    if reading["status"] != "ACCEPTED":
        raise ValueError("sensor reading rejected")
    destination = Path(readings_file).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as output:
        output.write(json.dumps(reading, sort_keys=True) + "\n")
    return reading


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--readings-file", required=True)
    args = parser.parse_args()
    print(json.dumps(collect(args.readings_file), sort_keys=True))
