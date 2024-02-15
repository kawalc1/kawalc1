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
        if w >= 10 and h >= 10:
            bubble_contours.append(c)
    return bubble_contours


def extract_digits_from_path(path: Path):
    image = cv2.imread(str(path))
    extract_digits(image)


def extract_digits(gray):
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    thresh = cv2.threshold(closed, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    contours = find_contours(thresh)
    numbers = extract_three_numbers(contours, thresh.shape[0])
    return int(f"{numbers[0]}{numbers[1]}{numbers[2]}")
