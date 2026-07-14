from collections.abc import Callable
from typing import Any

from lark import Transformer
import numpy as np


TraceCallback = Callable[[str], None]
KeepChoiceHandler = Callable[[np.ndarray, int], np.ndarray]


def truncate(string: str, length: int) -> str:
    if len(string) > length:
        return string[:length] + " ..."
    return string


class Evaluator(Transformer):
    def __init__(
        self,
        *,
        trace: TraceCallback | None = None,
        keep_choice_handler: KeepChoiceHandler | None = None,
    ) -> None:
        super().__init__()
        self.variable_declarations: dict[Any, float] = {}
        self._trace = trace
        self._keep_choice_handler = keep_choice_handler

    @property
    def trace(self) -> TraceCallback | None:
        return self._trace

    @trace.setter
    def trace(self, callback: TraceCallback | None) -> None:
        self._trace = callback

    @property
    def keep_choice_handler(self) -> KeepChoiceHandler | None:
        return self._keep_choice_handler

    @keep_choice_handler.setter
    def keep_choice_handler(self, handler: KeepChoiceHandler | None) -> None:
        self._keep_choice_handler = handler

    def _emit(self, message: str) -> None:
        if self._trace is not None:
            self._trace(message)

    def variable_declaration(self, arguments):
        name, value = arguments

        if name in self.variable_declarations:
            self._emit(
                f"Redeclaring variable {name} from {self.variable_declarations[name]} to {value}"
            )
        else:
            self._emit(f"Declaring variable {name} with value {value}")
        self.variable_declarations[name] = value
        return value

    def variable_search(self, arguments):
        (name,) = arguments
        if name not in self.variable_declarations:
            raise ValueError(f"Variable {name} is not defined")
        return self.variable_declarations[name]

    def dice_notation(self, arguments):
        (result,) = arguments
        return result

    def addition(self, arguments):
        left, right = arguments
        return left + right

    def subtraction(self, arguments):
        left, right = arguments
        return left - right

    def multiplication(self, arguments):
        left, right = arguments
        return left * right

    def divition(self, arguments):
        left, right = arguments
        return left / right

    def keep_highest(self, arguments):
        (value,) = arguments
        return "keep highest", int(value)

    def keep_lowest(self, arguments):
        (value,) = arguments
        return "keep lowest", int(value)

    def keep_choice(self, arguments):
        (value,) = arguments
        return "keep choice", int(value)

    def number(self, arguments):
        (value,) = arguments
        return float(value)

    def fudge(self, arguments):
        (quantity,) = arguments
        rolls = np.random.choice([-1, 0, 1], size=int(quantity))

        mapping_dictionary = {-1: "-", 0: " ", 1: "+"}

        self._emit(
            truncate(
                f"Rolling {int(quantity)} fudge dices: "
                f"{' '.join([f'[{mapping_dictionary[key]}]' for key in rolls])}",
                100,
            )
        )

        return rolls.sum()

    def dice(self, arguments):
        quantity, number_of_faces, *keep = arguments

        if quantity < sum([value for (_keyword, value) in keep]):
            raise ValueError(
                "The maximum amount of dice you can keep is the quantity of the throw"
            )

        rolls = np.random.choice(int(number_of_faces), size=int(quantity)) + 1

        self._emit(
            truncate(
                f"Rolling {int(quantity)} {int(number_of_faces)}-sided dices: "
                f"{[roll for roll in rolls]}",
                100,
            )
        )

        if keep:
            rolls_kept = np.array([])
            sorted_rolls_left = np.sort(rolls)
            for keep_key_word, amount in keep:
                if keep_key_word == "keep highest":
                    self._emit(
                        f"Keeping the {amount} highest dice: {sorted_rolls_left[-amount:]}"
                    )
                    rolls_kept = np.concatenate((rolls_kept, sorted_rolls_left[-amount:]))
                    sorted_rolls_left = sorted_rolls_left[:-amount]
                if keep_key_word == "keep lowest":
                    self._emit(
                        f"Keeping the {amount} lowest dice: {sorted_rolls_left[:amount]}"
                    )
                    rolls_kept = np.concatenate((rolls_kept, sorted_rolls_left[:amount]))
                    sorted_rolls_left = sorted_rolls_left[amount:]
                if keep_key_word == "keep choice":
                    choices_array = self._input_keep_choice_handler(
                        sorted_rolls_left, amount
                    )
                    for choice in choices_array:
                        if choice not in sorted_rolls_left:
                            raise ValueError(f"The value '{choice}' is not available")
                        index = np.where(sorted_rolls_left == choice)[0][0]
                        sorted_rolls_left = np.delete(sorted_rolls_left, index)

                    rolls_kept = np.concatenate((rolls_kept, choices_array))

            return rolls_kept.sum()

        return rolls.sum()

    def expected_value(self, _arguments):
        raise NotImplementedError("Expected value notation is not implemented")

    def _input_keep_choice_handler(self, sorted_rolls_left, amount):
        if self._keep_choice_handler is None:
            raise ValueError("keep choice notation requires a keep_choice_handler")
        return self._keep_choice_handler(sorted_rolls_left, amount)
