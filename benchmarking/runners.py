"""Run a benchmark problem in a given language and capture its timing.

Python and NumPy run in-process. Rust and Mojo run as subprocesses that print a
machine-readable ``ELAPSED_MS <float>`` line, which we parse back out.
"""

import os
import re
import subprocess

from benchmarking import paths
from benchmarking.algorithms import n_body, n_body_numpy, pidigits
from benchmarking.types import Language, Problem

_ELAPSED_RE = re.compile(r"ELAPSED_MS\s+([0-9.]+)")
_CONSERVED_RE = re.compile(r"CONSERVED\s+(true|false)")


def pin_to_core(core: int) -> None:
    """Pins this process to a single CPU core (Linux only).

    Subprocesses inherit the affinity, so this stabilises timings across all
    languages by cutting scheduler migration and multi-core turbo noise. A no-op
    on platforms without ``sched_setaffinity``.
    """
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {core})


# Which languages implement each problem.
_SUPPORTED: dict[Problem, tuple[Language, ...]] = {
    Problem.N_BODY: ("python", "numpy", "rust", "mojo"),
    Problem.PIDIGITS: ("python", "rust"),
}


def supported_languages(problem: Problem) -> tuple[Language, ...]:
    """Languages that implement ``problem``."""
    return _SUPPORTED[problem]


class BenchmarkError(RuntimeError):
    """A benchmark run failed to produce a timing."""


def run(problem: Problem, language: Language, size: int) -> tuple[float, bool]:
    """Runs one benchmark and returns ``(elapsed_ms, ok)``.

    ``ok`` reports whether the result passed its correctness check (energy
    conservation for n-body). The externally-timed Rust and Mojo runners report
    it via a machine-readable ``CONSERVED true|false`` line; a run without such a
    line (e.g. pidigits, which has no conservation check) is treated as ``True``.
    """
    if language not in supported_languages(problem):
        raise BenchmarkError(f"{language} does not implement {problem}")
    match language:
        case "python":
            return _run_python(problem, size)
        case "numpy":
            return n_body_numpy.run(size)
        case "rust":
            return _run_rust(problem, size)
        case "mojo":
            return _run_mojo(problem, size)


def _run_python(problem: Problem, size: int) -> tuple[float, bool]:
    if problem is Problem.N_BODY:
        return n_body.run(size)
    elapsed_ms, _pi = pidigits.run(size)
    return elapsed_ms, True


def _parse_result(stdout: str, context: str) -> tuple[float, bool]:
    """Extracts ``(elapsed_ms, ok)`` from a runner's machine-readable output.

    ``ok`` is ``True`` unless a ``CONSERVED false`` line is present; a run with
    no ``CONSERVED`` line at all (e.g. pidigits) is treated as passing.
    """
    match = _ELAPSED_RE.search(stdout)
    if match is None:
        raise BenchmarkError(f"no ELAPSED_MS line in {context} output:\n{stdout}")
    conserved = _CONSERVED_RE.search(stdout)
    ok = conserved is None or conserved.group(1) == "true"
    return float(match.group(1)), ok


def _run_subprocess(cmd: list[str], context: str, cwd: str | None = None) -> tuple[float, bool]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=cwd)
    except FileNotFoundError as exc:
        raise BenchmarkError(f"{context}: command not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise BenchmarkError(f"{context} exited {exc.returncode}:\n{exc.stderr}") from exc
    return _parse_result(proc.stdout, context)


def _run_rust(problem: Problem, size: int) -> tuple[float, bool]:
    ensure_rust_built()
    binary = paths.RUST_TARGET_DIR / (
        "n_body_rust" if problem is Problem.N_BODY else "pidigits_rust"
    )
    flag = "--steps" if problem is Problem.N_BODY else "--digits"
    return _run_subprocess([str(binary), flag, str(size)], context=f"rust {problem}")


def _run_mojo(problem: Problem, size: int) -> tuple[float, bool]:
    if problem is not Problem.N_BODY:
        raise BenchmarkError(f"mojo does not implement {problem}")
    ensure_mojo_built()
    cmd = [
        "pixi",
        "run",
        "--manifest-path",
        str(paths.MOJO_MANIFEST),
        str(paths.MOJO_N_BODY_BIN),
        str(size),
    ]
    return _run_subprocess(cmd, context="mojo n-body")


def ensure_rust_built() -> None:
    """Builds the Rust release binaries if they are missing."""
    binaries = [paths.RUST_TARGET_DIR / "n_body_rust", paths.RUST_TARGET_DIR / "pidigits_rust"]
    if all(b.exists() for b in binaries):
        return
    subprocess.run(
        ["cargo", "build", "--release", "--workspace"],
        cwd=str(paths.REPO_ROOT),
        check=True,
    )


def ensure_mojo_built() -> None:
    """Builds the Mojo n-body binary if it is missing or out of date."""
    source = paths.MOJO_DIR / "n_body.mojo"
    binary = paths.MOJO_N_BODY_BIN
    if binary.exists() and binary.stat().st_mtime >= source.stat().st_mtime:
        return
    subprocess.run(
        [
            "pixi",
            "run",
            "--manifest-path",
            str(paths.MOJO_MANIFEST),
            "mojo",
            "build",
            str(source),
            "-O3",
            "-o",
            str(binary),
        ],
        check=True,
    )
