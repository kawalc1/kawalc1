import unittest
import extraction
from os import walk
import fnmatch
import io
import settings
import tempfile
import json


class RegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.overwrite_resources = False

    def assert_extraction_as_expected(self, c1_form):
        transformed_path = 'test/resources/forms/transformed/'
        for root, dirs, file_names in walk(transformed_path):
            found_files = fnmatch.filter(file_names, '*' + c1_form + '.jpg')
        self.assertEqual(1, len(found_files), msg="only one file should match pattern")
        output_path = tempfile.gettempdir()
        probability_map = extraction.extract(found_files[0], transformed_path, output_path, settings.STATIC_DIR)
        expected_json_file_path = 'test/resources/probabilities/' + c1_form + '.json'
        with io.open(expected_json_file_path, 'r') as expected_json_file:
            expected = expected_json_file.read()
            self.maxDiff = None
            expected_json = json.loads(expected)
            actual_json = json.loads(probability_map)
        if (expected_json != actual_json) and self.overwrite_resources:
            json_string = json.dumps(actual_json, encoding='utf-8')
            with io.open(expected_json_file_path, 'w', encoding='utf-8') as expected_json_file:
                expected_json_file.write(unicode(json.dumps(actual_json, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True)))
                expected_json_file.flush()
                expected_json_file.close()
        self.assertEqual(expected_json, actual_json)

    def test_overwrite_resources_should_be_false(self):
        self.assertFalse(self.overwrite_resources)

    def test_extraction_succeeds_for_reference_form(self):
        self.assert_extraction_as_expected('1773007-005324400804')


if __name__ == '__main__':
    unittest.main()