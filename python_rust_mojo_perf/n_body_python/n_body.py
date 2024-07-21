import math
import time
from dataclasses import dataclass

import click

PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24
DELTA_T = 0.01  # timestep
ENERGY_DIFF_THRESHOLD = 1e-4


@dataclass
class Planet:
    pos: list[float]
    vel: list[float]
    mass: float


Sun = Planet([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], SOLAR_MASS)
Jupiter = Planet(
    [4.84143144246472090e00, -1.16032004402742839e00, -1.03622044471123109e-01],
    [
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
    ],
    9.54791938424326609e-04 * SOLAR_MASS,
)

Saturn = Planet(
    [8.34336671824457987e00, 4.12479856412430479e00, -4.03523417114321381e-01],
    [
        -2.76742510726862411e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
    ],
    2.85885980666130812e-04 * SOLAR_MASS,
)

Uranus = Planet(
    [1.28943695621391310e01, -1.51111514016986312e01, -2.23307578892655734e-01],
    [
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
    ],
    4.36624404335156298e-05 * SOLAR_MASS,
)

Neptune = Planet(
    [1.53796971148509165e01, -2.59193146099879641e01, 1.79258772950371181e-01],
    [
        2.68067772490389322e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
    ],
    5.15138902046611451e-05 * SOLAR_MASS,
)


INITIAL_SYSTEM = [Sun, Jupiter, Saturn, Uranus, Neptune]


def offset_momentum(planets: list[Planet]) -> None:
    for i in range(len(planets)):
        for j in range(3):
            Sun.vel[j] -= planets[i].vel[j] * planets[i].mass / SOLAR_MASS


def advance(planets: list[Planet], dt: float) -> None:
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


def energy(planets: list[Planet]) -> float:
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


def simulate(steps: int) -> None:
    """N-body simulation"""
    print("Starting N-BODY simulation...")

    # create the initial state of the system
    offset_momentum(INITIAL_SYSTEM)

    start_energy = energy(INITIAL_SYSTEM)

    # Simulation Main Loop
    for _ in range(steps):
        advance(INITIAL_SYSTEM, DELTA_T)

    end_energy = energy(INITIAL_SYSTEM)

    assert abs(start_energy - end_energy) < ENERGY_DIFF_THRESHOLD


def benchmark(steps: int) -> None:
    print("Starting N-BODY benchmark...")
    print(f"Number of steps: {steps}")

    t_start = time.perf_counter()
    # create the initial state of the system
    offset_momentum(INITIAL_SYSTEM)

    start_energy = energy(INITIAL_SYSTEM)

    # Simulation Main Loop
    for _ in range(steps):
        advance(INITIAL_SYSTEM, DELTA_T)

    end_energy = energy(INITIAL_SYSTEM)

    t_end = time.perf_counter()

    assert abs(start_energy - end_energy) < ENERGY_DIFF_THRESHOLD

    print(f"Time taken: {(t_end - t_start) * 1000:.2f} ms")


@click.command()
@click.option("-s", "--steps", default=100, help="Number of steps to run the simulation")
@click.option("-b", "--bench", is_flag=True, help="Run the benchmark")
def cli(steps: int, bench: bool) -> None:
    if bench:
        benchmark(steps)
    else:
        simulate(steps)


if __name__ == "__main__":
    cli()
