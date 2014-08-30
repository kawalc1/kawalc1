import unittest
import registration
import tempfile
import json
from os.path import join, exists

class RegistrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bla = True

    def test_registration_succeeds_for_reference_form(self):
        image = 'test/resources/forms/original/1773007-005324400804.jpg'
        reference_form = 'static/datasets/referenceform.jpg'
        expected_output_path = 'test/resources/forms/transformed'
        output_path = tempfile.gettempdir()
        registration_output = registration.register_image(image, reference_form, output_path, None)
        registration_json = json.loads(registration_output)

        temp_image = join(output_path, registration_json["transformedUrl"])
        reference_image = join(expected_output_path, registration_json["transformedUrl"])
        self.assertTrue(exists(temp_image))
        with open(temp_image) as actual_image, open(reference_image) as expected_image:
            self.assertEqual(actual_image.read(), expected_image.read())

if __name__ == '__main__':
    unittest.main()