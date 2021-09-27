# %%
from os import error
from lark import Lark
from evaluator import evaluator
from colorama import Fore


with open("grammar.lark", "r") as file:
    grammar = "\n".join(file.readlines())

parser = Lark(grammar, start='dice_notation')

# %%

while True:
    text = input(Fore.LIGHTYELLOW_EX + "Type in an expression in dice notation: \n" + Fore.RESET)

    try:
        tree = parser.parse(text)
        print(Fore.LIGHTMAGENTA_EX + f"🎲 {evaluator.transform(tree)} 🎲")
    except Exception as error:
        print(Fore.RED + "Can't parse expression: " + str(error))

