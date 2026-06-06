"""Utility helpers for demo_pkg."""


def add(a: int, b: int) -> int:
    """Return the sum of two integers.

    Args:
        a: First operand.
        b: Second operand.

    Returns:
        The sum of *a* and *b*.
    """
    return a + b


def is_even(n: int) -> bool:
    """Check whether an integer is even.

    Args:
        n: The integer to check.

    Returns:
        True if *n* is even, False otherwise.
    """
    return n % 2 == 0


def reverse_string(s: str) -> str:
    """Return the reversed copy of a string.

    Args:
        s: The string to reverse.

    Returns:
        The reversed string.
    """
    return s[::-1]


if __name__ == "__main__":
    print(add(2, 3))
    print(is_even(4))
    print(reverse_string("hello"))
