"""Correctness tests for the n-body implementations."""

from benchmarking.algorithms import n_body, n_body_numpy

# Reference initial energy of the canonical 5-body system after momentum offset,
# from the Computer Language Benchmarks Game n-body problem.
REFERENCE_ENERGY = -0.169075164
TOL = 1e-8


def test_pure_python_initial_energy() -> None:
    bodies = n_body.create_initial_system()
    n_body.offset_momentum(bodies)
    assert abs(n_body.energy(bodies) - REFERENCE_ENERGY) < TOL


def test_pure_python_conserves_energy() -> None:
    _, conserved = n_body.run(steps=50_000)
    assert conserved


def test_numpy_initial_energy_matches_pure_python() -> None:
    pos, vel, mass = n_body_numpy._initial_arrays()
    n_body_numpy.offset_momentum(vel, mass)
    assert abs(n_body_numpy.energy(pos, vel, mass) - REFERENCE_ENERGY) < TOL


def test_numpy_conserves_energy() -> None:
    _, conserved = n_body_numpy.run(steps=50_000)
    assert conserved


def test_numpy_matches_pure_python_trajectory() -> None:
    steps = 1_000
    py_bodies = n_body.create_initial_system()
    n_body.offset_momentum(py_bodies)
    for _ in range(steps):
        n_body.advance(py_bodies, n_body.DELTA_T)
    py_energy = n_body.energy(py_bodies)

    pos, vel, mass = n_body_numpy._initial_arrays()
    n_body_numpy.offset_momentum(vel, mass)
    for _ in range(steps):
        n_body_numpy.advance(pos, vel, mass, n_body.DELTA_T)
    np_energy = n_body_numpy.energy(pos, vel, mass)

    assert abs(py_energy - np_energy) < 1e-9
