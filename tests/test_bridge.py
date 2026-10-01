from pathlib import Path
import queue
import tempfile
import threading
import unittest

import serial
from tr_serial_proxy.bridge import pump
from tr_serial_proxy.logger import CaptureLog


class FakePort:
    def __init__(self, incoming=b"", fail=False):
        self.incoming = bytearray(incoming)
        self.output = bytearray()
        self.fail = fail

    @property
    def in_waiting(self):
        return len(self.incoming)

    def read(self, size):
        data = bytes(self.incoming[:size])
        del self.incoming[:size]
        return data

    def write(self, data):
        if self.fail:
            raise serial.SerialTimeoutException("simulated timeout")
        size = min(7, len(data))
        self.output.extend(data[:size])
        return size


class PumpTests(unittest.TestCase):
    def test_bidirectional_binary_and_partial_writes(self):
        payload = bytes(range(256)) * 3
        physical, virtual = FakePort(payload[::-1]), FakePort(payload)
        stop, errors = threading.Event(), queue.Queue()
        with tempfile.TemporaryDirectory() as directory:
            capture = CaptureLog(Path(directory), quiet=True, raw=True)
            original = capture.record
            complete = threading.Event()

            def record(direction, data):
                original(direction, data)
                if all(count[1] == len(payload) for count in capture.counts.values()):
                    complete.set()

            capture.record = record
            threads = [threading.Thread(target=pump, args=(src, dst, direction, capture, stop, errors, 31))
                       for src, dst, direction in ((virtual, physical, "TX"), (physical, virtual, "RX"))]
            try:
                for thread in threads:
                    thread.start()
                self.assertTrue(complete.wait(3), "ponte não completou o tráfego")
            finally:
                stop.set()
                for thread in threads:
                    thread.join(3)
                capture.close()
            self.assertTrue(all(not thread.is_alive() for thread in threads))
            self.assertTrue(errors.empty())
            self.assertEqual(physical.output, payload)
            self.assertEqual(virtual.output, payload[::-1])
            self.assertEqual(capture.counts, {"TX": [25, 768], "RX": [25, 768]})

    def test_log_before_write_and_timeout(self):
        events = []

        class Log:
            def record(self, direction, data):
                events.append((direction, data))

        stop, errors = threading.Event(), queue.Queue()
        pump(FakePort(b"\x00\xff"), FakePort(fail=True), "TX", Log(), stop, errors, 4096)
        self.assertEqual(events, [("TX", b"\x00\xff")])
        self.assertTrue(stop.is_set())
        self.assertIsInstance(errors.get_nowait()[1], serial.SerialTimeoutException)

    def test_log_failure_prevents_forwarding(self):
        class BrokenLog:
            def record(self, direction, data):
                raise OSError("disk full")

        destination, stop, errors = FakePort(), threading.Event(), queue.Queue()
        pump(FakePort(b"abc"), destination, "TX", BrokenLog(), stop, errors, 4096)
        self.assertTrue(stop.is_set())
        self.assertEqual(destination.output, b"")
        self.assertIsInstance(errors.get_nowait()[1], OSError)


