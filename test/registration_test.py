import unittest
from mengenali import registration
import tempfile
import json
import io
from os.path import join, exists, abspath


class RegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.overwrite_resources = False

    def assert_registration_as_expected(self, c1_form, expected_result):
        originals_path = './resources/forms/original/'
        image = join(originals_path, c1_form)
        self.assertTrue(exists(image))
        reference_form = '../static/datasets/referenceform.jpg'
        expected_output_path = './resources/forms/transformed'
        output_path = tempfile.gettempdir()
        registration_output = registration.register_image(image, reference_form, output_path, None, None)
        registration_json = json.loads(registration_output)
        success = registration_json["success"]

        self.assertEqual(success, expected_result, msg="registration success should be as expected")

        image_url = registration_json["transformedUrl"]
        temp_image_path = join(output_path, image_url)
        expected_image_path = join(expected_output_path, image_url)
        print("url", abspath(expected_image_path))
        self.assertTrue(exists(expected_image_path))

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
        self.assert_registration_as_expected('1773007-005324400804.jpg', True)

    def test_registration_fails_for_incorrect_form(self):
        self.assert_registration_as_expected('1386928-005381002001.jpg', False)


if __name__ == '__main__':
    unittest.main()