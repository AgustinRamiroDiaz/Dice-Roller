# A parser and evaluator for the dice notation grammar


## Prerequisites
- Python 3.12+
- uv


## Installation
- Clone the repo
- Go into the folder
- Execute from the command line: `uv sync`

## Development
- Install the development dependencies: `uv sync --dev`
- Install the Git hooks: `uv run pre-commit install`
- Run all hooks manually: `uv run pre-commit run --all-files`
- Run the test suite: `uv run pytest`
- Run the type checker: `uv run mypy`

## Testing
The test suite uses `pytest` and `hypothesis` for property-based tests. The
properties currently cover arithmetic expressions, parseable dice notation,
dice roll bounds, and deterministic keep-highest / keep-lowest behavior.

For example, Hypothesis generates many valid dice expressions and checks that a
plain roll always stays inside its possible bounds:

```python
from hypothesis import given
from hypothesis import strategies as st

from dice_roller import evaluate


@given(
    quantity=st.integers(min_value=1, max_value=20),
    faces=st.integers(min_value=1, max_value=100),
)
def test_dice_rolls_stay_within_possible_bounds(quantity: int, faces: int) -> None:
    result = evaluate(f"{quantity}d{faces}")

    assert quantity <= result <= quantity * faces
```

## Library usage
```python
from dice_roller import Evaluator, evaluate, parse, parser, simulate

result = simulate("2d6 + 3")
tree = parse("4d6kh3")
value = Evaluator().transform(tree)
```

## Dice notation examples
Valid expressions include:

```text
1d20
2d6 + 3
(1d8 + 2) * 2
4d6kh3
4d6kl2
4d6kc2
3df
x = 1d20
x
```

- `NdM` rolls `N` dice with `M` faces, for example `2d6`.
- `khN` keeps the `N` highest dice.
- `klN` keeps the `N` lowest dice.
- `kcN` asks a `keep_choice_handler` callback which `N` dice to keep.
- `Ndf` rolls `N` fudge dice.
- Variables can be assigned with `name = expression` and reused later by the
  same `Evaluator` instance.

To trace evaluation steps or handle keep-choice notation, pass callbacks to
`Evaluator`:

```python
from dice_roller import DiceRolls, Evaluator, KeepChoiceHandler, TraceCallback, evaluate


def trace(message: str) -> None:
    print(message)


def keep_choice_handler(sorted_rolls_left: DiceRolls, amount: int) -> DiceRolls:
    return sorted_rolls_left[:amount]


trace_callback: TraceCallback = trace
choice_handler: KeepChoiceHandler = keep_choice_handler

evaluator = Evaluator(
    trace=trace_callback,
    keep_choice_handler=choice_handler,
)
value = evaluate("4d6kc2", evaluator=evaluator)

evaluator.trace = None
evaluator.keep_choice_handler = choice_handler
```

## Known limitations
Negative number literals are not handled correctly yet. For example, `-1` is
currently parsed as subtraction with a missing left-hand operand, so evaluating
`-1` or expressions such as `0 + -1` fails. Use subtraction from a positive or
zero value instead, for example `0 - 1`.

## Execution
- Go into the folder
- Install the CLI extra: `uv sync --extra cli`
- Execute from the command line: `uv run dice-roller`

## TUI
- Install the TUI extra: `uv sync --extra tui`
- Execute from the command line: `uv run dice-roller-tui`


## Useful resources:
- [Dice notation on Wikipedia](https://en.wikipedia.org/wiki/Dice_notation)
- [Lark's documentation](https://lark-parser.readthedocs.io/en/latest/index.html). This tool is used for the lexer and parser to generate an AST (_Abstract Sintax Tree_) from a given grammar
- A related [youtube tutorial](https://www.youtube.com/watch?v=Eythq9848Fg&t=500s)
- A similar [open source project](https://github.com/Bernardo-MG/dice-notation-python)
