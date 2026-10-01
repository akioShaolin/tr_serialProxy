import json
from pathlib import Path
import tempfile
import unittest

from tr_serial_proxy.logger import CaptureLog


class LogTests(unittest.TestCase):
    def test_binary_roundtrip_and_counters(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = CaptureLog(Path(directory), raw=True, quiet=True, show_ascii=True)
            payload = bytes(range(256))
            capture.record("TX", payload, "2026-09-30T14:35:22.123456-03:00", 0.381224)
            capture.record("RX", b"\x00\xff\r\n")
            capture.close()
            records = [json.loads(line) for line in capture.raw_path.read_text().splitlines()]
            self.assertEqual(bytes.fromhex(records[0]["data"]), payload)
            self.assertEqual(records[0]["length"], 256)
            self.assertEqual(records[0]["elapsed"], 0.381224)
            self.assertEqual(capture.counts, {"TX": [1, 256], "RX": [1, 4]})
            text = capture.path.read_text(encoding="utf-8")
            self.assertIn("[+0.381224] TX  256 bytes", text)
            self.assertIn("ASCII: ....", text)


