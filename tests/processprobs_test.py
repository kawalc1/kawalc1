import unittest
import json
from mengenali import processprobs as pp


class ProcessProbabilitiesTest(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):

        # json_file = open('tests/resources/probabilities/1773007-005324400804.json')
        # cls.json_data = json.load(json_file)
        # json_file = open('./resources/probabilities/processprobs.wsgi.json')
        # cls.json_data = json.load(json_file)
        #
        # config_file = open('../static/datasets/digit_config.json')
        # cls.config = json.load(config_file)
        # json_file.close()

    # def test_json_is_read_correctly(self):
    #     numpy_table = pp.read_json(self.json_data)
    #     self.assertAlmostEqual(numpy_table[0][0], 0.00055694778)

    def test_get_numbers(self):
        outcomes = pp.get_possible_outcomes_for_config(self.config, self.json_data["probabilities"], 11)
        most_likely = outcomes[0][0]
        print("most likely", str(most_likely))
        self.assertAlmostEqual(most_likely['confidence'],  0.7020011959926853)
        self.assertEqual(most_likely['jokowi'], 186)
        self.assertEqual(most_likely['prabowo'], 117)
        self.assertEqual(most_likely['jumlah'], 303)

    def test_get_numbers2(self):
        json_file = open('./resources/probabilities/IMG_4221.json')
        json_data = json.load(json_file)

        config_file = open('../static/datasets/pilpres_2019_plano.json')
        config = json.load(config_file)
        json_file.close()

        numbers = json_data["numbers"]
        probabilities = []
        for number in numbers:
            probability_set = {"id": number["id"]}
            number_probabilities = []

            for digit_probability in number["extracted"]:
                number_probabilities.append(digit_probability["probabilities"])
            probability_set["probabilitiesForNumber"] = number_probabilities
            probabilities.insert(0, probability_set)
        print("probz", probabilities)

        outcomes = pp.get_possible_outcomes_for_config(config, probabilities, 11)
        most_likely = outcomes[0][0]
        print("most likely", str(most_likely))
        self.assertAlmostEqual(most_likely['confidence'], 0.7020011959926853)
        self.assertEqual(most_likely['jokowi'], 186)
        self.assertEqual(most_likely['prabowo'], 117)
        self.assertEqual(most_likely['jumlah'], 303)

    # def test_get_halaman_tiga_numbers(self):
    #     json_file = open('./resources/probabilities/hal3_processprobs.wsgi.json')
    #     hal3_json_data = json.load(json_file)
    #
    #     config_file = open('../static/datasets/hal_3_digit_config.json')
    #     hal3_config = json.load(config_file)
    #
    #     outcomes = pp.get_possible_outcomes_for_config(hal3_config, hal3_json_data["probabilities"], 11)
    #     most_likely = outcomes[0]
    #     print(str(most_likely))
    #     self.assertEqual(most_likely['ADPTLaki'], 221)
    #     self.assertEqual(most_likely['ADPTPerempuan'], 255)
    #     self.assertEqual(most_likely['ADPTJumlah'], 476)
    #     self.assertAlmostEqual(most_likely['confidence'],  0.699716392401)


if __name__ == '__main__':
    unittest.main()