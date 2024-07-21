from math import sqrt
from benchmark import run, keep
from collections import List
from testing import assert_almost_equal

alias PI = 3.141592653589793
alias SOLAR_MASS = 4 * PI * PI
alias DAYS_PER_YEAR = 365.24
alias DELTA_T = 0.01



@value
struct Planet:
    var pos: SIMD[DType.float64, 4]
    var velocity: SIMD[DType.float64, 4]
    var mass: Float64

    fn __init__(
        inout self,
        pos: SIMD[DType.float64, 4],
        velocity: SIMD[DType.float64, 4],
        mass: Float64,
    ):
        self.pos = pos
        self.velocity = velocity
        self.mass = mass

alias Sun = Planet(
    0,
    0,
    SOLAR_MASS,
)


alias Jupiter = Planet(
    SIMD[DType.float64, 4](
        4.84143144246472090e00,
        -1.16032004402742839e00,
        -1.03622044471123109e-01,
        0,
    ),
    SIMD[DType.float64, 4](
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
        0,
    ),
    9.54791938424326609e-04 * SOLAR_MASS,
)

alias Saturn = Planet(
    SIMD[DType.float64, 4](
        8.34336671824457987e00,
        4.12479856412430479e00,
        -4.03523417114321381e-01,
        0,
    ),
    SIMD[DType.float64, 4](
        -2.76742510726862411e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
        0,
    ),
    2.85885980666130812e-04 * SOLAR_MASS,
)

alias Uranus = Planet(
    SIMD[DType.float64, 4](
        1.28943695621391310e01,
        -1.51111514016986312e01,
        -2.23307578892655734e-01,
        0,
    ),
    SIMD[DType.float64, 4](
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
        0,
    ),
    4.36624404335156298e-05 * SOLAR_MASS,
)

alias Neptune = Planet(
    SIMD[DType.float64, 4](
        1.53796971148509165e01,
        -2.59193146099879641e01,
        1.79258772950371181e-01,
        0,
    ),
    SIMD[DType.float64, 4](
        2.68067772490389322e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
        0,
    ),
    5.15138902046611451e-05 * SOLAR_MASS,
)

alias INITIAL_SYSTEM = List[Planet](Sun, Jupiter, Saturn, Uranus, Neptune)


fn offset_momentum(inout bodies: List[Planet]):
    var p = SIMD[DType.float64, 4]()

    for body in bodies:
        p += body[].velocity * body[].mass

    var body = bodies[0]
    body.velocity = -p / SOLAR_MASS

    bodies[0] = body

fn advance(inout bodies: List[Planet], dt: Float64):
    for i in range(len(INITIAL_SYSTEM)):
        for j in range(i+1, len(INITIAL_SYSTEM)):
            var body_i = bodies[i]
            var body_j = bodies[j]
            var diff = body_i.pos - body_j.pos
            var diff_sqr = (diff * diff).reduce_add()
            var mag = dt / (diff_sqr * sqrt(diff_sqr))

            body_i.velocity -= diff * body_j.mass * mag
            body_j.velocity += diff * body_i.mass * mag

            bodies[i] = body_i
            bodies[j] = body_j

    for body in bodies:
        body[].pos += dt * body[].velocity


fn energy(bodies: List[Planet]) -> Float64:
    var e: Float64 = 0

    for i in range(len(INITIAL_SYSTEM)):
        var body_i = bodies[i]
        e += (
            0.5
            * body_i.mass
            * (body_i.velocity * body_i.velocity).reduce_add()
        )
        for j in range(i+i, len(INITIAL_SYSTEM)):
            var body_j = bodies[j]
            var diff = body_i.pos - body_j.pos
            var distance = sqrt((diff * diff).reduce_add())
            e -= (body_i.mass * body_j.mass) / distance

    return e


def benchmark():
    fn benchmark_fn():
        var system = INITIAL_SYSTEM
        offset_momentum(system)
        keep(energy(system))

        for _ in range(10_000_000):
            advance(system, 0.01)

        keep(energy(system))

    run[benchmark_fn](max_runtime_secs=0.5).print()

fn simulate(inout bodies: List[Planet], steps: Int) raises:
    offset_momentum(bodies)

    var initial_energy = energy(bodies)

    for _ in range(steps):
        advance(bodies, DELTA_T)

    var final_energy = energy(bodies)

    assert_almost_equal(initial_energy, final_energy, atol=0.01)

def main():
    var system = INITIAL_SYSTEM
    simulate(system, 100000000000)