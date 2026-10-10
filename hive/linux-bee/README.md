# Linux Bee — staged sensor gateway

A small Python program designed for an ephemeral Linux runner. It accepts JSON sensor envelopes on standard input, validates them, and routes by sensor type (audio, temperature, camera, location). This is a **prototype**, not a network receiver or virtual phone.

## Test on any Linux runner
```sh
cd hive/linux-bee
python3 -m unittest -v test_linux_bee.py
printf '%s\n' '{"device_id":"moto_1","sensor_type":"temperature","timestamp":"2026-10-09T12:00:00Z","payload":{"celsius":24.5}}' | python3 linux_bee.py
```

## Next verification gates
1. Run tests in a GitHub Actions Linux runner.
2. Connect one authorized physical device via an authenticated transport.
3. Verify genuine end-to-end sensor delivery, acknowledgements, replay, and reconnection.
4. Keep individual users/devices isolated; enforce consent, authentication and retention policy.

No phone downloads, network exposure, cloud provisioning or production changes required for this staged prototype.
