import unittest
import json
from mengenali import processprobs as pp
from mengenali.processprobs import print_outcome, print_outcome_parsable


class ProcessProbabilitiesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config_file = open('../static/datasets/digit_config_pilpres_2019.json')
        cls.config = json.load(config_file)
        config_file.close()

    def test_json_is_read_correctly(self):
        numpy_table = pp.read_json(self.json_data)
        self.assertAlmostEqual(numpy_table[0][0], 0.00055694778)

    def test_get_numbers(self):
        outcomes = pp.get_possible_outcomes_for_config(self.config, self.json_data["numbers"], 11, print_outcome)
        most_likely = outcomes[0][0]
        print("most likely", str(most_likely))
        self.assertAlmostEqual(most_likely['confidence'],  0.7020011959926853)
        self.assertEqual(most_likely['jokowi'], 186)
        self.assertEqual(most_likely['prabowo'], 117)
        self.assertEqual(most_likely['jumlah'], 303)

    def test_get_numbers_yosua(self):
        json_file_yosua = open('./resources/probabilities/yosua-probablities.json')
        json_data_yosua = json.load(json_file_yosua)
        json_file_yosua.close()

        outcomes = pp.get_possible_outcomes_for_config(self.config, json_data_yosua["probabilities"], 11, print_outcome_parsable)
        presidential = outcomes[0][0]['numbers']

        self.assertEqual(presidential[0]['number'], 118)
        self.assertEqual(presidential[0]['shortName'], 'jokowi')

        self.assertEqual(presidential[1]['number'], 125)
        self.assertEqual(presidential[1]['shortName'], 'prabowo')

        self.assertEqual(presidential[2]['number'], 243)
        self.assertEqual(presidential[2]['shortName'], 'jumlah')

        summary = outcomes[1][0]['numbers']

        self.assertEqual(summary[0]['number'], 243)
        self.assertEqual(summary[0]['shortName'], 'jumlah')

        self.assertEqual(summary[1]['number'], 7)
        self.assertEqual(summary[1]['shortName'], 'tidakSah')

        self.assertEqual(summary[2]['number'], 250)
        self.assertEqual(summary[2]['shortName'], 'jumlahSeluruh')

        self.assertAlmostEqual(outcomes[1][0]['confidence'], 0.7333740994255918)

    def test_get_numbers_kpu(self):
        json_file_yosua = open('./resources/probabilities/kpu-probabilities.json')
        json_data_yosua = json.load(json_file_yosua)
        json_file_yosua.close()

        config_file = open('../static/datasets/digit_config_ppwp_scan_halaman_2_2019.json')
        config = json.load(config_file)
        outcomes = pp.get_possible_outcomes_for_config(config, json_data_yosua["probabilities"], 11, print_outcome_parsable)
        presidential = outcomes[0][0]['numbers']

        self.assertEqual(presidential[0]['number'], 10)
        self.assertEqual(presidential[0]['shortName'], 'jokowi')

        self.assertEqual(presidential[1]['number'], 178)
        self.assertEqual(presidential[1]['shortName'], 'prabowo')

        self.assertEqual(presidential[2]['number'], 188)
        self.assertEqual(presidential[2]['shortName'], 'jumlah')

        summary = outcomes[1][0]['numbers']

        self.assertEqual(summary[0]['number'], 188)
        self.assertEqual(summary[0]['shortName'], 'jumlah')

        self.assertEqual(summary[1]['number'], 10)
        self.assertEqual(summary[1]['shortName'], 'tidakSah')

        self.assertEqual(summary[2]['number'], 198)
        self.assertEqual(summary[2]['shortName'], 'jumlahSeluruh')

        self.assertAlmostEqual(outcomes[1][0]['confidence'], 0.11396216028446514)
        config_file.close()


if __name__ == '__main__':
    unittest.main()