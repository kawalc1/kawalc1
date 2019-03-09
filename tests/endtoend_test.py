import json
import unittest

from tests import setup_django_settings
from mengenali.views import download
from django.test.client import RequestFactory


class EndToEndTest(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        setup_django_settings()

    def do_end_to_end(self, kelurahan, tps, file_name):
        request = self.factory.get(
            f'/download/{kelurahan}/{tps}/{file_name}.JPG?extractDigits=true&calculateNumbers=true&storeFiles=true')
        response = download(request, kelurahan, tps, f"{file_name}.JPG")
        return json.loads(response.content)

    def assert_result(self, result, success, min, max):
        outcome = result['outcome']
        self.assertEqual(result['success'], success)
        if success:
            self.assertEqual(outcome['jokowi'], 11)
            self.assertEqual(outcome['prabowo'], 92)
            self.assertEqual(outcome['jumlah'], 103)
            self.assertEqual(outcome['tidakSah'], 8)
        self.assertGreaterEqual(result['duration'], min)
        self.assertLessEqual(result['duration'], max)

    def test_1_12_1(self):
        res = self.do_end_to_end(1, 12, 1)
        self.assert_result(res, True, 1.5, 6)

    def test_1_13_3(self):
        res = self.do_end_to_end(1, 13, 3)
        self.assert_result(res, True, 2.5, 7)

    def test_2_21_4(self):
        res = self.do_end_to_end(2, 21, 4)
        self.assert_result(res, True, 4, 8)

    def test_2_22_5(self):
        res = self.do_end_to_end(2, 22, 5)
        self.assert_result(res, True, 4, 6)

    def test_1_13_2(self):
        res = self.do_end_to_end(1, 13, 2)
        self.assert_result(res, False, 2.5, 7)
