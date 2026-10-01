import contextlib
import io
import unittest

from tr_serial_proxy.cli import parse_args
from tr_serial_proxy.serial_config import SerialSettings


class ArgumentsTests(unittest.TestCase):
    base = ["--physical-port", "COM6", "--virtual-port", "COM21", "--baud", "9600"]

    def test_defaults_and_conversions(self):
        args = parse_args(self.base)
        self.assertEqual(SerialSettings.from_args(args), SerialSettings(9600))
        self.assertTrue(parse_args(["--list-ports"]).list_ports)

    def test_invalid_arguments(self):
        cases = [("--baud", "0"), ("--bytesize", "9"), ("--parity", "X"),
                 ("--stopbits", "3"), ("--timeout", "nan"), ("--timeout", "0"),
                 ("--write-timeout", "inf"), ("--chunk-size", "-1"),
                 ("--virtual-port", "com6"), ("--virtual-port", "\\\\.\\COM6"),
                 ("--log-prefix", "../bad")]
        for flag, value in cases:
            with self.subTest(flag=flag, value=value), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    parse_args(self.base + [flag, value])
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args([])


