"""Vectorised N-body simulation using NumPy.

Same physics as :mod:`benchmarking.algorithms.n_body`, but every timestep
operates on the whole system at once with array broadcasting. For the tiny
five-body system this trades per-element speed for per-step Python/NumPy
overhead, which is itself an instructive comparison point.
"""

from time import perf_counter

import numpy as np
from numpy.typing import NDArray

from benchmarking.algorithms.n_body import (
    DELTA_T,
    ENERGY_DIFF_THRESHOLD,
    SOLAR_MASS,
    create_initial_system,
)

type F64Array = NDArray[np.float64]


def _initial_arrays() -> tuple[F64Array, F64Array, F64Array]:
    bodies = create_initial_system()
    pos = np.array([b.pos for b in bodies], dtype=np.float64)
    vel = np.array([b.vel for b in bodies], dtype=np.float64)
    mass = np.array([b.mass for b in bodies], dtype=np.float64)
    return pos, vel, mass


def offset_momentum(vel: F64Array, mass: F64Array) -> None:
    """Cancels total momentum via the first body (the Sun)."""
    vel[0] = -(vel * mass[:, None]).sum(axis=0) / SOLAR_MASS


def advance(pos: F64Array, vel: F64Array, mass: F64Array, dt: float) -> None:
    """Advances the whole system by one timestep of length ``dt``."""
    dpos = pos[:, None, :] - pos[None, :, :]  # (N, N, 3): dpos[i, j] = pos[i] - pos[j]
    dist2 = (dpos * dpos).sum(axis=-1)  # (N, N)
    np.fill_diagonal(dist2, 1.0)  # avoid division by zero on the diagonal
    inv_dist3 = dist2**-1.5
    np.fill_diagonal(inv_dist3, 0.0)  # a body exerts no force on itself

    factor = mass[None, :] * inv_dist3  # (N, N)
    vel -= dt * np.einsum("ij,ijk->ik", factor, dpos)
    pos += dt * vel


def energy(pos: F64Array, vel: F64Array, mass: F64Array) -> float:
    """Total energy (kinetic + gravitational potential) of the system."""
    kinetic = 0.5 * (mass * (vel * vel).sum(axis=1)).sum()
    dpos = pos[:, None, :] - pos[None, :, :]
    dist = np.sqrt((dpos * dpos).sum(axis=-1))
    upper = np.triu_indices(len(mass), k=1)
    potential = -(np.outer(mass, mass)[upper] / dist[upper]).sum()
    return float(kinetic + potential)


def run(steps: int) -> tuple[float, bool]:
    """Runs the vectorised simulation for ``steps`` steps.

    Returns the wall-clock time of the integration loop in milliseconds and
    whether energy was conserved.
    """
    pos, vel, mass = _initial_arrays()
    offset_momentum(vel, mass)
    initial_energy = energy(pos, vel, mass)

    start = perf_counter()
    for _ in range(steps):
        advance(pos, vel, mass, DELTA_T)
    elapsed_ms = (perf_counter() - start) * 1e3

    conserved = abs(energy(pos, vel, mass) - initial_energy) < ENERGY_DIFF_THRESHOLD
    return elapsed_ms, conserved
