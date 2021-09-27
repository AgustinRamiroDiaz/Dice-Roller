# %%
from lark import Lark
from evaluator import evaluator

with open("grammar.lark", "r") as file:
    grammar = "\n".join(file.readlines())

parser = Lark(grammar, parser='lalr',
              start='dice_notation', transformer=evaluator)

# %%

while True:
    text = input()
    print(parser.parse(text))

# %%
