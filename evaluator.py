from lark import Transformer
from numpy.random import choice


class Evaluator(Transformer):
    def dice_notation(self, arguments):
        (result,) = arguments
        return result

    def addition(self, arguments):
        left, right = arguments
        return left + right

    def subtraction(self, arguments):
        left, right = arguments
        return left - right

    def multiplication(self, arguments):
        left, right = arguments
        return left * right

    def divition(self, arguments):
        left, right = arguments
        return left / right

    def fudge(self, arguments):
        (quantity, ) = arguments
        rolls = choice([-1, 0, 1], size=quantity)

        mapping_dictionary = {-1: "-", 0: " ", 1: "+"}
        print(f"Rolling {int(quantity)} fudge dices: {' + '.join(str([mapping_dictionary[key]]) for key in rolls)}")

        return rolls.sum()

    def dice(self, arguments):
        quantity, number_of_faces = arguments
        # TODO: Extrapolate to negative and floating point numbers
        rolls = choice(int(number_of_faces), size=int(quantity)) + 1

        print(f"Rolling {int(quantity)} {int(number_of_faces)}-sided dices: {' + '.join([str(roll) for roll in rolls])}")

        return rolls.sum()

    def number(self, arguments):
        (value,) = arguments
        return float(value)


evaluator = Evaluator()
