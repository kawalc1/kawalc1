import numpy as np
import cv2
import os
import datetime
import math
import json
import logging
from os.path import join

logging.basicConfig(level=logging.DEBUG)


def print_result(result_writer, iteration, homography, transform, result):
    row = [str(iteration), str(datetime.datetime.now()), homography, transform, result]
    logging.info("output: " + str(row))
    print row


def create_response(image_path, success):
    return json.dumps({'transformedUrl': image_path, 'success': success}, separators=(',', ':'))


def write_transformed_image(image_transformed, homography, transform, good_enough_match, file_name, output_path,
                            result_writer):
    file_prefix = "~trans" if good_enough_match else "~bad"
    transformed_image = file_prefix + "~hom" + str(homography) + "~warp" + str(transform) + "~" + file_name
    image_path = join(output_path, transformed_image)
    cv2.imwrite(image_path, image_transformed)

    result = "good" if good_enough_match else "bad"
    logging.info("%s image: %s", result, transformed_image)
    # print_result(result_writer, 0, transformed_image, homography, transform, result)
    return transformed_image


def register_image(file_path, reference_form_path, output_path, result_writer):
    reference = cv2.imread(reference_form_path, 0)
    logging.info("read reference %s", reference_form_path)
    orb = cv2.SIFT()
    kp2, des2 = orb.detectAndCompute(reference, None)

    image = cv2.imread(file_path, 0)
    logging.info("read uploaded image %s", file_path)
    kp1, des1 = orb.detectAndCompute(image, None)
    logging.info("detected orb")
    bf = cv2.BFMatcher(cv2.NORM_L2)
    raw_matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)
    logging.info("knn matched")
    matches = filter_matches(kp1, kp2, raw_matches)
    mkp1, mkp2 = zip(*matches)
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    logging.info("starting RANSAC")
    homography_transform, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    logging.info("RANSAC finished")
    homography, transform = check_homography(homography_transform)

    good_enough_match = check_match(homography, transform)

    h, w = reference.shape
    image_transformed = cv2.warpPerspective(image, homography_transform, (w, h))
    logging.info("transformed image")
    head, file_name = os.path.split(file_path)

    transformed_image = write_transformed_image(image_transformed, homography, transform, good_enough_match, file_name,
                                                output_path, result_writer)
    logging.info("transformed %s", transformed_image)
    return create_response(transformed_image, good_enough_match)


def process_file(result_writer, count, root, file_name):
    image_path = join(root + '/upload', file_name)
    reference_form_path = join(root, 'datasets/referenceform.jpg')
    output_path = join(root, 'transformed')
    return register_image(image_path, reference_form_path, output_path, result_writer)


def check_match(homography, transform):
    if homography < 0.01:
        return True
    if homography > 0.1:
        return False
    return transform < 0.1


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