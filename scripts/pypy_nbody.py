"""Standalone entry point for running the pure-Python n-body under PyPy.

PyPy is an older CPython (3.11) that cannot parse the 3.14-only harness modules,
so this script lives outside the ``benchmarking`` package (keeping the package
directory off ``sys.path[0]``, where it would otherwise shadow stdlib ``types``)
and imports only the dependency-free algorithm. It prints the same
``ELAPSED_MS`` / ``CONSERVED`` lines the other runners emit.

Invoked as ``pypy scripts/pypy_nbody.py <steps>`` by ``benchmarking.runners``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarking.algorithms.n_body import run


def main() -> None:
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    elapsed_ms, conserved = run(steps)
    print(f"ELAPSED_MS {elapsed_ms:.3f}")
    print(f"CONSERVED {conserved}")


if __name__ == "__main__":
    main()
