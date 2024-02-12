import os
import unittest
from pathlib import Path

import cv2

from kawalc1 import settings
from mengenali import imageclassifier
from mengenali.bubble_sheet_reader import extract_digits
from mengenali.extraction import unsharp_image, pre_process_digits, select_digits, extract_biggest_box
from mengenali.io import read_image
from mengenali.image_classifier import detect_most_similar
from tests import setup_django_settings
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

class ExtractBubbleSheet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_django_settings()

    def assert_most_similar(self, bubble_file: str, expected_number: int):
        reference_form_path = f'./resources/bubble_sheet/{bubble_file}'
        digits = extract_digits(Path(reference_form_path))
        print(digits)
        number = f"{digits[0][0]}{digits[1][0]}{digits[2][0]}"
        self.assertEqual(int(number), expected_number)

    def test_detect_sheet1(self):
        self.assert_most_similar('static_2024_transformed_6208022004_1~bubbleSheet1.webp', 123)
        self.assert_most_similar('static_2024_transformed_6208022004_1~bubbleSheet2.webp', 274)
        self.assert_most_similar('static_2024_transformed_6208022004_1~bubbleSheet3.webp', 42)

    def test_detect_sheet2(self):
        self.assert_most_similar('static_2024_transformed_6472061004_21~bubbleSheet1.webp', 75)
        self.assert_most_similar('static_2024_transformed_6472061004_21~bubbleSheet2.webp', 72)
        self.assert_most_similar('static_2024_transformed_6472061004_21~bubbleSheet3.webp', 60)

