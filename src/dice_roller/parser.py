from importlib import resources

from lark import Lark

_GRAMMAR = resources.files(__package__).joinpath("grammar.lark").read_text()

parser = Lark(_GRAMMAR, start="dice_notation")


def parse(notation: str):
    return parser.parse(notation)
