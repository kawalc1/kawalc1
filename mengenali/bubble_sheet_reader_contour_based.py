from pathlib import Path
from typing import Optional

import cv2
import imutils
import numpy as np


def group_to_number(group, thresholded_image) -> tuple[Optional[int], int]:
    sorted_by_y = sorted(group, key=lambda ctr: cv2.boundingRect(ctr)[1])
    len_group = len(group)
    if len_group != 10:
        return None, 0
    most_filled = (0, 0)
    second_most_filled = (0, 0)
    for idx, cont in enumerate(sorted_by_y):
        mask = np.zeros(thresholded_image.shape, dtype="uint8")
        cv2.drawContours(mask, [cont], -1, 255, -1)
        mask = cv2.bitwise_and(thresholded_image, thresholded_image, mask=mask)
        total = cv2.countNonZero(mask)

        if total > most_filled[1]:
            most_filled = (idx, total)
        elif total > second_most_filled[1]:
            second_most_filled = (idx, total)
        # cv2_imshow(mask)
        # print(f"{idx}: {total} {cv2.contourArea(cont)}")
    ratio = most_filled[1] / second_most_filled[1]
    if ratio > 1.2:
        return most_filled
    return 0


def extract_three_numbers(cnt):
    sorted_by_x = sorted(cnt, key=lambda ctr: cv2.boundingRect(ctr)[0])
    (previous_x, _, _, _) = cv2.boundingRect(sorted_by_x[0])

    contours = []
    contour_group = []
    for contour in sorted_by_x:
        (x, y, w, h) = cv2.boundingRect(contour)
        distance = x - previous_x
        if distance > 20:
            contours.append(contour_group)
            contour_group = []

        contour_group.append(contour)
        previous_x = x
    contours.append(contour_group)
    return contours


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
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    contours = find_contours(thresh)
    three = extract_three_numbers(contours)

    numbers = []
    for index in range(0,3):
        number = group_to_number(three[index], thresh)
        print(number)
        numbers.append(number)
    return numbers

