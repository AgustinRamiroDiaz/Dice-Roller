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

## Library usage
```python
from dice_roller import Evaluator, evaluate, parse, parser, simulate

result = simulate("2d6 + 3")
tree = parse("4d6kh3")
value = Evaluator().transform(tree)
```

To trace evaluation steps or handle keep-choice notation, pass callbacks to
`Evaluator`:

```python
import numpy as np

from dice_roller import Evaluator, KeepChoiceHandler, TraceCallback, evaluate


def trace(message: str) -> None:
    print(message)


def keep_choice_handler(sorted_rolls_left: np.ndarray, amount: int) -> np.ndarray:
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
