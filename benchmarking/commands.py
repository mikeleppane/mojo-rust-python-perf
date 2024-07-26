from collections.abc import Iterable

from click import Group

from benchmarking.problems.n_body.commands import NBodyCommand
from benchmarking.types import TCommand

commands: list[TCommand] = [NBodyCommand()]


def register_commands[T: TCommand](cli: Group, commands: Iterable[T]) -> None:
    for command in commands:
        cli.add_command(command.register())
