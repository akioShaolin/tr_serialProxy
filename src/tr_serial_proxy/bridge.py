"""Bidirectional byte forwarding and capture lifecycle."""

import argparse
import queue
import sys
import threading
import time

import serial

from .logger import CaptureLog
from .serial_config import SerialSettings


def write_all(destination, data: bytes) -> None:
    """Complete short writes without retrying uncertain failed writes."""
    offset = 0
    while offset < len(data):
        written = destination.write(data[offset:])
        if written is None or written <= 0:
            raise serial.SerialTimeoutException("escrita não avançou")
        offset += written


def pump(source, destination, direction, capture, stop, errors, chunk_size):
    try:
        while not stop.is_set():
            # Block for the first byte; drain only what is already available.
            data = source.read(min(chunk_size, max(1, source.in_waiting)))
            if data:
                capture.record(direction, data)
                write_all(destination, data)
    except Exception as exc:
        errors.put((direction, exc))
        stop.set()


def run(args: argparse.Namespace) -> int:
    """Own both ports, worker threads and capture cleanup for one session."""
    capture = None
    ports, threads = [], []
    stop, errors = threading.Event(), queue.Queue()
    failed = False
    try:
        capture = CaptureLog(args.log_dir, args.log_prefix, args.raw_log, args.quiet, args.ascii)
        physical_settings = SerialSettings.from_args(args)
        virtual_settings = SerialSettings.from_args(args)
        physical = physical_settings.open(args.physical_port)
        ports.append(physical)
        virtual = virtual_settings.open(args.virtual_port)
        ports.append(virtual)
        flow = ", ".join(name for name in ("xonxoff", "rtscts", "dsrdtr") if getattr(args, name)) or "none"
        print(f"tr_serialProxy\n\nPhysical: {args.physical_port}\nVirtual:  {args.virtual_port}"
              f"\nSettings: {args.baud} {args.bytesize}{args.parity}{args.stopbits:g}"
              f"\nFlow:     {flow}\nLog:      {capture.path}")
        if capture.raw_path:
            print(f"Raw log:  {capture.raw_path}")
        print("\nWaiting for traffic...\nPress Ctrl+C to stop.")
        for source, destination, direction in ((virtual, physical, "TX"), (physical, virtual, "RX")):
            thread = threading.Thread(target=pump, name=direction,
                                      args=(source, destination, direction, capture, stop, errors, args.chunk_size))
            thread.start()
            threads.append(thread)
        while not stop.wait(0.1):
            pass
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        failed = True
    finally:
        stop.set()
        # Cancel reads on Windows; allow current writes their configured timeout.
        for port in ports:
            try:
                port.cancel_read()
            except (AttributeError, OSError, serial.SerialException):
                pass
        for thread in threads:
            thread.join()
        while not errors.empty():
            direction, exc = errors.get_nowait()
            print(f"Erro {direction}: {exc}. O último bloco pode ter sido enviado parcialmente.", file=sys.stderr)
            failed = True
        if capture:
            try:
                capture.close()
            except OSError as exc:
                print(f"Erro ao fechar logs: {exc}", file=sys.stderr)
                failed = True
        for port in ports:
            try:
                port.close()
            except Exception as exc:
                print(f"Erro ao fechar porta: {exc}", file=sys.stderr)
                failed = True
        if capture:
            print(f"\nCapture finished.\nDuration: {time.perf_counter() - capture.started:.3f} s")
            for direction, (blocks, size) in capture.counts.items():
                print(f"{direction}: {blocks} blocks / {size} bytes")
            print(f"Log: {capture.path}")
    return 1 if failed else 0
