import itertools
import logging
import numpy as np

DIGITS_PER_NUMBER = 3
X_INDEX = 10


def get_possible_outcomes_for_config(config, numbers, categories_count, summary_function):
    all_sets = []
    for checksum in config["checkSums"]:
        numbers_in_set = get_numbers_in_checksum_set(numbers, checksum)
        all_sets.append(calculate_single_set(categories_count, config, numbers_in_set, checksum, summary_function))

    individual_numbers = get_individual_numbers(numbers, config["checkSums"])
    for individual_number in individual_numbers:
        single_set = calculate_single_set(categories_count, config, individual_numbers,
                                          {"total": individual_number["id"], "sigma": individual_number["id"]},
                                          summary_function)
        all_sets.append(single_set)
    return all_sets


def possible_numbers_for_digit_confidence_matrix(digit_confidence_matrix, threshold=.10):
    """ For each digit in the final number we are given the probabilities for each value. This
    function disregards any values with a probability lower than the threshold and then computes
    all possible numbers by taking the cartesian product of all possible values for each digit.
    The confidence rating for each number will be the product of the confidence rating of each of
    its digits
    """

    possible_numbers = []

    for digit_confidence_list in digit_confidence_matrix:
        possible_digits = list(filter(lambda x: x[1] > threshold, enumerate(digit_confidence_list)))

        if not possible_numbers:
            possible_numbers = list(map(lambda x: ([x[0]], x[1]), possible_digits))
        else:
            new_possible_numbers = []

            for [number, number_confidence] in possible_numbers:
                for [digit, digit_confidence] in possible_digits:
                    new_number = number + [digit]
                    new_confidence = number_confidence * digit_confidence
                    new_possible_numbers.append((new_number, new_confidence))

            possible_numbers = new_possible_numbers
    return possible_numbers


def get_possible_end_results(list_of_probs):
    total_probs = []


    for probs in list_of_probs:
        # if not total_probs:
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


def get_number_config_for_index(config, prob_index):
    for number in config["numbers"]:
        number_index = number["id"]
        if prob_index["id"] == number_index:
            return number
    return None


def print_outcome(config, outcome_matrix, all_probabilities):
    outcomes = []
    # logging.info(outcome_matrix)
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

        # logging.info(outcome)
        outcomes.append(outcome)
    return outcomes


def print_outcome_parsable(config, outcome_matrix, all_probabilities):
    outcomes = []
    logging.info(outcome_matrix)
    for outcome in outcome_matrix:
        numbers = outcome[0]
        confidence = outcome[1]
        outcome_array = []
        for i, number in enumerate(numbers):
            outcome_config = get_number_config_for_index(config, all_probabilities[i])
            res = {
                "id": outcome_config["id"],
                "number": number,
                "shortName": outcome_config["shortName"],
                "displayName": outcome_config["displayName"]
            }
            outcome_array.append(res)
        number_set = {
            "numbers": outcome_array,
            "confidence": confidence
        }
        outcomes.append(number_set)
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


def calculate_single_set(categories_count, config, all_probabilities, checksum, print_function):
    checksum_indexes = get_checksum_indexes(checksum, all_probabilities)
    outcome_matrix = get_numbers(checksum_indexes, all_probabilities, categories_count)
    return print_function(config, outcome_matrix, all_probabilities)


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
        in_checksums = list(filter(lambda x: x == number["id"], numbers_in_checksums))
        if not in_checksums:
            numbers_not_in_checksums.append(number)

    return numbers_not_in_checksums


def get_numbers(check_sums, all_probabilities, categories_count):
    all_numbers = []
    counts_as_zero = ([0.0] * categories_count)
    counts_as_zero[0] = 1.0
    for j, extract in enumerate(all_probabilities):
        probabilities = extract["probabilitiesForNumber"]
        print(f"LEN: {len(probabilities)}")
        print(f"{counts_as_zero}")
        print(f"{probabilities}")

        for i, probabilities in enumerate(probabilities):
            if len(probabilities) == 0:
                all_numbers = all_numbers + counts_as_zero
            elif len(probabilities) == 2:
                all_numbers = all_numbers + counts_as_zero
            else:
                all_numbers = all_numbers + probabilities
    print("ALL")
    return get_outcome_matrix(check_sums, np.asarray(all_numbers), categories_count, len(all_probabilities))


def numbers_add_up(probabilities, sigma_total):
    sigma, total = sigma_total
    running_total = 0
    expected_total = probabilities[total]
    for index in sigma:
        running_total += probabilities[index]
    return running_total == expected_total


def get_outcome_matrix(check_sums, all_squares, categories_count, number_count):
    print(check_sums, all_squares, categories_count, number_count)
    all_numbers_matrix = all_squares.reshape(number_count, DIGITS_PER_NUMBER, categories_count)

    def matrix_to_number(digit_confidence_matrix):
        possible_values = possible_numbers_for_digit_confidence_matrix(digit_confidence_matrix)
        return list(map(lambda x: make_number(x[0], x[1]), possible_values))

    all_numbers = list(map(matrix_to_number, all_numbers_matrix[0:number_count]))

    possibilities = get_possible_end_results(all_numbers)
    def reduce_probability_if_checksum_is_wrong(p):
        probabilities = p[0]
        confidence = p[1]
        if numbers_add_up(probabilities, check_sums):
            # logging.info("numbers add up :-)")
            return p
        else:
            # logging.info("numbers don't add up :-(")
            return probabilities, confidence * .005

    bigger_than_zero = list(filter(lambda x: x[1] > 0, possibilities))
    results = [reduce_probability_if_checksum_is_wrong(x) for x in bigger_than_zero]

    results.sort(key=lambda x: -x[1])
    return results


def read_json(data):
    rows = data["probabilities"]
    probability_matrix = np.ndarray(shape=(12, 11), dtype='f')

    for i, row in enumerate(rows):
        probability_matrix[i] = row

    return probability_matrix
