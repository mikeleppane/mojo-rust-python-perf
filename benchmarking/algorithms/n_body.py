"""Pure-Python N-body simulation of the outer solar system.

The classic Computer Language Benchmarks Game problem: the Sun plus the four
gas giants, integrated with a fixed timestep.
"""

import math
from dataclasses import dataclass
from time import perf_counter

PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24
DELTA_T = 0.01
ENERGY_DIFF_THRESHOLD = 1e-4


@dataclass(slots=True)
class Body:
    """A body with 3-D position, velocity and mass."""

    pos: list[float]
    vel: list[float]
    mass: float


def create_initial_system() -> list[Body]:
    """Builds the canonical five-body system (Sun + four gas giants)."""
    return [
        Body([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], SOLAR_MASS),
        Body(
            [4.84143144246472090e00, -1.16032004402742839e00, -1.03622044471123109e-01],
            [
                1.66007664274403694e-03 * DAYS_PER_YEAR,
                7.69901118419740425e-03 * DAYS_PER_YEAR,
                -6.90460016972063023e-05 * DAYS_PER_YEAR,
            ],
            9.54791938424326609e-04 * SOLAR_MASS,
        ),
        Body(
            [8.34336671824457987e00, 4.12479856412430479e00, -4.03523417114321381e-01],
            [
                -2.76742510726862411e-03 * DAYS_PER_YEAR,
                4.99852801234917238e-03 * DAYS_PER_YEAR,
                2.30417297573763929e-05 * DAYS_PER_YEAR,
            ],
            2.85885980666130812e-04 * SOLAR_MASS,
        ),
        Body(
            [1.28943695621391310e01, -1.51111514016986312e01, -2.23307578892655734e-01],
            [
                2.96460137564761618e-03 * DAYS_PER_YEAR,
                2.37847173959480950e-03 * DAYS_PER_YEAR,
                -2.96589568540237556e-05 * DAYS_PER_YEAR,
            ],
            4.36624404335156298e-05 * SOLAR_MASS,
        ),
        Body(
            [1.53796971148509165e01, -2.59193146099879641e01, 1.79258772950371181e-01],
            [
                2.68067772490389322e-03 * DAYS_PER_YEAR,
                1.62824170038242295e-03 * DAYS_PER_YEAR,
                -9.51592254519715870e-05 * DAYS_PER_YEAR,
            ],
            5.15138902046611451e-05 * SOLAR_MASS,
        ),
    ]


def offset_momentum(bodies: list[Body]) -> None:
    """Cancels total momentum by adjusting the first body's (the Sun's) velocity."""
    px = py = pz = 0.0
    for body in bodies:
        px += body.vel[0] * body.mass
        py += body.vel[1] * body.mass
        pz += body.vel[2] * body.mass
    sun = bodies[0]
    sun.vel[0] = -px / SOLAR_MASS
    sun.vel[1] = -py / SOLAR_MASS
    sun.vel[2] = -pz / SOLAR_MASS


def advance(bodies: list[Body], dt: float) -> None:
    """Advances every body by one timestep of length ``dt``."""
    n = len(bodies)
    for i in range(n):
        bi = bodies[i]
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bi.pos[0] - bj.pos[0]
            dy = bi.pos[1] - bj.pos[1]
            dz = bi.pos[2] - bj.pos[2]

            d_squared = dx * dx + dy * dy + dz * dz
            mag = dt / (d_squared * math.sqrt(d_squared))

            bim = bi.mass * mag
            bjm = bj.mass * mag
            bi.vel[0] -= dx * bjm
            bi.vel[1] -= dy * bjm
            bi.vel[2] -= dz * bjm
            bj.vel[0] += dx * bim
            bj.vel[1] += dy * bim
            bj.vel[2] += dz * bim

    for body in bodies:
        body.pos[0] += dt * body.vel[0]
        body.pos[1] += dt * body.vel[1]
        body.pos[2] += dt * body.vel[2]


def energy(bodies: list[Body]) -> float:
    """Total energy (kinetic + gravitational potential) of the system."""
    e = 0.0
    n = len(bodies)
    for i in range(n):
        bi = bodies[i]
        e += 0.5 * bi.mass * (bi.vel[0] ** 2 + bi.vel[1] ** 2 + bi.vel[2] ** 2)
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bi.pos[0] - bj.pos[0]
            dy = bi.pos[1] - bj.pos[1]
            dz = bi.pos[2] - bj.pos[2]
            e -= bi.mass * bj.mass / math.sqrt(dx * dx + dy * dy + dz * dz)
    return e


def run(steps: int) -> tuple[float, bool]:
    """Runs the simulation for ``steps`` steps.

    Returns the wall-clock time of the integration loop in milliseconds and
    whether energy was conserved. Only the loop is timed, so the number is
    comparable with the Rust and Mojo implementations.
    """
    bodies = create_initial_system()
    offset_momentum(bodies)
    initial_energy = energy(bodies)

    start = perf_counter()
    for _ in range(steps):
        advance(bodies, DELTA_T)
    elapsed_ms = (perf_counter() - start) * 1e3

    conserved = abs(energy(bodies) - initial_energy) < ENERGY_DIFF_THRESHOLD
    return elapsed_ms, conserved
