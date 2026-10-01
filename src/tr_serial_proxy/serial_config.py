"""Serial settings and CLI conversions."""

import argparse
from dataclasses import dataclass

import serial


def parity_value(value: str) -> str:
    value = value.upper()
    if value not in ("N", "E", "O", "M", "S"):
        raise argparse.ArgumentTypeError("paridade: N, E, O, M ou S")
    return value


def stopbits_value(value: str) -> float:
    number = float(value)
    if number not in (1, 1.5, 2):
        raise argparse.ArgumentTypeError("stopbits: 1, 1.5 ou 2")
    return number


@dataclass(frozen=True)
class SerialSettings:
    """Independent, immutable settings for one end of the bridge."""

    baudrate: int
    bytesize: int = 8
    parity: str = "N"
    stopbits: float = 1
    timeout: float = 0.01
    write_timeout: float = 1.0
    xonxoff: bool = False
    rtscts: bool = False
    dsrdtr: bool = False

    @classmethod
    def from_args(cls, args):
        return cls(args.baud, **{name: getattr(args, name) for name in
                   ("bytesize", "parity", "stopbits", "timeout", "write_timeout",
                    "xonxoff", "rtscts", "dsrdtr")})

    def open(self, port: str) -> serial.Serial:
        return serial.Serial(port=port, **vars(self))
