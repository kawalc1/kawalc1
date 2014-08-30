import unittest
import registration
from os import walk
import fnmatch

class RegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.overwrite_resources = False

    def assert_extraction_as_expected(self, c1_form, expected_result):
        transformed_path = 'test/resources/forms/transformed/'
        for root, dirs, file_names in walk(transformed_path):
            found_files = fnmatch.filter(file_names, '*' + c1_form)
        self.assertEqual(1, len(found_files))


    def test_overwrite_resources_should_be_false(self):
        self.assertFalse(self.overwrite_resources)

    def test_extraction_succeeds_for_reference_form(self):
        self.assert_extraction_as_expected('1773007-005324400804.jpg', True)


if __name__ == '__main__':
    unittest.main()