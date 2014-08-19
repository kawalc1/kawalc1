import itertools
import string
import numpy as np

NUMBER_COUNT = 4
X_INDEX = 10


def get_possible_values(list_of_probs, threshold=.10):
    """ [[digit, confidence]] -> [[digit], confidence]
    Each item in the list that has a confidence of higher than the threshold is
    taken into account as a possibility. All possible lists of digits are
    constructed (taking one digit per outer list) and given a confidence by
    multiplying the confidences of its digits."""

    total_probs = []

    for probs in list_of_probs:
        high_probs = filter(lambda x: x[1] > threshold, enumerate(probs))

        print "high probs:"
        print high_probs

        if not total_probs:
            total_probs = map(lambda x: ([x[0]], x[1]), high_probs)
        else:
            new_total_probs = []

            for current_prob in total_probs:
                for high_prob in high_probs:
                    new_total_probs.append((current_prob[0] + [high_prob[0]],
                                            current_prob[1] * high_prob[1]))

            total_probs = new_total_probs

    return total_probs


def get_possible_end_results(list_of_probs):
    total_probs = []

    for probs in list_of_probs:
        if not total_probs:
            total_probs = map(lambda x: ([x[0]], x[1]), probs)
        else:
            new_total_probs = []

            for current_prob in total_probs:
                for high_prob in probs:
                    new_total_probs.append((current_prob[0] + [high_prob[0]],
                                            current_prob[1] * high_prob[1]))

            total_probs = new_total_probs

    return total_probs


def make_number(digit_list, current_confidence):
    """Takes a list of digits and turns it into a number with the provided
    confidence. Returns confidence 0 when there is an X in an incorrect
    location."""

    significant_part = list(
        itertools.dropwhile(lambda i: i == X_INDEX or i == 0, digit_list))

    if len(significant_part) == 0:
        return 0, current_confidence
    elif X_INDEX in significant_part:
        return 0, 0
    else:
        return int(
            string.join(map(str, significant_part), "")), current_confidence


def print_possible(after_reduction):
    outcomes = []
    for x in after_reduction:
        outcome = {
            "prabowo": int(x[0][0]),
            "jokowi": int(x[0][1]),
            "total": int(x[0][2]),
            "invalid": int(x[0][3]),
            "confidence": float(x[1])
        }
        print(outcome)
        outcomes.append(outcome)
    return outcomes


def get_possible_outcomes(all_squares, categories_count):
    all_numbers_matrix = all_squares.reshape(4, 3, categories_count)

    def matrix_to_number(number_matrix):
        possible_values = get_possible_values(number_matrix)
        return map(lambda x: make_number(x[0], x[1]), possible_values)

    all_numbers = map(matrix_to_number, all_numbers_matrix[0:NUMBER_COUNT])

    possibilities = get_possible_end_results(all_numbers)

    def reduce_probability_if_checksum_is_wrong(p):
        if p[0][0] + p[0][1] == p[0][2]:
            return p
        else:
            return p[0], p[1] * .005

    results = map(reduce_probability_if_checksum_is_wrong,
                  filter(lambda x: x[1] > 0, possibilities))

    results.sort(key=lambda x: -x[1])
    return print_possible(results[0:NUMBER_COUNT])


def read_json(data):
    rows = data["probabilities"]
    probability_matrix = np.ndarray(shape=(12, 10), dtype='f')

    for i, row in enumerate(rows):
        probability_matrix[i] = row

    return probability_matrix
