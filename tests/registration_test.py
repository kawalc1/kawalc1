import os
import pathlib
import unittest
from mengenali import registration
import tempfile
import json
import io
from os.path import join, exists, abspath

from tests import setup_django_settings


class RegistrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.overwrite_resources = False
        setup_django_settings()

    def assert_registration_as_expected(self, c1_form, reference_form_rel_path, expected_result):
        reference_form_path = pathlib.Path(os.getenv('BASEDIR', '..')).joinpath(reference_form_rel_path)
        if not reference_form_path.exists():
            raise Exception('set BASEDIR in environment to resolve the test data or run the test from its directory')

        reference_form = reference_form_path.as_posix()

        originals_path = './resources/forms/original/'
        image = pathlib.Path(originals_path).joinpath(c1_form)
        print("\n" + str(image.resolve()))
        self.assertTrue(image.exists())
        expected_output_path = './resources/forms/transformed'
        output_path = './resources/temp/transformed'
        registration_output = registration.register_image(image.as_posix(), reference_form, output_path, None, None)
        registration_json = json.loads(registration_output)
        success = registration_json["success"]

        self.assertEqual(success, expected_result, msg="registration success should be as expected")

        image_name = registration_json["transformedUrl"].split('/')[1]
        temp_image_path = join(output_path, image_name)
        expected_image_path = join(expected_output_path, image_name)
        print("url", abspath(expected_image_path))

        self.assertTrue(exists(expected_image_path))

        print(os.path.abspath(temp_image_path))
        self.assertTrue(exists(temp_image_path))

        with io.FileIO(temp_image_path, mode='rb') as actual_image, io.FileIO(expected_image_path,
                                                                              mode='rb') as expected_image:
            actual_bytes = actual_image.readall()
            expected_bytes = expected_image.readall()

        if actual_bytes != expected_bytes and self.overwrite_resources:
            with io.FileIO(expected_image_path, mode='wb') as file_to_over_write:
                file_to_over_write.write(actual_bytes)
                file_to_over_write.flush()
        self.assertEqual(actual_bytes, expected_bytes, msg="images should be identical")

    def test_overwrite_resources_should_be_false(self):
        self.assertFalse(self.overwrite_resources)

    def test_registration_succeeds_for_reference_form(self):
        self.assert_registration_as_expected('1773007-005324400804.jpg', 'static/datasets/referenceform.jpg', True)

    def test_registration_succeeds_for_reference_form_plano(self):
        self.assert_registration_as_expected('DPR-2019-plano.jpg', 'static/datasets/DPR-2019-plano.jpg', True)

    def test_registration_fails_for_incorrect_form(self):
        self.assert_registration_as_expected('1386928-005381002001.jpg', 'static/datasets/referenceform.jpg', False)

    def test_registration_succeeds_for_other_form1(self):
        self.assert_registration_as_expected('IMG_4217.JPG', 'static/datasets/2019-reference2.jpg', True)

    def test_registration_succeeds_for_other_form2(self):
        self.assert_registration_as_expected('IMG_4218.JPG', 'static/datasets/2019-reference2.jpg', True)

    def test_registration_succeeds_for_other_form3(self):
        self.assert_registration_as_expected('IMG_4219.JPG', 'static/datasets/2019-reference2.jpg', True)

    def test_registration_succeeds_for_other_form4(self):
        self.assert_registration_as_expected('IMG_4220.JPG', 'static/datasets/2019-reference2.jpg', True)

    def test_registration_succeeds_for_other_form6(self):
        self.assert_registration_as_expected('IMG_4221.JPG', 'static/datasets/2019-reference2.jpg', True)

    def test_registration_succeeds_for_other_form7(self):
        self.assert_registration_as_expected('IMG_4221.JPG', 'static/datasets/2019-reference2.jpg', True)


if __name__ == '__main__':
    unittest.main()