# Mojo, Rust and Python: a performance comparison

The same two numerical problems implemented in **Python** (pure and NumPy),
**Rust**, and **Mojo**, timed under a single harness.

- **n-body** — gravitational simulation of the Sun and the four gas giants
  (the classic [Benchmarks Game](https://benchmarksgame-team.pages.debian.net/benchmarksgame/description/nbody.html)
  problem), swept over the number of integration steps.
- **pidigits** — digits of π via the Chudnovsky algorithm with binary splitting
  (Python's `decimal` vs Rust's GMP/MPFR via `rug`), swept over the number of digits.

> Background reading: [Medium post on the topic](https://medium.com/@mleppan23/rust-hashmaps-a-hands-on-comparison-b20123e80353).

## Results

Measured on an Intel Core i9-14900K, Ubuntu 24.04 (Linux 6.17), with
Python 3.14.5, Rust 1.96.0 and Mojo 1.0.0b2. Each cell is the fastest of 9 runs,
pinned to a single CPU core; **only the compute is timed**
(see [Methodology](#methodology)).

### n-body — time (lower is better)

| steps | Python | NumPy | Rust | Mojo |
| :--- | ---: | ---: | ---: | ---: |
| 10,000 | 25.2 ms | 57.6 ms | 0.30 ms | 0.29 ms |
| 100,000 | 254 ms | 574 ms | 2.96 ms | 3.00 ms |
| 1,000,000 | 2,541 ms | 5,749 ms | 29.6 ms | 27.9 ms |

### n-body — speedup vs. pure Python (higher is better)

| steps | Python | NumPy | Rust | Mojo |
| :--- | ---: | ---: | ---: | ---: |
| 10,000 | 1× | 0.4× | 85× | 86× |
| 100,000 | 1× | 0.4× | 86× | 85× |
| 1,000,000 | 1× | 0.4× | 86× | 91× |

### pidigits — time (lower is better)

| digits | Python | Rust | Rust speedup |
| :--- | ---: | ---: | ---: |
| 1,000 | 0.33 ms | 0.034 ms | 10× |
| 10,000 | 31.1 ms | 0.48 ms | 65× |
| 100,000 | 1,269 ms | 11.1 ms | 115× |

### What the numbers say

- **Rust and Mojo are a dead heat.** They trade the lead across sizes and runs
  (at 1M steps this run: Mojo 27.9 vs Rust 29.6 ms), both ~85–91× pure Python.
  The differences sit inside run-to-run variance — there is no consistent winner.
- **SIMD is not a silver bullet here.** Mojo uses 4-wide SIMD vectors (one lane
  wasted on a 3-D problem) plus a horizontal `reduce_add`; Rust uses scalar
  `[f64; 3]` with explicit FMA. Both saturate the same FP units, so they tie.
- **NumPy is *slower* than pure Python here.** Vectorising a five-body system
  pays per-step array-allocation overhead that never amortises: the arrays are
  tiny and the step loop still runs in Python. NumPy wins when *N* is large, not
  when the step count is. An honest reminder that "vectorise it" is not free.
- **pidigits is a big-integer story.** Rust's GMP/MPFR backend pulls further
  ahead of Python's `decimal` as precision grows (10× → 115×), because the
  asymptotically better big-number kernels dominate.
- Mojo has no standard-library big-integer type, so pidigits is Python-vs-Rust
  only.

Reproduce with `make compare` (writes `results/results.json` and `results/results.md`).
Timings are sensitive to scheduler and turbo noise, so the harness pins to one
core (`--core`); without it, run-to-run spread can reach 2× on the sub-10 ms cells.

## Methodology

Comparing *languages* means comparing the algorithm, not the runtime's start-up
cost. So each implementation times **only the hot region** with a monotonic
clock — the integration loop for n-body, the Chudnovsky computation for pidigits
— and prints `ELAPSED_MS <value>`. Process start-up, interpreter boot, NumPy
import, argument parsing and result formatting are all excluded. The Python and
NumPy variants are timed in-process; Rust and Mojo run as release binaries (`target-cpu=native`, `-O3`)
whose self-reported time the harness reads back. The harness pins itself (and,
by inheritance, the subprocesses) to one CPU core to cut scheduler and turbo
noise. Every case is run 9 times and the minimum is kept (the least-perturbed
sample). All implementations are single-threaded.

## Getting started

You need [uv](https://docs.astral.sh/uv/), a Rust toolchain (1.85+ for edition
2024) and [pixi](https://pixi.sh/) (for Mojo).

```bash
uv sync                       # Python 3.14 env + dev tools
cargo build --release         # Rust binaries
make build                    # also builds the Mojo binary via pixi
```

Run one case:

```bash
uv run benchmarks n-body  -l mojo   -s 1000000 -r 9 --core 3
uv run benchmarks n-body  -l numpy  -s 100000
uv run benchmarks pidigits -l rust  -d 100000
```

Run the whole comparison:

```bash
make compare        # builds everything, then sweeps all languages and sizes
```

## Developing

A single `Makefile` fronts all three toolchains:

| command | what it does |
| :--- | :--- |
| `make check` | lint, type-check and test Python, Rust and Mojo |
| `make fix` | auto-format everything (ruff, rustfmt, mojo format) |
| `make test` | run the three test suites |
| `make build` | build the Rust + Mojo release binaries |
| `make compare` | run the full cross-language comparison |

- **Python** — uv + [ruff](https://docs.astral.sh/ruff/) (lint + format) + mypy
  (strict) + pytest.
- **Rust** — a Cargo workspace (`n_body_rust`, `pidigits_rust`), edition 2024,
  `cargo fmt` + `clippy -W pedantic` + tests + Criterion benches (`cargo bench`).
- **Mojo** — a pixi project in `n_body_mojo/`; `pixi run test`, `pixi run build`.

## Layout

```text
benchmarking/            Python package: CLI, harness, report generator
  algorithms/            pure-Python + NumPy reference implementations
  runners.py             runs each language and captures timings
n_body_rust/             Rust crate: n-body        (workspace member)
pidigits_rust/           Rust crate: pidigits      (workspace member)
n_body_mojo/             Mojo project (pixi): n-body in modern Mojo
tests/                   Python correctness tests
```

## Notes on the modernisation

This repository was brought up to date from an older revision:

- **Two real bugs fixed** in the Rust n-body: the kinetic-energy term dropped
  the *z* velocity component, and Uranus's *z* position had a typo'd exponent
  (`e-101`). Both are now covered by a reference-energy test.
- **Rust** moved to a Cargo workspace on edition 2024; the `clang`/`lld` linker
  override (which broke builds where `lld` is absent) was removed.
- **Python** migrated from Poetry to uv with a PEP 621 layout, targeting
  Python 3.14; black + isort were dropped in favour of ruff.
- **Mojo** was rewritten from pre-1.0 syntax (`inout`, `let`, `@value`, `alias`,
  `time.now()`) to Mojo 1.0 (`mut`, `comptime`, `@fieldwise_init`, SIMD vectors),
  and an off-by-one (`i+i`) in the old SIMD variant was fixed. The dead
  Python-shelling "pidigits" Mojo file was removed.
