"""Small argument validators and byte formatting helpers."""

import argparse
import math
import re


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("deve ser um inteiro positivo")
    return number


def positive_seconds(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("deve ser um número finito maior que zero")
    return number


def port_key(value: str) -> str:
    value = value.strip().upper()
    if value.startswith("\\\\.\\"):
        value = value[4:]
    match = re.fullmatch(r"COM(\d+)", value)
    return f"COM{int(match[1])}" if match else value


def hex_dump(data: bytes) -> str:
    return data.hex(" ").upper()
