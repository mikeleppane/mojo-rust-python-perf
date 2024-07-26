import click

from benchmarking.commands import commands, register_commands


@click.group()
def cli() -> None:
    pass


register_commands(cli, commands=commands)
