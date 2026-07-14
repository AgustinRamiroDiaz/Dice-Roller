from .evaluator import Evaluator
from .parser import parse


def evaluate(notation: str, *, evaluator: Evaluator | None = None):
    active_evaluator = evaluator or Evaluator()
    return active_evaluator.transform(parse(notation))


def simulate(notation: str):
    return evaluate(notation)
