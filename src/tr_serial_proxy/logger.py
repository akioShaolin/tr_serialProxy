"""Text and reversible JSONL capture logs."""

from datetime import datetime
from pathlib import Path
import json
import threading
import time

from .utils import hex_dump


def format_record(record, show_ascii=False):
    data = bytes.fromhex(record["data"])
    result = (f"[{record['time']}] [+{record['elapsed']:.6f}] "
              f"{record['direction']}  {record['length']} bytes\n{hex_dump(data)}\n")
    if show_ascii:
        result += "ASCII: " + "".join(chr(b) if 32 <= b <= 126 else "." for b in data) + "\n"
    return result + "\n"


class CaptureLog:
    """Serialize complete records from both reader threads before forwarding."""

    def __init__(self, directory: Path, prefix: str = "serial", raw: bool = False,
                 quiet: bool = False, show_ascii: bool = False):
        self.lock = threading.Lock()
        self.started = time.perf_counter()
        self.counts = {"TX": [0, 0], "RX": [0, 0]}
        self.quiet, self.show_ascii = quiet, show_ascii
        self.raw_file = None
        directory.mkdir(parents=True, exist_ok=True)
        stem = prefix + "-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        self.path = directory / (stem + ".log")
        self.raw_path = directory / (stem + ".jsonl") if raw else None
        self.file = self.path.open("x", encoding="utf-8", newline="\n")
        try:
            if raw:
                self.raw_file = self.raw_path.open("x", encoding="utf-8", newline="\n")
        except BaseException:
            self.file.close()
            raise

    def record(self, direction: str, data: bytes, timestamp: str | None = None,
               elapsed: float | None = None) -> None:
        record = dict(time=timestamp or datetime.now().astimezone().isoformat(timespec="microseconds"),
                      elapsed=time.perf_counter() - self.started if elapsed is None else elapsed,
                      direction=direction, length=len(data), data=data.hex())
        rendered = format_record(record, self.show_ascii)
        with self.lock:
            self.file.write(rendered)
            self.file.flush()
            if self.raw_file:
                self.raw_file.write(json.dumps(record) + "\n")
                self.raw_file.flush()
            self.counts[direction][0] += 1
            self.counts[direction][1] += len(data)
            if not self.quiet:
                print(rendered, end="", flush=True)

    def close(self) -> None:
        try:
            self.file.close()
        finally:
            if self.raw_file:
                self.raw_file.close()
