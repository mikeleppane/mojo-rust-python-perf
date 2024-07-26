from typing import TypedDict

from benchmarking.problems.n_body.python.n_body.n_body import NBodyPython
from benchmarking.types import ProblemType, TLanguage


class NBodyParams(TypedDict):
    language: TLanguage
    steps: int
    bench: bool
    bodies: int | None


def run(params: NBodyParams) -> None:
    match params["language"]:
        case "python":
            problem = NBodyPython(
                type=ProblemType.N_BODY,
                steps=params["steps"],
                bodies=params["bodies"],
            )
            if params["bench"]:
                problem.benchmark()
            else:
                problem.solve()
        case "rust":
            pass
        case "mojo":
            pass
        case _:
            raise ValueError(
                f"Invalid language: {params["language"]}. Please choose from python, rust, mojo"
            )
