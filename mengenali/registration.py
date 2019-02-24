from os import path

import numpy as np
import cv2
import os
import datetime
import math
import json
import logging
from os.path import join
from mengenali.io import write_image, read_image, image_url, is_url

logging.basicConfig(level=logging.DEBUG)


def print_result(result_writer, iteration, homography, transform, result):
    row = [str(iteration), str(datetime.datetime.now()), homography, transform, result]
    logging.info("output: " + str(row))
    print(row)


def create_response(image_path, success, config_file):
    transformed_path = path.join('transformed', image_path)
    return json.dumps({'transformedUrl': image_url(transformed_path), 'transformedUri':  path.join('.', 'static', transformed_path),
                       'success': success, 'configFile': config_file},
                      separators=(',', ':'))


def get_target_path(file_path):
    if is_url(file_path):
        path_parts = file_path.split(os.sep)
        return path.join(path_parts[-3], path_parts[-2], path_parts[-1])
    head, file_name = os.path.split(file_path)
    return "trans" + file_name


def write_transformed_image(image_transformed, homography, transform, good_enough_match, file_path, output_path):
    file_prefix = "~trans" if good_enough_match else "~bad"
    # transformed_image = file_prefix + "~hom" + str(homography) + "~warp" + str(transform) + "~" + file_name

    transformed_image = get_target_path(file_path)

    image_path = join(output_path, transformed_image)

    write_image(image_path, image_transformed)

    result = "good" if good_enough_match else "bad"
    logging.info("%s image", result)
    return transformed_image


def register_image(file_path, reference_form_path, output_path, result_writer, config_file):
    from datetime import datetime
    lap = datetime.now()
    reference = cv2.imread(reference_form_path, 0)
    logging.info("read reference %s %s", reference_form_path, (datetime.now() - lap).total_seconds())
    lap = datetime.now()
    brisk = cv2.BRISK_create()
    kp2, des2 = brisk.detectAndCompute(reference, None)
    logging.info("BRISK reference %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    image = read_image(file_path)
    logging.info("image read %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    kp1, des1 = brisk.detectAndCompute(image, None)
    logging.info("BRISK image %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)  # or pass empty dictionary

    bf = cv2.FlannBasedMatcher(index_params,search_params)
    raw_matches = bf.knnMatch(np.float32(des1), trainDescriptors=np.float32(des2), k=2)
    logging.info("knn matched %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    matches = filter_matches(kp1, kp2, raw_matches)
    mkp1, mkp2 = zip(*matches)
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    homography_transform, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)

    logging.info("RANSAC  %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    homography, transform = check_homography(homography_transform)

    # good_enough_match = check_match(homography, transform)
    good_enough_match = True

    h, w = reference.shape
    image_transformed = cv2.warpPerspective(image, homography_transform, (w, h))
    logging.info("transformed image %s, %s", file_path, (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    transformed_image = write_transformed_image(image_transformed, homography, transform, good_enough_match, file_path,
                                                output_path)
    logging.info("transformed %s, %s", transformed_image, (datetime.now() - lap).total_seconds())
    return create_response(transformed_image, good_enough_match, config_file)


def process_file(result_writer, count, root, file_name, reference_form_path, config_file):
    image_path = join(root + '/upload', file_name)
    output_path = join(root, 'transformed')
    return register_image(image_path, reference_form_path, output_path, result_writer, config_file)


def check_match(homography, transform):
    if homography < 0.05:
        return True
    return homography < 1.0 or transform < 0.3


def filter_matches(kp1, kp2, matches, ratio=0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append(kp1[m.queryIdx])
            mkp2.append(kp2[m.trainIdx])
    kp_pairs = zip(mkp1, mkp2)
    return kp_pairs


def check_homography(homography_transform):
    homography = abs(homography_transform[0, 0] - homography_transform[1, 1])
    if homography > 0.01:
        # test=np.array([[10,20,20,10],[10,10,20,20],[1,1,1,1]])
        test = np.array([[10, 10, 1], [20, 10, 1], [20, 20, 1], [10, 20, 1]])
        # do the check
        trans = np.dot(test, homography_transform)
        # print trans
        dist1 = math.sqrt(math.pow(trans[0, 0] - trans[2, 0], 2) + math.pow(trans[0, 1] - trans[2, 1], 2))
        dist2 = math.sqrt(math.pow(trans[1, 0] - trans[3, 0], 2) + math.pow(trans[1, 1] - trans[3, 1], 2))

        measure = math.fabs((dist1 / dist2) - 1) - math.fabs((dist2 / dist1) - 1)
        absolute_measure = math.fabs(measure)
        return homography, absolute_measure
    else:
        return homography, 0
