#!/usr/bin/env python3
"""Small, dependency-free performance benchmark for CryptoEdu Pro.

This is intentionally a report-only tool: it does not fail CI on a machine
with variable CPU load. Use it to compare two revisions on the same machine.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from pathlib import Path

# Allow ``python tools/benchmark.py`` to work without requiring installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.service import CryptoOperationService as Service


CASES: dict[str, Callable[[], object]] = {
    "Caesar": lambda: Service.execute("Caesar", "HELLO WORLD " * 100, ["3"], "encrypt"),
    "Vigenere": lambda: Service.execute("Vigenere", "ATTACKATDAWN " * 100, ["LEMON"], "encrypt"),
    "Playfair": lambda: Service.execute("Playfair", "INSTRUMENT" * 100, ["MONARCHY"], "encrypt"),
    "Hill": lambda: Service.execute("Hill", "HITHERE" * 100, ["HILL"], "encrypt"),
    "SDES": lambda: Service.execute("SDES", "10101101", ["1010110011"], "encrypt"),
    "DES": lambda: Service.execute(
        "DES",
        "0000000100100011010001010110011110001001101010111100110111101111",
        ["0001001100110100010101110111100110011011101111001101111111110001"],
        "encrypt",
    ),
    "RSA": lambda: Service.execute("RSA", "HELLO WORLD", ["61", "53", "17"], "encrypt"),
}


def benchmark(operation: Callable[[], object], warmup: int, repeats: int) -> float:
    for _ in range(warmup):
        operation()
    started = time.perf_counter()
    for _ in range(repeats):
        operation()
    return (time.perf_counter() - started) / repeats * 1000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=100, help="timed runs per case (default: 100)")
    parser.add_argument("--warmup", type=int, default=5, help="untimed warmup runs (default: 5)")
    parser.add_argument("--case", choices=["all", *CASES], default="all")
    args = parser.parse_args()
    if args.repeats < 1 or args.warmup < 0:
        parser.error("--repeats must be positive and --warmup cannot be negative")

    selected = CASES if args.case == "all" else {args.case: CASES[args.case]}
    print(f"CryptoEdu Pro benchmark | repeats={args.repeats}, warmup={args.warmup}")
    print("case                 ms/op")
    print("---------------------------")
    for name, operation in selected.items():
        elapsed = benchmark(operation, args.warmup, args.repeats)
        print(f"{name:<20} {elapsed:7.3f}")


if __name__ == "__main__":
    main()
