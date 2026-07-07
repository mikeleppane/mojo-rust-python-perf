"""Command-line interface for the cross-language benchmark suite."""

from typing import cast

import click

from benchmarking import report, runners
from benchmarking.types import BenchResult, Language, Problem

# Default problem sizes swept by ``compare``.
DEFAULT_STEPS = (10_000, 100_000, 1_000_000)
DEFAULT_DIGITS = (1_000, 10_000, 100_000)


@click.group()
def cli() -> None:
    """Benchmark the same algorithms across Python, NumPy, Rust and Mojo."""


def _language_choice(problem: Problem) -> click.Choice[str]:
    return click.Choice(runners.supported_languages(problem))


def _maybe_pin(core: int | None) -> None:
    if core is not None:
        runners.pin_to_core(core)
        click.secho(f"Pinned to CPU core {core}", fg="cyan", err=True)


_core_option = click.option(
    "--core", type=int, default=None, help="Pin to this CPU core for stable timings (Linux)."
)


@cli.command(name="n-body")
@click.option("-l", "--language", type=_language_choice(Problem.N_BODY), required=True)
@click.option("-s", "--steps", default=100_000, show_default=True, help="Integration steps.")
@click.option("-r", "--repeat", default=1, show_default=True, help="Runs; the fastest is reported.")
@_core_option
def n_body_cmd(language: str, steps: int, repeat: int, core: int | None) -> None:
    """Run the N-body simulation in a single language."""
    _maybe_pin(core)
    _run_single(Problem.N_BODY, language, steps, repeat)


@cli.command(name="pidigits")
@click.option("-l", "--language", type=_language_choice(Problem.PIDIGITS), required=True)
@click.option("-d", "--digits", default=10_000, show_default=True, help="Digits of pi.")
@click.option("-r", "--repeat", default=1, show_default=True, help="Runs; the fastest is reported.")
@_core_option
def pidigits_cmd(language: str, digits: int, repeat: int, core: int | None) -> None:
    """Compute digits of pi in a single language."""
    _maybe_pin(core)
    _run_single(Problem.PIDIGITS, language, digits, repeat)


@cli.command()
@click.option("--repeat", default=5, show_default=True, help="Runs per case; the fastest counts.")
@click.option("--steps", default=DEFAULT_STEPS, multiple=True, type=int, help="N-body step counts.")
@click.option("--digits", default=DEFAULT_DIGITS, multiple=True, type=int, help="Pidigits sizes.")
@_core_option
def compare(repeat: int, steps: tuple[int, ...], digits: tuple[int, ...], core: int | None) -> None:
    """Run every language across a range of sizes and write a comparison report."""
    _maybe_pin(core)
    sizes = {Problem.N_BODY: steps, Problem.PIDIGITS: digits}
    results: list[BenchResult] = []

    for problem in Problem:
        for language in runners.supported_languages(problem):
            for size in sizes[problem]:
                result = _best_of(problem, language, size, repeat)
                results.append(result)
                status = "" if result.ok else click.style(" [check FAILED]", fg="red")
                click.echo(
                    f"{problem:>8} {language:>6} {size:>9,} {problem.size_label}: "
                    f"{result.elapsed_ms:9.3f} ms{status}"
                )

    json_path, md_path = report.write(results)
    click.secho(f"\nWrote {json_path}", fg="green")
    click.secho(f"Wrote {md_path}", fg="green")
    click.echo("\n" + report.markdown(results))


def _best_of(problem: Problem, language: str, size: int, repeat: int) -> BenchResult:
    lang = cast(Language, language)  # guaranteed valid by click.Choice
    best = float("inf")
    ok = True
    for _ in range(repeat):
        try:
            elapsed_ms, run_ok = runners.run(problem, lang, size)
        except runners.BenchmarkError as exc:
            click.secho(f"  {lang} {problem} {size} failed: {exc}", fg="red", err=True)
            return BenchResult(problem, lang, size, float("nan"), ok=False)
        best = min(best, elapsed_ms)
        ok = ok and run_ok
    return BenchResult(problem, lang, size, best, ok=ok)


def _run_single(problem: Problem, language: str, size: int, repeat: int) -> None:
    result = _best_of(problem, language, size, repeat)
    if not result.ok:
        raise SystemExit(1)
    label = problem.size_label
    click.secho(
        f"{problem} [{language}] {size:,} {label}: {result.elapsed_ms:.3f} ms",
        fg="blue",
    )
