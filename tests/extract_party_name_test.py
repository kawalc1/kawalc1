import unittest

from mengenali.io import read_image
from mengenali.partyclassifier import detect_party
from tests import setup_django_settings


class PartyMatchTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_django_settings()

    def assert_most_similar(self, party_file, expected_result):
        reference_form_path = f'./resources/parties/{party_file}'
        image = read_image(reference_form_path)
        party, confidence = detect_party(image)
        self.assertTrue(expected_result in party, f'Expected {expected_result} in {party}')

    def test_detect_party_pdi(self):
        self.assert_most_similar('transDPR_PDI~namaPartai.jpg', 'PDI-PERJUANGAN')

    def test_detect_party_pkb(self):
        self.assert_most_similar('transDPR-PKB~namaPartai.jpg', 'PARTAI-KEBANGKITAN-BANGSA')

    def test_detect_party_gerindra(self):
        self.assert_most_similar('transDPR-GERINDRA~namaPartai.jpg', 'PARTAI-GERINDRA')
