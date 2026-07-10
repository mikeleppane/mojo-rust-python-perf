"""Shared types for the cross-language benchmark harness."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, get_args

type Language = Literal["python", "pypy", "numpy", "rust", "mojo-naive", "mojo"]

LANGUAGES: tuple[Language, ...] = get_args(Language.__value__)

# Display names for report tables (raw value -> label).
LANGUAGE_LABELS: dict[Language, str] = {
    "python": "Python",
    "pypy": "PyPy",
    "numpy": "NumPy",
    "rust": "Rust",
    "mojo-naive": "Mojo (naive)",
    "mojo": "Mojo (SIMD)",
}


class Problem(StrEnum):
    """A benchmark problem, implemented in several languages."""

    N_BODY = "n-body"
    PIDIGITS = "pidigits"

    @property
    def size_label(self) -> str:
        """Human name for the problem's size parameter."""
        return "steps" if self is Problem.N_BODY else "digits"


@dataclass(frozen=True, slots=True)
class BenchResult:
    """The outcome of a single (problem, language, size) benchmark run."""

    problem: Problem
    language: Language
    size: int
    elapsed_ms: float
    ok: bool
