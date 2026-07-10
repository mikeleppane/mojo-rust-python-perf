"""Correctness tests for the pidigits implementation."""

import pytest

from benchmarking.algorithms import pidigits

# First 50 significant digits of pi, without the decimal point.
PI_STREAM = "31415926535897932384626433832795028841971693993751"


def test_small_cases() -> None:
    assert pidigits.chudnovsky(0) == 3
    assert str(pidigits.chudnovsky(1)) == "3.1"


@pytest.mark.parametrize("digits", [10, 50, 100, 500])
def test_prefix_matches_reference(digits: int) -> None:
    result = str(pidigits.chudnovsky(digits)).replace(".", "")
    # The final significant digit may be rounded, so compare with one guard digit.
    guard = min(digits - 1, len(PI_STREAM))
    assert result[:guard] == PI_STREAM[:guard]


def test_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="invalid digits"):
        pidigits.chudnovsky(pidigits.MAX_DIGITS + 1)
