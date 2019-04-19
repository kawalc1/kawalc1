import unittest

from numpy import unicode

from mengenali import views
from mengenali import extraction
from os import walk
import fnmatch
import io
from app import settings
import tempfile
import json


class RegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.overwrite_resources = False

    def assert_extraction_as_expected(self, c1_form, config_file):
        config = views.load_config(config_file)
        transformed_path = './resources/forms/transformed/'
        found_files = []
        for root, dirs, file_names in walk(transformed_path):
            found_files = fnmatch.filter(file_names, '*' + c1_form + '.jpg')
        self.assertEqual(1, len(found_files), msg="only one file should match pattern")
        output_path = tempfile.gettempdir()
        probability_map = extraction.extract_deprecated(found_files[0], transformed_path, output_path, settings.STATIC_DIR, config)
        expected_json_file_path = './resources/probabilities/' + c1_form + '.json'
        with io.open(expected_json_file_path, 'r') as expected_json_file:
            expected = expected_json_file.read()
            self.maxDiff = None
            expected_json = json.loads(expected)
            actual_json = json.loads(probability_map)
        if (expected_json != actual_json) and self.overwrite_resources:
            json_string = json.dumps(actual_json)
            with io.open(expected_json_file_path, 'w') as expected_json_file:
                expected_json_file.write(unicode(json.dumps(actual_json, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True)))
                expected_json_file.flush()
                expected_json_file.close()
        self.assertEqual(expected_json, actual_json)

    def test_overwrite_resources_should_be_false(self):
        self.assertFalse(self.overwrite_resources)

    def test_extraction_succeeds_for_reference_form(self):
        self.assert_extraction_as_expected('1773007-005324400804', 'digit_config.json')

    def test_extraction_succeeds_for_reference_form2(self):
        self.assert_extraction_as_expected('IMG_4221', 'pilpres_2019_plano.json')


if __name__ == '__main__':
    unittest.main()