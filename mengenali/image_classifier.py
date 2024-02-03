import logging
import math
import os
import pickle
import cv2
from kawalc1 import settings
import pathlib
import numpy as np

from mengenali.registration import unpickle_keypoints, filter_matches_with_amount, feature_similarity


def read_descriptors(reference_form_path):
    with open(reference_form_path, "rb") as pickled:
        return pickle.load(pickled)


def detect_most_similar(image, feature_path: str):
    brisk = cv2.BRISK_create()
    im_kp, im_descriptors = brisk.detectAndCompute(cv2.resize(image, None, fx=1.0, fy=1.0), None)

    features_dir = pathlib.Path(settings.STATIC_DIR).joinpath(feature_path)
    listdir = os.listdir(features_dir)
    most_similar = 0
    most_similar_form = ""
    for file in listdir:
        key_point_file = pathlib.Path(features_dir).joinpath(file)
        key_points = read_descriptors(key_point_file)
        ref_kp, ref_descriptors = unpickle_keypoints(key_points['keypoints'])

        bf = cv2.BFMatcher(cv2.NORM_L2)
        raw_matches = bf.knnMatch(np.float32(im_descriptors), trainDescriptors=np.float32(ref_descriptors), k=2)

        amount, matches = filter_matches_with_amount(im_kp, ref_kp, raw_matches)

        if amount > 0:
            mkp1, mkp2 = zip(*matches)
            similarity = feature_similarity(mkp1, mkp2)
            if similarity > most_similar:
                most_similar = similarity
                most_similar_form = file
    logging.info("match: %s %s", most_similar, most_similar_form)
    return most_similar_form.replace(".p", ""), most_similar



