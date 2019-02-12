import itertools
import string
import numpy as np

NUMBER_COUNT = 4
DIGITS_PER_NUMBER = 3
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
        return int("".join(str(x) for x in significant_part)), current_confidence


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


def get_number_config_for_index(config, prob_index):
    for number in config["numbers"]:
        number_index = number["id"]
        if prob_index["id"] == number_index:
            return number
    return None


def print_outcome(config, outcome_matrix, all_probabilities):
    outcomes = []
    print(outcome_matrix)
    for outcome in outcome_matrix:
        numbers = outcome[0]
        confidence = outcome[1]
        outcome = {}
        for i, number in enumerate(numbers):
            outcome_config = get_number_config_for_index(config, all_probabilities[i])
            id = outcome_config["id"]
            res = {
                "number": number,
                "shortName": outcome_config["shortName"],
                "displayName": outcome_config["displayName"]
            }
            outcome[id] = res
        outcome["confidence"] = confidence

        print(outcome)
        outcomes.append(outcome)
    return outcomes


def get_checksum_indexes(checksum_config, numbers):
    sigma = checksum_config["sigma"]
    sigma_indexes = []
    total = -1
    for i, number in enumerate(numbers):
        if number["id"] in sigma:
            sigma_indexes.append(i)
        if number["id"] == checksum_config["total"]:
            total = i
    return sigma_indexes, total


def calculate_single_set(categories_count, config, all_probabilities, checksum):
    checksum_indexes = get_checksum_indexes(checksum, all_probabilities)
    outcome_matrix = get_numbers(checksum_indexes, all_probabilities, categories_count)
    return print_outcome(config, outcome_matrix, all_probabilities)


def get_total_of_checksum(numbers, checksum):
    numbers_in_checksum = []
    for j, extract in enumerate(numbers):
        if extract["id"] == checksum["total"]:
            numbers_in_checksum.append(extract)
    return numbers_in_checksum


def get_numbers_in_checksum_sigma_part(numbers, checksum):
    numbers_in_checksum = []
    for j, extract in enumerate(numbers):
        if extract["id"] in checksum["sigma"]:
            numbers_in_checksum.append(extract)
    return numbers_in_checksum


def get_numbers_in_checksum_set(numbers, checksum):
    numbers_in_checksum = get_numbers_in_checksum_sigma_part(numbers, checksum)
    numbers_in_checksum.extend(get_total_of_checksum(numbers, checksum))
    return numbers_in_checksum


def get_individual_numbers(numbers, checksums):
    numbers_in_checksums = {}
    for i, checksum in enumerate(checksums):
        for j, number_in_checksum in enumerate(get_numbers_in_checksum_set(numbers, checksum)):
            numbers_in_checksums[number_in_checksum["id"]] = number_in_checksum

    numbers_not_in_checksums = []
    for i, number in enumerate(numbers):
        in_checksums = filter(lambda x: x == number["id"], numbers_in_checksums)
        if not in_checksums:
            numbers_not_in_checksums.append(number)

    return numbers_not_in_checksums


def get_possible_outcomes_for_config(config, numbers, categories_count):
    all_sets = []
    for checksum in config["checkSums"]:
        numbers_in_set = get_numbers_in_checksum_set(numbers, checksum)
        all_sets.append(calculate_single_set(categories_count, config, numbers_in_set, checksum))

    individual_numbers = get_individual_numbers(numbers, config["checkSums"])
    for individual_number in individual_numbers:
        single_set = calculate_single_set(categories_count, config, individual_numbers,
                                          {"total": individual_number["id"], "sigma": individual_number["id"]})
        all_sets.append(single_set)
    return all_sets


def get_numbers(check_sums, all_probabilities, categories_count):
    all_numbers = []
    for j, extract in enumerate(all_probabilities):
        for i, probabilities in enumerate(extract["probabilitiesForNumber"]):
            if len(probabilities) is 0:
                all_numbers = all_numbers + ([0] * categories_count)
            else:
                all_numbers = all_numbers + probabilities
    return get_outcome_matrix(check_sums, np.asarray(all_numbers), categories_count, len(all_probabilities))


def numbers_add_up(probabilities, sigma_total):
    sigma, total = sigma_total
    running_total = 0
    expected_total = probabilities[total]
    for index in sigma:
        running_total += probabilities[index]
    return running_total == expected_total


def get_outcome_matrix(check_sums, all_squares, categories_count, number_count):
    all_numbers_matrix = all_squares.reshape(number_count, DIGITS_PER_NUMBER, categories_count)

    def matrix_to_number(number_matrix):
        possible_values = get_possible_values(number_matrix)
        return map(lambda x: make_number(x[0], x[1]), possible_values)

    all_numbers = map(matrix_to_number, all_numbers_matrix[0:number_count])
    possibilities = get_possible_end_results(all_numbers)

    def reduce_probability_if_checksum_is_wrong(p):
        probabilities = p[0]
        confidence = p[1]
        if numbers_add_up(probabilities, check_sums):
            print("numbers add up :-)")
            return p
        else:
            print("numbers don't add up :-(")
            return probabilities, confidence * .005

    bigger_than_zero = filter(lambda x: x[1] > 0, possibilities)
    results = [reduce_probability_if_checksum_is_wrong(x) for x in bigger_than_zero]

    results.sort(key=lambda x: -x[1])
    return results

def get_possible_outcomes(all_squares, categories_count):
    results = get_outcome_matrix(all_squares, categories_count)
    return print_possible(results[0:NUMBER_COUNT])


def read_json(data):
    rows = data["probabilities"]
    probability_matrix = np.ndarray(shape=(12, 11), dtype='f')

    for i, row in enumerate(rows):
        probability_matrix[i] = row

    return probability_matrix
