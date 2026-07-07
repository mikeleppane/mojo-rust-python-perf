"""Compute digits of pi with the Chudnovsky algorithm and binary splitting."""

import math
import sys
from decimal import Decimal, getcontext
from time import perf_counter

# Chudnovsky produces very large integers; allow their decimal repr.
sys.set_int_max_str_digits(1_000_000_000)

MAX_DIGITS = 1073741823  # (2**32 - 1) // 4


def binary_split(a: int, b: int) -> tuple[int, int, int]:
    """Binary-splitting recursion over ``[a, b)``, returning the ``(P, Q, R)`` triple."""
    if b - a == 1:
        if a == 0:
            return (1, 1, 13591409)
        pab = (6 * a - 5) * (2 * a - 1) * (6 * a - 1)
        qab = a**3 * 10939058860032000
        rab = pab * (13591409 + 545140134 * a)
        # The series alternates sign: R is negated for odd terms.
        return (pab, qab, rab) if a % 2 == 0 else (pab, qab, -rab)
    m = (a + b) // 2
    pam, qam, ram = binary_split(a, m)
    pmb, qmb, rmb = binary_split(m, b)
    return (pam * pmb, qam * qmb, ram * qmb + pam * rmb)


def chudnovsky(digits: int) -> Decimal:
    """Computes ``digits`` decimal digits of pi as a :class:`~decimal.Decimal`."""
    if digits == 0:
        return Decimal(3)
    if digits == 1:
        return Decimal("3.1")
    if digits > MAX_DIGITS:
        raise ValueError("invalid digits: value must satisfy 0 <= digits < (2**32 - 1) / 4")

    getcontext().prec = digits
    digits_per_term = math.log10(10939058860032000.0 / 6.0 / 2.0 / 6.0)
    n = math.ceil(digits / digits_per_term)
    numerator = 426880 * Decimal(10005).sqrt()

    _, q1n, r1n = binary_split(0, n)
    return (numerator * q1n) / r1n


def run(digits: int) -> tuple[float, str]:
    """Computes ``digits`` digits of pi.

    Returns the wall-clock time of the computation in milliseconds and the
    result as a string. Only the numeric computation is timed; converting the
    result to a string is excluded so the number matches the Rust implementation.
    """
    start = perf_counter()
    pi = chudnovsky(digits)
    elapsed_ms = (perf_counter() - start) * 1e3
    return elapsed_ms, str(pi)
