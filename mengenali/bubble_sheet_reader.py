from pathlib import Path

import cv2
import imutils
import numpy as np


def extract_three_numbers(cnt, height: int):
    sorted_by_x = sorted(cnt, key=lambda ctr: cv2.boundingRect(ctr)[0])
    step = height / 10

    steps: list[float] = [index * step for index in range(0, 10)]

    digits = []
    for bubble in sorted_by_x:
        (x, y, w, h) = cv2.boundingRect(bubble)

        differences = [abs(step - y) for step in steps]
        digits.append(differences.index(min(differences)))

    zeroes = [0 for _ in range(0, 3 - len(digits))]
    return zeroes + digits


def find_contours(thresholded_image):
    countours = cv2.findContours(thresholded_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    countours = imutils.grab_contours(countours)
    bubble_contours = []
    for c in countours:
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        # in order to label the contour as a question, region
        # should be sufficiently wide, sufficiently tall, and
        # have an aspect ratio approximately equal to 1
        if w >= 10 and h >= 10:
            bubble_contours.append(c)
    return bubble_contours


def extract_digits(path: Path):
    image = cv2.imread(str(path))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    thresh = cv2.threshold(closed, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    contours = find_contours(thresh)
    return extract_three_numbers(contours, thresh.shape[0])
