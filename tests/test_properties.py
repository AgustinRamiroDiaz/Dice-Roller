from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

from hypothesis import given
from hypothesis import strategies as st
import numpy as np

from dice_roller import evaluate, parse


small_numbers = st.integers(min_value=0, max_value=1_000)
positive_numbers = st.integers(min_value=1, max_value=1_000)
dice_quantities = st.integers(min_value=1, max_value=20)
dice_faces = st.integers(min_value=1, max_value=100)


@given(value=small_numbers)
def test_number_literals_evaluate_to_their_float_value(value: int) -> None:
    assert evaluate(str(value)) == float(value)


@given(left=small_numbers, right=small_numbers)
def test_addition_matches_python_arithmetic(left: int, right: int) -> None:
    assert evaluate(f"{left} + {right}") == float(left + right)


@given(left=small_numbers, right=small_numbers)
def test_subtraction_matches_python_arithmetic(left: int, right: int) -> None:
    assert evaluate(f"{left} - {right}") == float(left - right)


@given(left=small_numbers, right=small_numbers)
def test_multiplication_matches_python_arithmetic(left: int, right: int) -> None:
    assert evaluate(f"{left} * {right}") == float(left * right)


@given(left=small_numbers, right=positive_numbers)
def test_division_matches_python_arithmetic(left: int, right: int) -> None:
    assert evaluate(f"{left} / {right}") == left / right


@given(quantity=dice_quantities, faces=dice_faces)
def test_dice_rolls_stay_within_possible_bounds(quantity: int, faces: int) -> None:
    result = evaluate(f"{quantity}d{faces}")

    assert quantity <= result <= quantity * faces


@contextmanager
def _use_predictable_rolls() -> Iterator[None]:
    def choice(options: Any, *, size: int) -> np.ndarray[Any, np.dtype[np.int_]]:
        if isinstance(options, int):
            return np.arange(size) % options
        return np.resize(np.asarray(options), size)

    with patch("numpy.random.choice", choice):
        yield


@given(quantity=dice_quantities, faces=dice_faces, keep=st.data())
def test_keep_highest_sums_the_largest_rolls(
    quantity: int, faces: int, keep: st.DataObject
) -> None:
    with _use_predictable_rolls():
        amount = keep.draw(st.integers(min_value=1, max_value=quantity))
        rolls = (np.arange(quantity) % faces) + 1

        assert evaluate(f"{quantity}d{faces}kh{amount}") == float(
            np.sort(rolls)[-amount:].sum()
        )


@given(quantity=dice_quantities, faces=dice_faces, keep=st.data())
def test_keep_lowest_sums_the_smallest_rolls(
    quantity: int, faces: int, keep: st.DataObject
) -> None:
    with _use_predictable_rolls():
        amount = keep.draw(st.integers(min_value=1, max_value=quantity))
        rolls = (np.arange(quantity) % faces) + 1

        assert evaluate(f"{quantity}d{faces}kl{amount}") == float(
            np.sort(rolls)[:amount].sum()
        )


@given(quantity=dice_quantities, faces=dice_faces)
def test_generated_dice_notation_is_parseable(quantity: int, faces: int) -> None:
    assert parse(f"{quantity}d{faces}") is not None
