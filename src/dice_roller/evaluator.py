from collections.abc import Callable
from typing import Any

from lark import Transformer
import numpy as np
import numpy.typing as npt


DiceRolls = npt.NDArray[Any]
TraceCallback = Callable[[str], None]
KeepChoiceHandler = Callable[[DiceRolls, int], DiceRolls]
KeepModifier = tuple[str, int]
TransformResult = float | KeepModifier
type DiceArguments = tuple[float, float, *tuple[KeepModifier, ...]]


def format_rolls(rolls: DiceRolls) -> list[Any]:
    return [roll.item() for roll in rolls]


class Evaluator(Transformer[Any, float]):
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

    def variable_declaration(self, arguments: list[Any]) -> float:
        name, value = arguments

        if name in self.variable_declarations:
            self._emit(
                f"Redeclaring variable {name} from {self.variable_declarations[name]} to {value}"
            )
        else:
            self._emit(f"Declaring variable {name} with value {value}")
        numeric_value = float(value)
        self.variable_declarations[name] = numeric_value
        return numeric_value

    def variable_search(self, arguments: list[Any]) -> float:
        (name,) = arguments
        if name not in self.variable_declarations:
            raise ValueError(f"Variable {name} is not defined")
        return self.variable_declarations[name]

    def dice_notation(self, arguments: list[TransformResult]) -> TransformResult:
        (result,) = arguments
        return result

    def addition(self, arguments: list[float]) -> float:
        left, right = arguments
        return left + right

    def subtraction(self, arguments: list[float]) -> float:
        left, right = arguments
        return left - right

    def multiplication(self, arguments: list[float]) -> float:
        left, right = arguments
        return left * right

    def divition(self, arguments: list[float]) -> float:
        left, right = arguments
        return left / right

    def keep_highest(self, arguments: list[float]) -> KeepModifier:
        (value,) = arguments
        return "keep highest", int(value)

    def keep_lowest(self, arguments: list[float]) -> KeepModifier:
        (value,) = arguments
        return "keep lowest", int(value)

    def keep_choice(self, arguments: list[float]) -> KeepModifier:
        (value,) = arguments
        return "keep choice", int(value)

    def number(self, arguments: list[str]) -> float:
        (value,) = arguments
        return float(value)

    def fudge(self, arguments: list[float]) -> float:
        (quantity,) = arguments
        rolls = np.random.choice([-1, 0, 1], size=int(quantity))

        mapping_dictionary = {-1: "-", 0: " ", 1: "+"}

        self._emit(
            f"Rolling {int(quantity)} fudge dices: "
            f"{' '.join([f'[{mapping_dictionary[key]}]' for key in rolls])}"
        )

        return float(rolls.sum())

    def dice(self, arguments: DiceArguments) -> float:
        quantity, number_of_faces, *keep = arguments

        if quantity < sum(value for (_keyword, value) in keep):
            raise ValueError(
                "The maximum amount of dice you can keep is the quantity of the throw"
            )

        rolls = np.random.choice(int(number_of_faces), size=int(quantity)) + 1

        self._emit(
            f"Rolling {int(quantity)} {int(number_of_faces)}-sided dices: "
            f"{format_rolls(rolls)}"
        )

        if keep:
            rolls_kept = np.array([])
            sorted_rolls_left = np.sort(rolls)
            for keep_key_word, amount in keep:
                if keep_key_word == "keep highest":
                    self._emit(
                        f"Keeping the {amount} highest dice: "
                        f"{format_rolls(sorted_rolls_left[-amount:])}"
                    )
                    rolls_kept = np.concatenate((rolls_kept, sorted_rolls_left[-amount:]))
                    sorted_rolls_left = sorted_rolls_left[:-amount]
                if keep_key_word == "keep lowest":
                    self._emit(
                        f"Keeping the {amount} lowest dice: "
                        f"{format_rolls(sorted_rolls_left[:amount])}"
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

            return float(rolls_kept.sum())

        return float(rolls.sum())

    def expected_value(self, _arguments: list[Any]) -> None:
        raise NotImplementedError("Expected value notation is not implemented")

    def _input_keep_choice_handler(
        self, sorted_rolls_left: DiceRolls, amount: int
    ) -> DiceRolls:
        if self._keep_choice_handler is None:
            raise ValueError("keep choice notation requires a keep_choice_handler")
        return self._keep_choice_handler(sorted_rolls_left, amount)
