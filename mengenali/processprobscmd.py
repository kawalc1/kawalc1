import argparse
import os
import fnmatch
import shutil
from os.path import join, getsize
import csv
import itertools
import string
import numpy
import operator
import json
#setup the argument parser

CATEGORIES_COUNT = 11
X_INDEX = 10


parser = argparse.ArgumentParser()
parser.add_argument("inputcsv", help="location of the image files")
args = parser.parse_args()

inputcsv=args.inputcsv


def getProbs(row):
    rowprobs = []
    for item in row[0:CATEGORIES_COUNT]:
        rowprobs.append(float(item))
    return rowprobs


def getCurrentSquare(row):
    filename = row[CATEGORIES_COUNT + 1]
    splitter = filename.split("~")
    return int(splitter[-1])


def get_possible_values(list_of_probs, threshold=.10):
    """ [[digit, confidence]] -> [[digit], confidence]
    Each item in the list that has a confidence of higher than the threshold is
    taken into account as a possibility. All possible lists of digits are
    constructed (taking one digit per outer list) and given a confidence by
    multiplying the confidences of its digits."""

    total_probs = []

    for probs in list_of_probs:
        high_probs = filter(lambda x: x[1] > threshold, enumerate(probs))

        print(high_probs)

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


def print_possible(after_bla):
    for x in after_bla:
        print("P: " + str(x[0][0]) + ", J: " + str(x[0][1]) + ", T: " + str(x[0][2]) + ", Confidence: " + str(x[1]))


def print_list_of_numbers(all_squares):
    all_numbers_matrix = all_squares.reshape(4, 3, 11)

    def matrix_to_number(number_matrix):
        possible_values = get_possible_values(number_matrix)
        return map(lambda x: make_number(x[0], x[1]), possible_values)

    all_numbers = map(matrix_to_number, all_numbers_matrix[0:3])

    possibilities = get_possible_end_results(all_numbers)

    def reduce_probability_if_checksum_is_wrong(p):
        if p[0][0] + p[0][1] == p[0][2]:
            return p
        else:
            return p[0], p[1] * .005

    results = map(reduce_probability_if_checksum_is_wrong,
                  filter(lambda x: x[1] > 0, possibilities))

    results.sort(key=lambda x: -x[1])
    print_possible(results[0:3])


with open(inputcsv, 'rb') as f:
    reader = csv.reader(f)
    row = reader.next()

#     while True:
    print("", row[12], "")

    probmatrix = numpy.zeros(shape=(12, 11), dtype='f')
    for square in range(0, 12):
        if square == getCurrentSquare(row):
            probmatrix[square] = getProbs(row)
            row = reader.next()
        else:
            probmatrix[square] = numpy.zeros(11)
            probmatrix[square][X_INDEX] = 1.

    print(json.dumps({'probabilityMatrix': probmatrix.tolist()}, separators=(',', ':')))
    #     print "mat" + str(probmatrix)
    print_list_of_numbers(probmatrix)