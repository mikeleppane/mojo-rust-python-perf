from enum import StrEnum
from typing import Literal, Protocol, runtime_checkable

from click import Command

type TLanguage = Literal["python", "rust", "mojo"]


@runtime_checkable
class TCommand(Protocol):
    def register(self) -> Command: ...


class ProblemType(StrEnum):
    N_BODY = "n_body"


@runtime_checkable
class Problem(Protocol):
    type: ProblemType

    def solve(self) -> None: ...

    def benchmark(self) -> None: ...


@runtime_checkable
class Runner(Protocol):
    problem: Problem
    language: TLanguage

    def execute(self) -> None: ...
