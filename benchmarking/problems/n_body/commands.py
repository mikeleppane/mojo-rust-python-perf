from dataclasses import dataclass

import click

from benchmarking.problems.n_body.runner import NBodyParams, run
from benchmarking.types import TLanguage


@click.command(help="Run the N-body simulation")
@click.option(
    "-l",
    "--language",
    required=True,
    type=click.Choice(
        [
            "python",
            "rust",
            "mojo",
        ]
    ),
    help="Language to run the benchmark in",
)
@click.option(
    "-s", "--steps", default=100, type=click.INT, help="Number of steps to run the simulation"
)
@click.option("-b", "--bench", is_flag=True, type=click.BOOL, help="Run the benchmark")
@click.option("--bodies", type=click.INT, help="Number of bodies in the system")
def n_body(
    language: TLanguage,
    steps: int,
    bench: bool,
    bodies: int,
) -> None:
    n_body_params = NBodyParams(language=language, steps=steps, bench=bench, bodies=bodies)
    run(n_body_params)


@dataclass(frozen=True)
class NBodyCommand:
    def register(self) -> click.Command:  # noqa: PLR6301
        return n_body
