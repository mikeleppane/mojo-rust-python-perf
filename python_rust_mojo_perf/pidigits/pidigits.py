import math
import sys
import time
from decimal import Decimal, getcontext
from typing import TypeAlias

import click

sys.set_int_max_str_digits(10000000)

MAX_DIGITS = 1073741823

BINARY_SPLIT_RES: TypeAlias = tuple[int, int, int]


def binary_split(a: int, b: int) -> BINARY_SPLIT_RES:
    if b - a == 1:
        if a == 0:
            pab = 1
            qab = 1
            rab = pab * (13591409 + 545140134 * a)
            return (pab, qab, rab)
        pab = (6 * a - 5) * (2 * a - 1) * (6 * a - 1)
        qab = a**3 * 10939058860032000
        rab = pab * (13591409 + 545140134 * a)
        if a % 2 == 0:
            return (pab, qab, rab)
        return (pab, qab, -1 * rab)
    m = (a + b) // 2
    (pam, qam, ram) = binary_split(a, m)
    (pmb, qmb, rmb) = binary_split(m, b)
    p1n = pam * pmb
    q1n = qam * qmb
    r1n = ram * qmb + pam * rmb
    return (p1n, q1n, r1n)


def chudnovsky(digits: int) -> str:
    if digits == 0:
        return "3"
    if digits == 1:
        return "3.1"
    if digits * 4 > MAX_DIGITS:
        raise ValueError("Invalid digits: value must be between 0 <= x < (2^32-1)/4")
    getcontext().prec = digits
    digits_per_term = math.log10(10939058860032000.0 / 6.0 / 2.0 / 6.0)
    n = math.ceil(digits / digits_per_term)
    i1 = 426880 * Decimal(10005).sqrt()

    (_, q1n, r1n) = binary_split(0, n)
    return str((i1 * q1n) / r1n)


def main(digits: int) -> None:
    print("Starting PIDIGITS calculation...")
    print(f"Calculating {digits} digits of pi")
    res = chudnovsky(digits)

    print(f"First {digits} digits of pi: {res}")


def benchmark(digits: int) -> None:
    print("Starting PIDIGITS benchmark...")
    print(f"Calculating {digits} digits of pi")

    t_start = time.perf_counter()

    chudnovsky(digits)

    t_end = time.perf_counter()

    print(f"Time taken: {(t_end - t_start) * 1000:.2f} ms")


@click.command()
@click.option("-d", "--digits", default=100, help="Number of digits to calculate")
@click.option("-b", "--bench", is_flag=True, help="Run the benchmark")
def cli(digits: int, bench: bool) -> None:
    if bench:
        benchmark(digits)
    else:
        main(digits=digits)


if __name__ == "__main__":
    cli()
