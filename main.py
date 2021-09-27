# %%
from lark import Lark
from evaluator import evaluator

with open("grammar.lark", "r") as file:
    grammar = "\n".join(file.readlines())

parser = Lark(grammar, start='dice_notation')

# %%

while True:
    text = input("Type in an expression in dice notation: \n")
    
    try:
        tree = parser.parse(text)
        print(f"Result: {evaluator.transform(tree)}")
    except:
        print("Can't parse expression")

