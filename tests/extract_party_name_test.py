import unittest

from mengenali.io import read_image
from mengenali.image_classifier import detect_most_similar
from tests import setup_django_settings


class ImageMatchTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_django_settings()

    def assert_most_similar(self, party_file, expected_result, image_base_path: str = 'parties',
                            feature_base_path: str = 'party_features'):
        reference_form_path = f'./resources/{image_base_path}/{party_file}'
        image = read_image(reference_form_path)
        party, confidence = detect_most_similar(image, f'datasets/{feature_base_path}')
        self.assertTrue(expected_result in party, f'Expected {expected_result} in {party}')

    def test_detect_party_pdi(self):
        self.assert_most_similar('transDPR_PDI~namaPartai.jpg', 'PDI-PERJUANGAN')

    def test_detect_party_pkb(self):
        self.assert_most_similar('transDPR-PKB~namaPartai.jpg', 'PARTAI-KEBANGKITAN-BANGSA')

    def test_detect_party_gerindra(self):
        self.assert_most_similar('transDPR-GERINDRA~namaPartai.jpg', 'PARTAI-GERINDRA')

    def test_detect_form_second(self):
        self.assert_most_similar('pilpres-2024-hal2.jpg', 'hal2', 'forms', 'form_features')

    def test_detect_form_third(self):
        self.assert_most_similar('pilpres-2024-hal3.jpg', 'hal3', 'forms', 'form_features')
