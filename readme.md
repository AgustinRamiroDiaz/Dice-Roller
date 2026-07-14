# A parser and evaluator for the dice notation grammar


## Prerequisites
- Python 3.11+
- uv


## Installation
- Clone the repo
- Go into the folder
- Execute from the command line: `uv sync`

## Library usage
```python
from dice_roller import Evaluator, evaluate, parse, parser, simulate

result = simulate("2d6 + 3")
tree = parse("4d6kh3")
value = Evaluator().transform(tree)
```

## Execution
- Go into the folder
- Execute from the command line: `uv run dice-roller`


## Useful resources:
- [Dice notation on Wikipedia](https://en.wikipedia.org/wiki/Dice_notation)
- [Lark's documentation](https://lark-parser.readthedocs.io/en/latest/index.html). This tool is used for the lexer and parser to generate an AST (_Abstract Sintax Tree_) from a given grammar
- A related [youtube tutorial](https://www.youtube.com/watch?v=Eythq9848Fg&t=500s)
- A similar [open source project](https://github.com/Bernardo-MG/dice-notation-python)
