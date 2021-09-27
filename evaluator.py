from lark import Transformer
import numpy as np


def truncate(string, length):
    if len(string) > length:
        return string[:length] + ' ...'
    return string


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
        # TODO: Extrapolate to negative and floating point numbers
        rolls = np.random.choice([-1, 0, 1], size=int(quantity))

        mapping_dictionary = {-1: "-", 0: " ", 1: "+"}

        print(truncate(
            f"# Rolling {int(quantity)} fudge dices: {' + '.join(str([mapping_dictionary[key]]) for key in rolls)}", 100))

        return rolls.sum()

    def dice(self, arguments):
        quantity, number_of_faces, *keep = arguments

        if quantity < sum([value for (k, value) in keep]):
            raise ValueError(
                "The maximum amount of dice you can keep is the quantity of the throw")

        # TODO: Extrapolate to negative and floating point numbers
        rolls = np.random.choice(int(number_of_faces), size=int(quantity)) + 1

        print(truncate(
            f"# Rolling {int(quantity)} {int(number_of_faces)}-sided dices: {' + '.join([str(roll) for roll in rolls])}", 100))

        if keep:
            rolls_kept = np.array([])
            sorted_rolls_left = np.sort(rolls)
            for keep_key_word, amount in keep:
                if keep_key_word == "keep highest":
                    print(
                        f"Keeping the {amount} highest dice: {sorted_rolls_left[-amount:]}")
                    rolls_kept = np.concatenate(
                        (rolls_kept, sorted_rolls_left[-amount:]))
                    sorted_rolls_left = sorted_rolls_left[:-amount]
                if keep_key_word == "keep lowest":
                    print(
                        f"Keeping the {amount} lowest dice: {sorted_rolls_left[:amount]}")
                    rolls_kept = np.concatenate(
                        (rolls_kept, sorted_rolls_left[:amount]))
                    sorted_rolls_left = sorted_rolls_left[amount:]
                if keep_key_word == "keep choice":
                    choices = input(
                        f"Choose the values you would like to keep from {list(sorted_rolls_left)} (write them separated by spaces): ")
                    choices_array = np.array([int(choice) for choice in choices.split()])
                    for choice in choices_array:
                        if choice not in sorted_rolls_left:
                            raise ValueError(
                                f"The value '{choice}' is not avaiable")
                        index = np.where(sorted_rolls_left == choice)[0][0]
                        sorted_rolls_left = np.delete(sorted_rolls_left, index)

                    rolls_kept = np.concatenate((rolls_kept, choices_array))

            return rolls_kept.sum()

        return rolls.sum()

    def keep_highest(self, arguments):
        (value,) = arguments
        return "keep highest", int(value)

    def keep_lowest(self, arguments):
        (value,) = arguments
        return "keep lowest", int(value)

    def keep_choice(self, arguments):
        (value,) = arguments
        return "keep choice", int(value)

    def number(self, arguments):
        (value,) = arguments
        return float(value)


evaluator = Evaluator()
