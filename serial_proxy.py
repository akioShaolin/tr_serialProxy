"""Compatibility launcher; install the package first (pip install -e .)."""

from tr_serial_proxy.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
