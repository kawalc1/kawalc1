import math
import os
import pathlib
import pickle
import unittest

import cv2

from mengenali.io import read_image
from mengenali.registration import unpickle_keypoints
from tests import setup_django_settings
import numpy as np


class RegistrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_django_settings()


    def assert_most_similar(self, party_file, expected_result):
        def read_descriptors(reference_form_path):
            with open(reference_form_path, "rb") as pickled:
                return pickle.load(pickled)

        originals_path = './resources/parties/features'

        brisk = cv2.BRISK_create()

        reference_form_path = f'./resources/parties/{party_file}'
        image = read_image(reference_form_path)
        im_kp, im_descriptors = brisk.detectAndCompute(cv2.resize(image, None, fx=1.0, fy=1.0), None)

        def filter_matches_with_amount(kp1, kp2, matches, ratio=0.75):
            mkp1, mkp2 = [], []
            total = 0
            for m in matches:
                if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                    m = m[0]
                    total += 1
                    mkp1.append(kp1[m.queryIdx])
                    mkp2.append(kp2[m.trainIdx])
            kp_pairs = zip(mkp1, mkp2)
            return total, kp_pairs

        listdir = os.listdir(originals_path)
        most_similar = 0
        most_similar_form = ""
        for file in listdir:

            key_point_file = pathlib.Path(originals_path).joinpath(file)
            key_points = read_descriptors(key_point_file)
            ref_kp, ref_descriptors = unpickle_keypoints(key_points['keypoints'])

            bf = cv2.BFMatcher(cv2.NORM_L2)
            raw_matches = bf.knnMatch(np.float32(im_descriptors), trainDescriptors=np.float32(ref_descriptors), k=2)

            amount, matches = filter_matches_with_amount(im_kp, ref_kp, raw_matches)

            if amount > 0:
                mkp1, mkp2 = zip(*matches)
                p1 = np.float32([kp.pt for kp in mkp1])
                p2 = np.float32([kp.pt for kp in mkp2])

                distances = []
                for i in range(len(p1)):
                    x_dist = p1[i][0] - p2[i][0]
                    y_dist = p1[i][1] - p2[i][1]
                    hypot = math.pow(math.hypot(x_dist, y_dist), 2)
                    distances.append(hypot)
                median = np.median(distances)
                similarity = len(distances) / median
                if similarity > most_similar:
                    most_similar = similarity
                    most_similar_form = file
        print("match: ", most_similar, most_similar_form)
        self.assertTrue(expected_result in most_similar_form, f'Expected {expected_result} in {most_similar_form}')

    def test_detect_party_pdi(self):
        self.assert_most_similar('transDPR_PDI~namaPartai.jpg', 'PDI-PERJUANGAN')

    def test_detect_party_pkb(self):
        self.assert_most_similar('transDPR-PKB~namaPartai.jpg', 'PARTAI-KEBANGKITAN-BANGSA')
