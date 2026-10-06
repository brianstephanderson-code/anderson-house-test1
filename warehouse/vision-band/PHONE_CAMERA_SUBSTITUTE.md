# Vision Band — Phone Camera Substitute

Status: READY TO PROBE

Yes: the Android phone camera can stand in for the future Vision Band camera.

Why this is useful:
- it gives us a real optical sensor now,
- the same /status /mode /capture contract is preserved,
- Three Amigos can exercise a real capture -> bridge -> upstream workflow,
- later the XIAO wearable replaces only the sensor endpoint.

## Preferred prototype path

Phone camera
-> phone_camera_adapter.py
-> Vision Band endpoint contract
-> existing vision_band_client.py
-> Three Amigos

## Android implementation

The first adapter uses Termux:API's `termux-camera-photo` when available.

If Termux:API camera access is not installed/available, do NOT pretend the replay passed.
The fallback is to add camera capture to the Android device-agent instead.

## Safety / privacy

- Default mode is PARKED.
- Capture is refused while PARKED.
- Still images only.
- No continuous background recording.
- The phone/Android OS camera permission remains authoritative.
- This is a development substitute, not the final wearable.

## Next gate

1. Probe phone for termux-camera-photo.
2. If present: launch adapter and run the SAME endpoint replay with a real JPEG.
3. If absent: route camera capture through Amigos Device Agent.
4. GREEN only after real-image capture succeeds.
