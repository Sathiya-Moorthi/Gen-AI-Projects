"""Unit tests for the Calculator MCP Server."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculator_server import (
    add,
    subtract,
    multiply,
    divide,
    power,
    modulo,
    square_root,
    absolute,
    percentage,
)


class TestAddition:
    """Tests for the add function."""

    def test_add_positive_numbers(self):
        assert add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert add(-2, -3) == -5

    def test_add_mixed_numbers(self):
        assert add(-2, 5) == 3

    def test_add_floats(self):
        assert add(2.5, 3.5) == 6.0

    def test_add_zero(self):
        assert add(5, 0) == 5


class TestSubtraction:
    """Tests for the subtract function."""

    def test_subtract_positive_numbers(self):
        assert subtract(10, 4) == 6

    def test_subtract_negative_result(self):
        assert subtract(4, 10) == -6

    def test_subtract_floats(self):
        assert subtract(5.5, 2.5) == 3.0


class TestMultiplication:
    """Tests for the multiply function."""

    def test_multiply_positive_numbers(self):
        assert multiply(6, 7) == 42

    def test_multiply_by_zero(self):
        assert multiply(100, 0) == 0

    def test_multiply_negative_numbers(self):
        assert multiply(-3, -4) == 12

    def test_multiply_mixed_signs(self):
        assert multiply(-3, 4) == -12


class TestDivision:
    """Tests for the divide function."""

    def test_divide_exact(self):
        assert divide(15, 3) == 5.0

    def test_divide_with_remainder(self):
        assert divide(10, 4) == 2.5

    def test_divide_negative(self):
        assert divide(-10, 2) == -5.0

    def test_divide_by_zero_raises_error(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)


class TestPower:
    """Tests for the power function."""

    def test_power_positive_exponent(self):
        assert power(2, 3) == 8.0

    def test_power_zero_exponent(self):
        assert power(5, 0) == 1.0

    def test_power_negative_exponent(self):
        assert power(2, -1) == 0.5

    def test_power_fractional_exponent(self):
        assert power(4, 0.5) == 2.0


class TestModulo:
    """Tests for the modulo function."""

    def test_modulo_basic(self):
        assert modulo(17, 5) == 2

    def test_modulo_exact_division(self):
        assert modulo(10, 5) == 0

    def test_modulo_by_zero_raises_error(self):
        with pytest.raises(ValueError, match="Cannot perform modulo with zero divisor"):
            modulo(10, 0)


class TestSquareRoot:
    """Tests for the square_root function."""

    def test_square_root_perfect_square(self):
        assert square_root(16) == 4.0

    def test_square_root_non_perfect(self):
        assert abs(square_root(2) - 1.4142135623730951) < 1e-10

    def test_square_root_zero(self):
        assert square_root(0) == 0.0

    def test_square_root_negative_raises_error(self):
        with pytest.raises(ValueError, match="Cannot calculate square root of a negative number"):
            square_root(-4)


class TestAbsolute:
    """Tests for the absolute function."""

    def test_absolute_negative(self):
        assert absolute(-5) == 5

    def test_absolute_positive(self):
        assert absolute(5) == 5

    def test_absolute_zero(self):
        assert absolute(0) == 0


class TestPercentage:
    """Tests for the percentage function."""

    def test_percentage_basic(self):
        assert percentage(200, 15) == 30.0

    def test_percentage_hundred(self):
        assert percentage(50, 100) == 50.0

    def test_percentage_zero(self):
        assert percentage(100, 0) == 0.0
