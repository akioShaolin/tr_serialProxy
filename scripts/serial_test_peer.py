"""Optional binary echo peer for a second virtual COM pair."""

import argparse
import sys
import time

import serial

from tr_serial_proxy.bridge import write_all
from tr_serial_proxy.utils import positive_int, positive_seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=positive_int, default=9600)
    parser.add_argument("--send-test", action="store_true",
                        help="envia todos os 256 valores de byte e verifica o eco")
    parser.add_argument("--deadline", type=positive_seconds, default=5.0)
    args = parser.parse_args()
    try:
        with serial.Serial(args.port, args.baud, timeout=0.05, write_timeout=1) as port:
            if args.send_test:
                payload = bytes(range(256))
                write_all(port, payload)
                received = bytearray()
                deadline = time.perf_counter() + args.deadline
                while len(received) < len(payload) and time.perf_counter() < deadline:
                    received.extend(port.read(len(payload) - len(received)))
                if received != payload:
                    print(f"FALHA: esperado {payload.hex()}, recebido {received.hex()}")
                    return 1
                print("OK: 256 bytes enviados e recebidos sem alterações.")
            else:
                print("Eco binário ativo. Ctrl+C para sair.")
                while True:
                    data = port.read(min(4096, max(1, port.in_waiting)))
                    if data:
                        write_all(port, data)
    except KeyboardInterrupt:
        pass
    except (OSError, serial.SerialException) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
