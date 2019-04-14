import pickle
from os import path

import numpy as np
import cv2
import os
import datetime
import math
import json
import logging
from os.path import join

from kawalc1 import settings
from mengenali.io import write_image, read_image, image_url, is_url

logging.basicConfig(level=logging.DEBUG)


def print_result(result_writer, iteration, homography, transform, result):
    row = [str(iteration), str(datetime.datetime.now()), homography, transform, result]
    logging.info("output: " + str(row))
    print(row)


def create_response(image_path, success, hash):
    transformed_path = path.join('transformed', image_path)
    return json.dumps(
        {'transformedUrl': image_url(transformed_path), 'transformedUri': path.join('.', 'static', transformed_path),
         'hash': str(hash), 'success': success},
        separators=(',', ':'))


def get_target_path(file_path, target_path):
    full_path, ext = os.path.splitext(file_path)
    path_with_ext = f'{full_path}{settings.TARGET_EXTENSION}'
    if is_url(path_with_ext):
        path_parts = path_with_ext.split(os.sep)
        return path.join(target_path, path_parts[-1])
    head, file_name = os.path.split(path_with_ext)
    return "trans" + file_name


def write_transformed_image(image_transformed, homography, transform, good_enough_match, file_path, output_path,
                            target_path):
    file_prefix = "~trans" if good_enough_match else "~bad"
    # transformed_image = file_prefix + "~hom" + str(homography) + "~warp" + str(transform) + "~" + file_name

    transformed_image = get_target_path(file_path, target_path)

    image_path = join(output_path, transformed_image)

    write_image(image_path, image_transformed)

    result = "good" if good_enough_match else "bad"
    logging.info("%s image", result)
    return transformed_image


def unpickle_keypoints(array):
    keypoints = []
    descriptors = []
    for point in array:
        temp_feature = cv2.KeyPoint(x=point[0][0], y=point[0][1], _size=point[1], _angle=point[2], _response=point[3],
                                    _octave=point[4], _class_id=point[5])
        temp_descriptor = point[6]
        keypoints.append(temp_feature)
        descriptors.append(temp_descriptor)
    return keypoints, np.array(descriptors)


def read_descriptors(reference_form_path):
    with open(reference_form_path.replace('.jpg', '.p'), "rb") as pickled:
        return pickle.load(pickled)

# https://www.pyimagesearch.com/2017/11/27/image-hashing-opencv-python/
def dhash(image, hashSize=8):
    resized = cv2.resize(image, (hashSize + 1, hashSize))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def register_image(file_path, reference_form_path, output_path, result_writer, target_path=""):
    from datetime import datetime

    lap = datetime.now()
    key_points = read_descriptors(reference_form_path)
    ref_kp, ref_descriptors = unpickle_keypoints(key_points['keypoints'])
    h = key_points['h']
    w = key_points['w']

    logging.info("BRISK reference %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    image = read_image(file_path)
    logging.info("image read %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    hash = dhash(image)

    brisk = cv2.BRISK_create()
    im_kp, im_descriptors = brisk.detectAndCompute(cv2.resize(image, None, fx=1.0, fy=1.0), None)
    logging.info("BRISK image %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    bf = cv2.BFMatcher(cv2.NORM_L2)
    raw_matches = bf.knnMatch(np.float32(im_descriptors), trainDescriptors=np.float32(ref_descriptors), k=2)
    logging.info("knn matched %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    matches = filter_matches(im_kp, ref_kp, raw_matches)
    logging.warning("matches %s", matches.__sizeof__())

    # show_match(im_kp, image, raw_matches, ref_kp, reference_form_path)

    mkp1, mkp2 = zip(*matches)
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])

    homography_transform, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)

    logging.info("RANSAC  %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    homography, transform = check_homography(homography_transform)

    # good_enough_match = check_match(homography, transform)
    good_enough_match = True

    image_transformed = cv2.warpPerspective(image, homography_transform, (w, h))
    logging.info("transformed image %s, %s", file_path, (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    transformed_image = write_transformed_image(image_transformed, homography, transform, good_enough_match, file_path,
                                                output_path, target_path)
    logging.info("transformed %s, %s", transformed_image, (datetime.now() - lap).total_seconds())
    return create_response(transformed_image, good_enough_match, hash)


def show_match(im_kp, image, raw_matches, ref_kp, reference_form_path):
    reference = cv2.imread(reference_form_path, 0)
    img_match = np.empty((max(reference.shape[0], image.shape[0]), reference.shape[1] + image.shape[1], 3),
                         dtype=np.uint8)
    good = []
    for m, n in raw_matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])
    # img3 = cv2.drawMatchesKnn(image, im_kp, reference, ref_kp, matches, None, **draw_params)
    im_matches = cv2.drawMatchesKnn(image, im_kp, reference, ref_kp, good, outImg=img_match, matchColor=None,
                                    singlePointColor=(255, 255, 255), flags=2)
    factor = 0.5
    im_matches_small = cv2.resize(im_matches, None, fx=factor, fy=factor)
    cv2.imshow("match", im_matches_small)
    cv2.waitKey(0)


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
        # tests=np.array([[10,20,20,10],[10,10,20,20],[1,1,1,1]])
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
