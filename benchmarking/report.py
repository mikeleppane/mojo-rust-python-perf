"""Turn benchmark results into a JSON record and Markdown tables."""

import json
import math
from collections.abc import Iterable
from pathlib import Path

from benchmarking import paths, runners
from benchmarking.types import BenchResult, Language, Problem

_BASELINE: Language = "python"
_MS_PER_SECOND = 1000


def write(results: list[BenchResult]) -> tuple[Path, Path]:
    """Writes ``results.json`` and ``results.md`` to the results directory."""
    paths.RESULTS_DIR.mkdir(exist_ok=True)
    json_path = paths.RESULTS_DIR / "results.json"
    md_path = paths.RESULTS_DIR / "results.md"
    json_path.write_text(to_json(results), encoding="utf-8")
    md_path.write_text(markdown(results), encoding="utf-8")
    return json_path, md_path


def to_json(results: list[BenchResult]) -> str:
    """Serialises results to a stable JSON document."""
    payload = {
        "results": [
            {
                "problem": r.problem.value,
                "language": r.language,
                "size": r.size,
                "elapsed_ms": None if math.isnan(r.elapsed_ms) else r.elapsed_ms,
                "ok": r.ok,
            }
            for r in results
        ]
    }
    return json.dumps(payload, indent=2)


def markdown(results: list[BenchResult]) -> str:
    """Renders per-problem timing and speedup tables as Markdown."""
    sections: list[str] = []
    for problem in Problem:
        problem_results = [r for r in results if r.problem is problem]
        if not problem_results:
            continue
        sections.append(_problem_section(problem, problem_results))
    return "\n\n".join(sections)


def _problem_section(problem: Problem, results: list[BenchResult]) -> str:
    languages = runners.supported_languages(problem)
    sizes = sorted({r.size for r in results})
    lookup = {(r.language, r.size): r.elapsed_ms for r in results}

    header = f"### {problem.value}\n\n_Time (lower is better)_\n"
    time_table = _table(
        head=[problem.size_label, *languages],
        rows=[
            [f"{size:,}", *[_fmt_ms(lookup.get((lang, size))) for lang in languages]]
            for size in sizes
        ],
    )

    speedup_head = [problem.size_label, *[f"{lang} x" for lang in languages]]
    speedup_rows = [
        [
            f"{size:,}",
            *[
                _fmt_speedup(lookup.get((lang, size)), lookup.get((_BASELINE, size)))
                for lang in languages
            ],
        ]
        for size in sizes
    ]
    speedup_table = _table(head=speedup_head, rows=speedup_rows)

    return (
        f"{header}\n{time_table}\n\n_Speedup vs. pure Python (higher is better)_\n\n{speedup_table}"
    )


def _table(head: list[str], rows: Iterable[list[str]]) -> str:
    aligns = ["---:"] * len(head)
    aligns[0] = ":---"
    lines = [
        "| " + " | ".join(head) + " |",
        "| " + " | ".join(aligns) + " |",
        *["| " + " | ".join(row) + " |" for row in rows],
    ]
    return "\n".join(lines)


def _fmt_ms(value: float | None) -> str:
    if value is None or math.isnan(value):
        return "—"
    if value >= _MS_PER_SECOND:
        return f"{value:,.0f} ms"
    if value >= 1:
        return f"{value:.2f} ms"
    return f"{value:.3f} ms"


def _fmt_speedup(value: float | None, baseline: float | None) -> str:
    if value is None or baseline is None or math.isnan(value) or math.isnan(baseline) or value == 0:
        return "—"
    return f"{baseline / value:,.1f}x"
