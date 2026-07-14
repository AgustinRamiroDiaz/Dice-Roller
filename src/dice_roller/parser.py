from importlib import resources
from typing import Any

from lark import Lark, Tree

_GRAMMAR = resources.files(__package__).joinpath("grammar.lark").read_text()

parser = Lark(_GRAMMAR, start="dice_notation")


def parse(notation: str) -> Tree[Any]:
    return parser.parse(notation)
