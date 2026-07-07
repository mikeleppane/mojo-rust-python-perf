"""Correctness tests for the Mojo n-body simulation.

Run with: `pixi run test` (or `mojo run -I . test_n_body.mojo`).
"""

from std.testing import TestSuite, assert_almost_equal

from n_body import (
    DELTA_T,
    advance,
    create_initial_system,
    energy,
    offset_momentum,
)

# Reference initial energy of the canonical 5-body system after momentum offset,
# from the Computer Language Benchmarks Game n-body problem.
comptime REFERENCE_ENERGY = -0.169075164


def test_initial_energy() raises:
    var bodies = create_initial_system()
    offset_momentum(bodies)
    assert_almost_equal(energy(bodies), REFERENCE_ENERGY, atol=1e-6)


def test_energy_is_conserved() raises:
    var bodies = create_initial_system()
    offset_momentum(bodies)
    var initial = energy(bodies)
    for _ in range(100_000):
        advance(bodies, DELTA_T)
    assert_almost_equal(energy(bodies), initial, atol=1e-4)


def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()
