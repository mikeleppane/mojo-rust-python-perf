"""Filesystem locations of the build artifacts for each language."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Rust binaries land in the shared workspace target directory.
RUST_TARGET_DIR = REPO_ROOT / "target" / "release"

# The Mojo project (pixi manifest + sources + compiled binary).
MOJO_DIR = REPO_ROOT / "n_body_mojo"
MOJO_MANIFEST = MOJO_DIR / "pixi.toml"
MOJO_N_BODY_BIN = MOJO_DIR / "n_body"

# Where `compare` writes its results.
RESULTS_DIR = REPO_ROOT / "results"
