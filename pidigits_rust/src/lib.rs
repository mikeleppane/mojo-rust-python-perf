use color_eyre::eyre::{Report, Result};
use rug::{ops::Pow, Float, Integer};

fn binary_split(a: u32, b: u32) -> (Integer, Integer, Integer) {
    if b - a == 1 {
        if a == 0 {
            let pab = Integer::from(1);
            let qab = Integer::from(1);
            let rab = Integer::from(&pab * (13_591_409 + 545_140_134 * a));
            return (pab, qab, rab);
        }
        let a_bigint = Integer::from(a);
        let pab: Integer = (Integer::from(6 * &a_bigint) - 5)
            * (Integer::from(2 * &a_bigint) - 1)
            * (Integer::from(6 * &a_bigint) - 1);
        let qab = a_bigint.clone().pow(3) * 10_939_058_860_032_000u64;
        let rab = &pab * (13_591_409 + 545_140_134 * a_bigint);

        if a % 2 == 0 {
            return (pab, qab, rab);
        }
        return (pab, qab, -1 * rab);
    }
    let m = (a + b) / 2;
    let (pam, qam, ram) = binary_split(a, m);
    let (pmb, qmb, rmb) = binary_split(m, b);
    let p1n = Integer::from(&pam * &pmb);
    let q1n = Integer::from(&qam * &qmb);
    let r1n = Integer::from(&ram * &qmb) + Integer::from(&pam * &rmb);
    (p1n, q1n, r1n)
}

/// # Errors
///
/// Returns an error if the input is invalid.
#[allow(clippy::cast_possible_truncation)]
#[allow(clippy::cast_sign_loss)]
#[allow(clippy::cast_precision_loss)]
pub fn chudnovsky(digits: u32) -> Result<Float> {
    match digits {
        0 => return Ok(Float::with_val(53, 3)),
        1 => return Ok(Float::with_val(53, 3.1)),
        _ => {
            if digits.checked_mul(4).is_none() {
                return Err(Report::msg(
                    "Invalid digits: value must be between 0 <= x < (2^32-1)/4",
                ));
            }
        }
    }
    let used_precision = digits * 4;
    let digits_per_term = f32::log10(10_939_058_860_032_000_f32 / 6f32 / 2f32 / 6f32);
    let n = (digits as f32 / digits_per_term).ceil() as u32;
    let i1 = Integer::from(426_880);
    let i2 = Float::with_val(used_precision, 10_005);

    let (_, q1n, r1n) = binary_split(0, n);
    Ok((i1 * i2.sqrt() * q1n) / r1n)
}
