import numpy as np

from .evaluator import DiceRolls, Evaluator
from .simulation import evaluate

try:
    from colorama import Fore
except ImportError as error:
    raise SystemExit(
        "The dice-roller CLI requires the optional 'cli' extra. "
        "Install it with: uv sync --extra cli"
    ) from error


def _trace(message: str) -> None:
    print(Fore.GREEN + message + Fore.RESET)


def _input_keep_choice_handler(sorted_rolls_left: DiceRolls, amount: int) -> DiceRolls:
    choices = input(
        Fore.YELLOW
        + f"Choose {amount} dices you would like to keep from {list(sorted_rolls_left)} "
        + "(write them separated by spaces): "
        + Fore.RESET
    )
    choices_array = np.array([int(choice) for choice in choices.split()])
    while len(choices_array) != amount:
        print(
            Fore.RED
            + f"Wrong amount of dice: your input amount was {len(choices_array)} "
            + f"but the expected was {amount}"
            + Fore.RESET
        )
        choices = input(
            Fore.YELLOW
            + f"Choose {amount} dices you would like to keep from {list(sorted_rolls_left)} "
            + "(write them separated by spaces): "
            + Fore.RESET
        )
        choices_array = np.array([int(choice) for choice in choices.split()])

    return choices_array


def main() -> None:
    evaluator = Evaluator(
        trace=_trace,
        keep_choice_handler=_input_keep_choice_handler,
    )

    while True:
        text = input(
            Fore.LIGHTYELLOW_EX
            + "Type in an expression in dice notation: \n"
            + Fore.RESET
        )

        try:
            print(
                Fore.LIGHTMAGENTA_EX
                + f"\n🎲 {evaluate(text, evaluator=evaluator)} 🎲"
                + Fore.RESET,
                end="\n\n",
            )
        except Exception as error:
            print(Fore.RED + "Can't parse expression: " + str(error) + Fore.RESET)
