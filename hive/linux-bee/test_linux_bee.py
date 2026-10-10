import unittest
from linux_bee import process

BASE = {"device_id":"moto_1","sensor_type":"temperature","timestamp":"2026-10-09T12:00:00Z","payload":{"celsius":24.5}}

class LinuxBeeTests(unittest.TestCase):
    def test_temperature(self):
        self.assertEqual(process(BASE)["route"], "sensor/temperature")
    def test_audio(self):
        self.assertEqual(process({**BASE,"sensor_type":"audio","payload":{"duration_ms":500}})["route"],"sensor/audio")
    def test_camera(self):
        self.assertEqual(process({**BASE,"sensor_type":"camera","payload":{"frame_count":1}})["route"],"sensor/camera")
    def test_location(self):
        self.assertEqual(process({**BASE,"sensor_type":"location","payload":{"lat":0,"lon":0}})["route"],"sensor/location")
    def test_bad_device(self):
        with self.assertRaises(ValueError): process({**BASE,"device_id":"../escape"})
    def test_bad_temperature(self):
        with self.assertRaises(ValueError): process({**BASE,"payload":{"celsius":"hot"}})
    def test_missing_field(self):
        with self.assertRaises(ValueError): process({"sensor_type":"audio"})
    def test_naive_timestamp(self):
        with self.assertRaises(ValueError): process({**BASE,"timestamp":"2026-10-09T12:00:00"})
    def test_raw_media_rejected(self):
        with self.assertRaises(ValueError): process({**BASE,"sensor_type":"audio","payload":{"base64":"abc"}})

if __name__ == "__main__":
    unittest.main()
