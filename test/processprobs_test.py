import unittest
import json
import processprobs as pp


class ProcessProbabilitiesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # json_file = open('test/resources/probabilities/1773007-005324400804.json')
        # cls.json_data = json.load(json_file)
        json_file = open('test/resources/probabilities/processprobs.wsgi.json')
        cls.json_data = json.load(json_file)

        config_file = open('static/datasets/digit_config.json')
        cls.config = json.load(config_file)
        json_file.close()

    # def test_json_is_read_correctly(self):
    #     numpy_table = pp.read_json(self.json_data)
    #     self.assertAlmostEqual(numpy_table[0][0], 0.00055694778)

    def test_get_numbers(self):
        outcomes = pp.get_possible_outcomes_for_config(self.config, self.json_data["probabilities"], 11)
        most_likely = outcomes[0]
        print str(most_likely)
        self.assertEqual(most_likely['jokowi'], 186)
        self.assertEqual(most_likely['prabowo'], 117)
        self.assertEqual(most_likely['jumlah'], 303)


if __name__ == '__main__':
    unittest.main()