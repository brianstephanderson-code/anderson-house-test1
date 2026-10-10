import unittest
from moto_battery_adapter import convert

class MotoBatteryTests(unittest.TestCase):
    def test_realistic_battery_reading(self):
        result = convert({"health":"GOOD","percentage":78,"plugged":"UNPLUGGED","status":"DISCHARGING","temperature":31.2},timestamp="2026-10-09T12:00:00Z")
        self.assertEqual(result["route"],"sensor/temperature")
        self.assertEqual(result["payload"]["celsius"],31.2)
        self.assertEqual(result["payload"]["measurement"],"battery_not_room")
    def test_missing_temperature(self):
        with self.assertRaises(ValueError): convert({"percentage":78})
    def test_invalid_temperature(self):
        with self.assertRaises(ValueError): convert({"temperature":"warm"})
    def test_nonfinite_temperature(self):
        with self.assertRaises(ValueError): convert({"temperature":float("nan")})

if __name__=="__main__":
    unittest.main()
