import unittest
from pathlib import Path

from mengenali.bubble_sheet_reader import extract_digits_from_path
from tests import setup_django_settings


class ExtractBubbleSheet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_django_settings()

    def assert_most_similar(self, bubble_file: str, expected_number):
        reference_form_path = f'./resources/bubble_sheet/{bubble_file}'
        digits = extract_digits_from_path(Path(reference_form_path))
        print(digits)
        number = [digits[0], digits[1], digits[2]]
        self.assertEqual(number, expected_number)

    def test_detect_sheet1(self):
        self.assert_most_similar('static_2024_transformed_6208022004_1~bubbleSheet1.webp', [1,2,3])
        self.assert_most_similar('static_2024_transformed_6208022004_1~bubbleSheet2.webp', [2,7,4])
        self.assert_most_similar('static_2024_transformed_6208022004_1~bubbleSheet3.webp', [0,3,2])

    def test_detect_sheet2(self):
        self.assert_most_similar('static_2024_transformed_6472061004_21~bubbleSheet1.webp', [0,7,5])
        self.assert_most_similar('static_2024_transformed_6472061004_21~bubbleSheet2.webp', [0,7,2])
        self.assert_most_similar('static_2024_transformed_6472061004_21~bubbleSheet3.webp', [0,6,0])

