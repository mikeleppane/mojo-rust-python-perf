//! Computes digits of pi with the Chudnovsky algorithm using binary splitting,
//! backed by GMP/MPFR arbitrary-precision arithmetic via the `rug` crate.

use std::time::Instant;

use color_eyre::eyre::{Report, Result};
use rug::{Float, Integer, ops::Pow};

/// Binary-splitting recursion for the Chudnovsky series over the interval
/// `[a, b)`, returning the `(P, Q, R)` triple.
#[expect(
    clippy::many_single_char_names,
    reason = "P, Q, R are the canonical Chudnovsky binary-splitting variables"
)]
fn binary_split(a: u32, b: u32) -> (Integer, Integer, Integer) {
    if b - a != 1 {
        let m = a.midpoint(b);
        let (pam, qam, ram) = binary_split(a, m);
        let (pmb, qmb, rmb) = binary_split(m, b);
        let p = Integer::from(&pam * &pmb);
        let q = Integer::from(&qam * &qmb);
        let r = Integer::from(&ram * &qmb) + Integer::from(&pam * &rmb);
        return (p, q, r);
    }

    if a == 0 {
        return (
            Integer::from(1),
            Integer::from(1),
            Integer::from(13_591_409),
        );
    }

    let a_big = Integer::from(a);
    let pab: Integer = (Integer::from(6 * &a_big) - 5)
        * (Integer::from(2 * &a_big) - 1)
        * (Integer::from(6 * &a_big) - 1);
    let qab = a_big.clone().pow(3) * 10_939_058_860_032_000_u64;
    let rab = &pab * (13_591_409 + 545_140_134 * a_big);

    // The series alternates sign: R is negated for odd terms.
    if a % 2 == 0 {
        (pab, qab, rab)
    } else {
        (pab, qab, -rab)
    }
}

/// Computes `digits` decimal digits of pi.
///
/// # Errors
///
/// Returns an error if `digits` is so large that the required precision would
/// overflow a `u32` (i.e. `digits >= (2^32 - 1) / 4`).
pub fn chudnovsky(digits: u32) -> Result<Float> {
    match digits {
        0 => return Ok(Float::with_val(53, 3)),
        1 => return Ok(Float::with_val(53, 3.1)),
        _ => {}
    }

    let Some(used_precision) = digits.checked_mul(4) else {
        return Err(Report::msg(
            "invalid digit count: 4 * digits overflows u32 (max is (2^32 - 1) / 4)",
        ));
    };

    let digits_per_term = f64::log10(10_939_058_860_032_000_f64 / 6.0 / 2.0 / 6.0);
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "n is a small positive term count that always fits in u32"
    )]
    let n = (f64::from(digits) / digits_per_term).ceil() as u32;

    let (_, q1n, r1n) = binary_split(0, n);
    let numerator = Float::with_val(used_precision, 10_005).sqrt() * 426_880 * q1n;
    Ok(numerator / r1n)
}

/// Computes `digits` digits of pi and returns the wall-clock time of the
/// computation in milliseconds together with the result.
///
/// # Errors
///
/// Propagates any error from [`chudnovsky`].
pub fn run(digits: u32) -> Result<(f64, Float)> {
    let start = Instant::now();
    let pi = chudnovsky(digits)?;
    let elapsed_ms = start.elapsed().as_secs_f64() * 1e3;
    Ok((elapsed_ms, pi))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn computes_known_pi_prefix() {
        let pi = chudnovsky(20).expect("20 digits is valid");
        let s = pi.to_string_radix(10, Some(15));
        assert!(s.starts_with("3.14159265358979"), "got {s}");
    }

    #[test]
    fn small_cases() {
        assert!((chudnovsky(0).unwrap().to_f64() - 3.0).abs() < 1e-12);
        assert!((chudnovsky(1).unwrap().to_f64() - 3.1).abs() < 1e-12);
    }
}
