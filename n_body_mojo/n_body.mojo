from math import sqrt
import math
from benchmark import run, keep
from collections import List
from testing import assert_almost_equal
from python import Python
from collections import InlineList

alias PI = 3.141592653589793
alias SOLAR_MASS = 4 * PI * PI
alias DAYS_PER_YEAR = 365.24
alias DELTA_T = 0.01


@value
struct Planet:
    var position: List[Float64]
    var velocity: List[Float64]
    var mass: Float64


alias Sun = Planet(List[Float64](0.0, 0.0, 0.0), List[Float64](0.0, 0.0, 0.0), mass=SOLAR_MASS)

alias Jupiter = Planet(
    List[Float64](4.84143144246472090e00, -1.16032004402742839e00, -1.03622044471123109e-01),
    List[Float64](
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
    ),
    mass=9.54791938424326609e-04 * SOLAR_MASS,
)

alias Saturn = Planet(
    List[Float64](8.34336671824457987e00, 4.12479856412430479e00, -4.03523417114321381e-01),
    List[Float64](
        -2.76742510726862411e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
    ),
    mass=2.85885980666130812e-04 * SOLAR_MASS,
)

alias Uranus = Planet(
    List[Float64](1.28943695621391310e01, -1.51111514016986312e01, -2.23307578892655734e-01),
    List[Float64](
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
    ),
    mass=4.36624404335156298e-05 * SOLAR_MASS,
)

alias Neptune = Planet(
    List[Float64](1.53796971148509165e01, -2.59193146099879641e01, 1.79258772950371181e-01),
    List[Float64](
        2.68067772490389322e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
    ),
    mass=5.15138902046611451e-05 * SOLAR_MASS,
)

alias INITIAL_SYSTEM = List[Planet](Sun, Jupiter, Saturn, Uranus, Neptune)


fn offset_momentum(inout bodies: List[Planet]):
    var px = 0.0
    var py = 0.0
    var pz = 0.0
    for body in bodies:
        px -= body[].velocity[0] * body[].mass
        py -= body[].velocity[1] * body[].mass
        pz -= body[].velocity[2] * body[].mass

    bodies[0].velocity[0] = px / SOLAR_MASS
    bodies[0].velocity[1] = py / SOLAR_MASS
    bodies[0].velocity[2] = pz / SOLAR_MASS


fn advance(inout bodies: List[Planet], dt: Float64):
    for i in range(len(INITIAL_SYSTEM)):
        for j in range(i + 1, len(INITIAL_SYSTEM)):
            var dx = bodies[j].position[0] - bodies[i].position[0]
            var dy = bodies[j].position[1] - bodies[i].position[1]
            var dz = bodies[j].position[2] - bodies[i].position[2]

            var dSquared = dx * dx + dy * dy + dz * dz
            var distance = sqrt(dSquared)
            var mag = dt / (dSquared * distance)

            var bim = bodies[i].mass
            var bjm = bodies[j].mass

            bodies[i].velocity[0] += dx * bjm * mag
            bodies[i].velocity[1] += dy * bjm * mag
            bodies[i].velocity[2] += dz * bjm * mag

            bodies[j].velocity[0] -= dx * bim * mag
            bodies[j].velocity[1] -= dy * bim * mag
            bodies[j].velocity[2] -= dz * bim * mag

    for body in bodies:
        body[].position[0] += dt * body[].velocity[0]
        body[].position[1] += dt * body[].velocity[1]
        body[].position[2] += dt * body[].velocity[2]


fn energy(borrowed bodies: List[Planet]) -> Float64:
    var e = 0.0
    for i in range(len(INITIAL_SYSTEM)):
        e += (
            0.5
            * bodies[i].mass
            * (
                bodies[i].velocity[0] * bodies[i].velocity[0]
                + bodies[i].velocity[1] * bodies[i].velocity[1]
                + bodies[i].velocity[2] * bodies[i].velocity[2]
            )
        )

        for j in range(i + 1, len(INITIAL_SYSTEM)):
            var dx = bodies[j].position[0] - bodies[i].position[0]
            var dy = bodies[j].position[1] - bodies[i].position[1]
            var dz = bodies[j].position[2] - bodies[i].position[2]

            var distance = sqrt(dx * dx + dy * dy + dz * dz)
            e -= bodies[i].mass * bodies[j].mass / distance

    return e


fn simulate(inout bodies: List[Planet], steps: Int) raises:
    offset_momentum(bodies)

    var initial_energy = energy(bodies)

    for _ in range(steps):
        advance(bodies, DELTA_T)

    var final_energy = energy(bodies)

    assert_almost_equal(initial_energy, final_energy, atol=0.01)


fn benchmark():
    fn benchmark_fn():
        var system = INITIAL_SYSTEM
        offset_momentum(system)
        keep(energy(system))

        for _ in range(1_000):
            advance(system, DELTA_T)

        keep(energy(system))

    run[benchmark_fn](max_runtime_secs=1000).print()


fn main() raises:
    var system = INITIAL_SYSTEM
    simulate(system, 1000000000)
