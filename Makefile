# Single entry point for the Python / Rust / Mojo benchmark project.
#
#   make check   - lint, type-check and test all three languages
#   make fix     - auto-format all three languages
#   make test    - run the test suites
#   make build   - build the Rust + Mojo release binaries
#   make compare - run the full cross-language comparison

PY_SRC   := benchmarking tests
MOJO      := pixi run --manifest-path n_body_mojo/pixi.toml

.PHONY: check fix test build compare \
        check-python check-rust check-mojo \
        fix-python fix-rust fix-mojo \
        test-python test-rust test-mojo clean

check: check-python check-rust check-mojo
fix: fix-python fix-rust fix-mojo
test: test-python test-rust test-mojo

# --- Python (uv + ruff + mypy + pytest) ------------------------------------
check-python:
	uv run ruff check $(PY_SRC)
	uv run ruff format --check $(PY_SRC)
	uv run mypy $(PY_SRC)
	uv run pytest

fix-python:
	uv run ruff format $(PY_SRC)
	uv run ruff check --fix $(PY_SRC)

test-python:
	uv run pytest

# --- Rust (cargo fmt + clippy + test) --------------------------------------
check-rust:
	cargo fmt --check
	cargo clippy --workspace --all-targets -- -D warnings -W clippy::pedantic
	cargo test --workspace

fix-rust:
	cargo fmt

test-rust:
	cargo test --workspace

# --- Mojo (pixi: format-check + test) --------------------------------------
# mojo format has no --check mode, so verify formatting is idempotent: hash the
# sources, format in place, and fail if anything changed.
check-mojo:
	@before=$$(find n_body_mojo -name '*.mojo' | sort | xargs md5sum); \
	$(MOJO) fmt >/dev/null; \
	after=$$(find n_body_mojo -name '*.mojo' | sort | xargs md5sum); \
	[ "$$before" = "$$after" ] || { echo "Mojo files not formatted; run: make fix-mojo"; exit 1; }
	$(MOJO) test

fix-mojo:
	$(MOJO) fmt

test-mojo:
	$(MOJO) test

# --- Build + run -----------------------------------------------------------
build:
	cargo build --release --workspace
	$(MOJO) build

compare: build
	uv run benchmarks compare

clean:
	cargo clean
	rm -f n_body_mojo/n_body n_body_mojo/n_body_naive
	rm -rf results
