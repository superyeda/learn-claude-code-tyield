"""Tests for demo_pkg.utils."""

import unittest

from demo_pkg.utils import add, is_even, reverse_string


# -- add ------------------------------------------------------------------

class TestAdd(unittest.TestCase):
    """Tests for :func:`add`."""

    def test_positive_numbers(self) -> None:
        self.assertEqual(add(2, 3), 5)

    def test_negative_numbers(self) -> None:
        self.assertEqual(add(-1, -2), -3)

    def test_zero(self) -> None:
        self.assertEqual(add(0, 0), 0)


# -- is_even --------------------------------------------------------------

class TestIsEven(unittest.TestCase):
    """Tests for :func:`is_even`."""

    def test_even(self) -> None:
        self.assertTrue(is_even(4))

    def test_odd(self) -> None:
        self.assertFalse(is_even(3))

    def test_zero_is_even(self) -> None:
        self.assertTrue(is_even(0))


# -- reverse_string -------------------------------------------------------

class TestReverseString(unittest.TestCase):
    """Tests for :func:`reverse_string`."""

    def test_normal_string(self) -> None:
        self.assertEqual(reverse_string("hello"), "olleh")

    def test_empty_string(self) -> None:
        self.assertEqual(reverse_string(""), "")

    def test_palindrome(self) -> None:
        self.assertEqual(reverse_string("racecar"), "racecar")


if __name__ == "__main__":
    unittest.main()
