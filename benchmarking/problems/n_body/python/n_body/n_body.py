import math
import time
from dataclasses import dataclass
from random import uniform

import click

from benchmarking.types import Problem, ProblemType

PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24
DELTA_T = 0.01  # timestep
ENERGY_DIFF_THRESHOLD = 1e-4


@dataclass
class Body:
    pos: list[float]
    vel: list[float]
    mass: float


Sun = Body([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], SOLAR_MASS)
Jupiter = Body(
    [4.84143144246472090e00, -1.16032004402742839e00, -1.03622044471123109e-01],
    [
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
    ],
    9.54791938424326609e-04 * SOLAR_MASS,
)

Saturn = Body(
    [8.34336671824457987e00, 4.12479856412430479e00, -4.03523417114321381e-01],
    [
        -2.76742510726862411e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
    ],
    2.85885980666130812e-04 * SOLAR_MASS,
)

Uranus = Body(
    [1.28943695621391310e01, -1.51111514016986312e01, -2.23307578892655734e-01],
    [
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
    ],
    4.36624404335156298e-05 * SOLAR_MASS,
)

Neptune = Body(
    [1.53796971148509165e01, -2.59193146099879641e01, 1.79258772950371181e-01],
    [
        2.68067772490389322e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
    ],
    5.15138902046611451e-05 * SOLAR_MASS,
)


def create_n_bodies(n: int) -> list[Body]:
    bodies = [
        Body(
            [uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)],
            [uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)],
            5.0e-05 * SOLAR_MASS * uniform(0.1, 1),
        )
        for _ in range(n - 1)
    ]
    bodies.insert(0, Sun)
    return bodies


INITIAL_SYSTEM = [Sun, Jupiter, Saturn, Uranus, Neptune]


def offset_momentum(planets: list[Body]) -> None:
    for i in range(len(planets)):
        for j in range(3):
            planets[0].vel[j] -= planets[i].vel[j] * planets[i].mass / SOLAR_MASS


def advance(planets: list[Body], dt: float) -> None:
    N = len(planets)
    for i in range(N):
        for j in range(i + 1, N):
            dx = planets[i].pos[0] - planets[j].pos[0]
            dy = planets[i].pos[1] - planets[j].pos[1]
            dz = planets[i].pos[2] - planets[j].pos[2]

            dSquared = dx * dx + dy * dy + dz * dz
            distance = math.sqrt(dSquared)
            mag = dt / (dSquared * distance)

            planets[i].vel[0] -= dx * planets[j].mass * mag
            planets[i].vel[1] -= dy * planets[j].mass * mag
            planets[i].vel[2] -= dz * planets[j].mass * mag

            planets[j].vel[0] += dx * planets[i].mass * mag
            planets[j].vel[1] += dy * planets[i].mass * mag
            planets[j].vel[2] += dz * planets[i].mass * mag

    for i in range(N):
        planets[i].pos[0] += dt * planets[i].vel[0]
        planets[i].pos[1] += dt * planets[i].vel[1]
        planets[i].pos[2] += dt * planets[i].vel[2]


def energy(planets: list[Body]) -> float:
    e = 0.0
    N = len(planets)
    for i in range(N):
        e += (
            0.5
            * planets[i].mass
            * (
                planets[i].vel[0] * planets[i].vel[0]
                + planets[i].vel[1] * planets[i].vel[1]
                + planets[i].vel[2] * planets[i].vel[2]
            )
        )

        for j in range(i + 1, N):
            dx = planets[i].pos[0] - planets[j].pos[0]
            dy = planets[i].pos[1] - planets[j].pos[1]
            dz = planets[i].pos[2] - planets[j].pos[2]

            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            e -= (planets[i].mass * planets[j].mass) / distance

    return e


def simulate(system: list[Body], steps: int) -> None:
    """N-body simulation"""
    print("Starting N-BODY simulation...")

    # create the initial state of the system
    offset_momentum(system)

    start_energy = energy(system)

    # Simulation Main Loop
    for _ in range(steps):
        advance(system, DELTA_T)

    end_energy = energy(system)

    if abs(start_energy - end_energy) < ENERGY_DIFF_THRESHOLD:
        click.secho("Energy conserved", fg="green")
    else:
        click.secho(f"Energy not conserved: Got {end_energy}, expected {start_energy}", fg="red")


def benchmark(system: list[Body], steps: int) -> None:
    print("Starting N-BODY benchmark...")
    print(f"Number of steps: {steps}")

    t_start = time.perf_counter()
    # create the initial state of the system
    offset_momentum(system)

    start_energy = energy(system)

    # Simulation Main Loop system
    for _ in range(steps):
        advance(system, DELTA_T)

    end_energy = energy(system)

    t_end = time.perf_counter()

    if abs(start_energy - end_energy) < ENERGY_DIFF_THRESHOLD:
        click.secho("Energy conserved", fg="green")
    else:
        click.secho(f"Energy not conserved: Got {end_energy}, expected {start_energy}", fg="red")

    click.secho(f"Time taken: {(t_end - t_start) * 1000:.2f} ms", fg="blue")


@dataclass(frozen=True)
class NBodyPython(Problem):
    type: ProblemType

    steps: int
    bodies: int | None = None

    def solve(self) -> None:
        system = create_n_bodies(self.bodies) if self.bodies else INITIAL_SYSTEM
        simulate(system, self.steps)

    def benchmark(self) -> None:
        system = create_n_bodies(self.bodies) if self.bodies else INITIAL_SYSTEM
        benchmark(system, self.steps)
