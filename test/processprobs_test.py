import unittest
import json
import processprobs as pp


class ProcessProbabilitiesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        json_file = open('test/resources/probabilities/1773007-005324400804.json')
        cls.json_data = json.load(json_file)
        json_file.close()

    def test_json_is_read_correctly(self):
        numpy_table = pp.read_json(self.json_data)
        self.assertEqual(numpy_table[0][0], 0.00017933209892362356)

    def test_get_possible_outcomes_returns_correct_outcome(self):
        numpy_table = pp.read_json(self.json_data)
        outcomes = pp.get_possible_outcomes(numpy_table, 10)
        most_likely = outcomes[0]

        self.assertEqual(most_likely['jokowi'], 186)
        self.assertEqual(most_likely['prabowo'], 117)
        self.assertEqual(most_likely['total'], 303)


if __name__ == '__main__':
    unittest.main()