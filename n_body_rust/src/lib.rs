//! N-body simulation of the outer solar system (the classic
//! Computer Language Benchmarks Game problem: Sun + four gas giants).

use smallvec::{SmallVec, smallvec};
use std::time::Instant;

const SOLAR_MASS: f64 = 4.0 * std::f64::consts::PI * std::f64::consts::PI;
const DAYS_PER_YEAR: f64 = 365.24;
const DELTA_T: f64 = 0.01;
const ENERGY_DIFF_THRESHOLD: f64 = 1e-4;

/// A body in the simulation: 3-D position, velocity and its mass.
pub struct Planet {
    pos: [f64; 3],
    vel: [f64; 3],
    mass: f64,
}

/// Builds the canonical five-body system (Sun, Jupiter, Saturn, Uranus, Neptune).
#[must_use]
pub fn create_initial_system() -> SmallVec<[Planet; 5]> {
    smallvec![
        // Sun
        Planet {
            pos: [0.0, 0.0, 0.0],
            vel: [0.0, 0.0, 0.0],
            mass: SOLAR_MASS,
        },
        // Jupiter
        Planet {
            pos: [
                4.841_431_442_464_721,
                -1.160_320_044_027_428_4,
                -1.036_220_444_711_231_1e-1,
            ],
            vel: [
                1.660_076_642_744_037e-3 * DAYS_PER_YEAR,
                7.699_011_184_197_404e-3 * DAYS_PER_YEAR,
                -6.904_600_169_720_63e-5 * DAYS_PER_YEAR,
            ],
            mass: 9.547_919_384_243_266e-4 * SOLAR_MASS,
        },
        // Saturn
        Planet {
            pos: [
                8.343_366_718_244_58,
                4.124_798_564_124_305,
                -4.035_234_171_143_214e-1,
            ],
            vel: [
                -2.767_425_107_268_624e-3 * DAYS_PER_YEAR,
                4.998_528_012_349_172e-3 * DAYS_PER_YEAR,
                2.304_172_975_737_639_3e-5 * DAYS_PER_YEAR,
            ],
            mass: 2.858_859_806_661_308e-4 * SOLAR_MASS,
        },
        // Uranus
        Planet {
            pos: [
                1.289_436_956_213_913_1e1,
                -1.511_115_140_169_863_1e1,
                -2.233_075_788_926_557_3e-1,
            ],
            vel: [
                2.964_601_375_647_616e-3 * DAYS_PER_YEAR,
                2.378_471_739_594_809_5e-3 * DAYS_PER_YEAR,
                -2.965_895_685_402_375_6e-5 * DAYS_PER_YEAR,
            ],
            mass: 4.366_244_043_351_563e-5 * SOLAR_MASS,
        },
        // Neptune
        Planet {
            pos: [
                1.537_969_711_485_091_7e1,
                -2.591_931_460_998_796_4e1,
                1.792_587_729_503_711_8e-1,
            ],
            vel: [
                2.680_677_724_903_893_2e-3 * DAYS_PER_YEAR,
                1.628_241_700_382_423e-3 * DAYS_PER_YEAR,
                -9.515_922_545_197_159e-5 * DAYS_PER_YEAR,
            ],
            mass: 5.151_389_020_466_114_5e-5 * SOLAR_MASS,
        },
    ]
}

/// Cancels the total momentum of the system by adjusting the Sun's velocity, so
/// the centre of mass stays put.
pub fn offset_momentum(planets: &mut [Planet]) {
    let mut momentum = [0.0; 3];
    for planet in planets.iter() {
        for (m, v) in momentum.iter_mut().zip(planet.vel) {
            *m += v * planet.mass;
        }
    }
    for (v, m) in planets[0].vel.iter_mut().zip(momentum) {
        *v = -m / SOLAR_MASS;
    }
}

/// Advances every body by one `DELTA_T` step using pairwise gravitation.
#[inline]
pub fn advance(planets: &mut [Planet]) {
    for i in 0..planets.len() {
        for j in i + 1..planets.len() {
            let dx = planets[i].pos[0] - planets[j].pos[0];
            let dy = planets[i].pos[1] - planets[j].pos[1];
            let dz = planets[i].pos[2] - planets[j].pos[2];

            let d2 = dz.mul_add(dz, dx.mul_add(dx, dy * dy));
            let mag = DELTA_T / (d2 * d2.sqrt());

            // Fold each body's mass into `mag` once, so the per-component
            // updates share a single scalar (matching the Mojo version).
            let fi = planets[i].mass * mag;
            let fj = planets[j].mass * mag;
            planets[i].vel[0] -= dx * fj;
            planets[i].vel[1] -= dy * fj;
            planets[i].vel[2] -= dz * fj;
            planets[j].vel[0] += dx * fi;
            planets[j].vel[1] += dy * fi;
            planets[j].vel[2] += dz * fi;
        }
    }

    for planet in planets.iter_mut() {
        planet.pos[0] += DELTA_T * planet.vel[0];
        planet.pos[1] += DELTA_T * planet.vel[1];
        planet.pos[2] += DELTA_T * planet.vel[2];
    }
}

/// Total energy of the system (kinetic + gravitational potential).
#[must_use]
#[inline]
pub fn energy(planets: &[Planet]) -> f64 {
    let mut energy = 0.0;
    for i in 0..planets.len() {
        let v = planets[i].vel;
        energy += 0.5 * planets[i].mass * v[2].mul_add(v[2], v[1].mul_add(v[1], v[0] * v[0]));
        for j in i + 1..planets.len() {
            let dx = planets[i].pos[0] - planets[j].pos[0];
            let dy = planets[i].pos[1] - planets[j].pos[1];
            let dz = planets[i].pos[2] - planets[j].pos[2];
            let d2 = dz.mul_add(dz, dx.mul_add(dx, dy * dy));
            energy -= planets[i].mass * planets[j].mass / d2.sqrt();
        }
    }
    energy
}

/// Runs the simulation for `n_steps` and returns the wall-clock time of the
/// integration loop in milliseconds together with whether energy was conserved.
///
/// Only the advance loop is timed; system setup and energy checks are excluded
/// so the number is comparable across the Python and Mojo implementations.
#[must_use]
pub fn run(n_steps: usize) -> (f64, bool) {
    let mut planets = create_initial_system();
    offset_momentum(&mut planets);
    let initial_energy = energy(&planets);

    let start = Instant::now();
    for _ in 0..n_steps {
        advance(&mut planets);
    }
    let elapsed_ms = start.elapsed().as_secs_f64() * 1e3;

    let conserved = (energy(&planets) - initial_energy).abs() < ENERGY_DIFF_THRESHOLD;
    (elapsed_ms, conserved)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn energy_is_conserved() {
        let (_, conserved) = run(100_000);
        assert!(conserved, "energy drifted beyond the threshold");
    }

    #[test]
    fn initial_energy_matches_reference() {
        // Reference value from the Benchmarks Game n-body problem.
        let mut planets = create_initial_system();
        offset_momentum(&mut planets);
        assert!((energy(&planets) - (-0.169_075_164)).abs() < 1e-6);
    }
}
