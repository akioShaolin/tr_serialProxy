"""Transparent Serial Proxy Logger for Windows."""

import argparse
from pathlib import Path
import re
import sys

import serial
from serial.tools import list_ports

from .bridge import run
from .serial_config import parity_value, stopbits_value
from .utils import port_key, positive_int, positive_seconds


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--physical-port", type=str.strip)
    parser.add_argument("--virtual-port", type=str.strip)
    parser.add_argument("--baud", type=positive_int)
    parser.add_argument("--bytesize", type=int, choices=(5, 6, 7, 8), default=8)
    parser.add_argument("--parity", type=parity_value, default="N")
    parser.add_argument("--stopbits", type=stopbits_value, default=1)
    parser.add_argument("--timeout", type=positive_seconds, default=0.01)
    parser.add_argument("--write-timeout", type=positive_seconds, default=1.0)
    for flag in ("xonxoff", "rtscts", "dsrdtr", "quiet", "ascii", "raw-log", "list-ports"):
        parser.add_argument(f"--{flag}", action="store_true")
    parser.add_argument("--log-dir", type=Path, default=Path("logs"))
    parser.add_argument("--log-prefix", default="serial")
    parser.add_argument("--chunk-size", type=positive_int, default=4096)
    args = parser.parse_args(argv)
    if not args.list_ports:
        for name in ("physical_port", "virtual_port", "baud"):
            if not getattr(args, name):
                parser.error(f"--{name.replace('_', '-')} é obrigatório")
        if port_key(args.physical_port) == port_key(args.virtual_port):
            parser.error("as portas física e virtual devem ser diferentes")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.log_prefix):
        parser.error("--log-prefix aceita apenas letras ASCII, números, _ e -")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list_ports:
        try:
            ports = sorted(list_ports.comports(), key=lambda port: port.device)
            for port in ports:
                print(f"{port.device}: {port.description} [{port.hwid}]")
            if not ports:
                print("Nenhuma porta serial encontrada.")
            return 0
        except (OSError, serial.SerialException) as exc:
            print(f"Erro ao listar portas: {exc}", file=sys.stderr)
            return 1
    return run(args)
