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
from kawalc1.settings import TRANSFORMED_DIR
from mengenali.io import write_image, read_image, image_url, is_url

logging.basicConfig(level=logging.DEBUG)


def print_result(result_writer, iteration, homography, transform, result):
    row = [str(iteration), str(datetime.datetime.now()), homography, transform, result]
    logging.info("output: " + str(row))
    print(row)


def create_response(image_path, success, hash, similarity):
    transformed_path = path.join(TRANSFORMED_DIR, 'transformed', image_path)
    return json.dumps(
        {'transformedUrl': image_url(transformed_path), 'transformedUri': transformed_path,
         'similarity': similarity, 'hash': str(hash), 'success': success},
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
                            target_path, store_files=True) -> str:
    file_prefix = "~trans" if good_enough_match else "~bad"
    transformed_image: str = get_target_path(file_path, target_path)

    image_path = join(output_path, transformed_image)

    if store_files:
        write_image(image_path, image_transformed)

    result = "good" if good_enough_match else "bad"
    logging.info("%s image", result)
    return transformed_image


def unpickle_keypoints(array):
    keypoints = []
    descriptors = []
    for point in array:
        temp_feature = cv2.KeyPoint(x=point[0][0], y=point[0][1], size=point[1], angle=point[2], response=point[3],
                                    octave=point[4], class_id=point[5])
        temp_descriptor = point[6]
        keypoints.append(temp_feature)
        descriptors.append(temp_descriptor)
    return keypoints, np.array(descriptors)


def read_descriptors(reference_form_path, algorithm):
    with open(reference_form_path.replace('.jpg', f'.{algorithm}.p'), "rb") as pickled:
        return pickle.load(pickled)


# https://www.pyimagesearch.com/2017/11/27/image-hashing-opencv-python/
def dhash(image, hashSize=8):
    resized = cv2.resize(image, (hashSize + 1, hashSize))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


# def register_image_sift(file_path, reference_form_path, output_path, result_writer, target_path=""):
#     from datetime import datetime
#     lap = datetime.now()
#
#     reference = read_image(reference_form_path)
#     logging.info("read reference %s", reference_form_path)
#     sift = cv2.xfeatures2d.SIFT_create()
#     ref_kp, ref_descriptors = sift.detectAndCompute(reference, None)
#
#
#
#     logging.info("SIFT reference %s", (datetime.now() - lap).total_seconds())
#     lap = datetime.now()
#
#     image = read_image(file_path)
#     logging.info("image read %s", (datetime.now() - lap).total_seconds())
#     lap = datetime.now()
#
#     difference_hash = dhash(image)
#     similarity = 0.0
#     try:
#         im_kp, im_descriptors = sift.detectAndCompute(cv2.resize(image, None, fx=1.0, fy=1.0), None)
#         logging.info("SIFT image %s", (datetime.now() - lap).total_seconds())
#         lap = datetime.now()
#
#         bf = cv2.BFMatcher(cv2.NORM_L2)
#         raw_matches = bf.knnMatch(im_descriptors, trainDescriptors=ref_descriptors, k=2)
#         logging.info("knn matched %s", (datetime.now() - lap).total_seconds())
#         lap = datetime.now()
#
#         amount, matches = filter_matches_with_amount(im_kp, ref_kp, raw_matches)
#         mkp1, mkp2 = zip(*matches)
#         logging.warning("matches %s", matches.__sizeof__())
#
#         # show_match(im_kp, image, raw_matches, ref_kp, reference_form_path)
#
#         p1 = np.float32([kp.pt for kp in mkp1])
#         p2 = np.float32([kp.pt for kp in mkp2])
#
#         homography_transform, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
#
#         logging.info("RANSAC  %s", (datetime.now() - lap).total_seconds())
#         lap = datetime.now()
#
#         homography, transform = check_homography(homography_transform)
#
#         # good_enough_match = check_match(homography, transform)
#         good_enough_match = True
#
#         h, w = reference.shape
#         image_transformed = cv2.warpPerspective(image, homography_transform, (w, h))
#         logging.info("transformed image %s, %s", file_path, (datetime.now() - lap).total_seconds())
#         lap = datetime.now()
#
#         tr_kp, tr_descriptors = sift.detectAndCompute(image_transformed, None)
#         tr_raw_matches = bf.knnMatch(tr_descriptors, trainDescriptors=ref_descriptors, k=2)
#         tr_amount, tr_matches_filtered = filter_matches_with_amount(tr_kp, ref_kp, tr_raw_matches)
#         trkp1, trkp2 = zip(*tr_matches_filtered)
#         similarity = feature_similarity(trkp1, trkp2) if tr_amount > 0 else -1
#
#         transformed_image = write_transformed_image(image_transformed, homography, transform, good_enough_match,
#                                                     file_path,
#                                                     output_path, target_path)
#         logging.info("transformed %s, %s", transformed_image, (datetime.now() - lap).total_seconds())
#         return create_response(transformed_image, good_enough_match, difference_hash, similarity)
#     except Exception as e:
#         logging.exception("Registration failed")
#         return json.dumps(
#             {'transformedUrl': None,
#              'transformedUri': None,
#              'similarity': -1.0,
#              'hash': str(difference_hash), 'success': False},
#             separators=(',', ':'))


def register_image_akaze(file_path, reference_form_path, output_path, result_writer, target_path="", store_files=True):
    from datetime import datetime
    lap = datetime.now()

    key_points = read_descriptors(reference_form_path, "akaze")
    ref_kp, ref_descriptors = unpickle_keypoints(key_points['keypoints'])
    h = key_points['h']
    w = key_points['w']

    akaze = cv2.AKAZE_create()

    logging.info("AKAZE reference %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    image = read_image(file_path)
    logging.info("image read %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    difference_hash = dhash(image)
    similarity = 0.0
    try:
        im_kp, im_descriptors = akaze.detectAndCompute(image, None)
        logging.info("AKAZE image %s", (datetime.now() - lap).total_seconds())
        lap = datetime.now()

        bf = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        raw_matches = bf.knnMatch(im_descriptors, trainDescriptors=ref_descriptors, k=2)
        logging.info("knn matched %s", (datetime.now() - lap).total_seconds())
        lap = datetime.now()

        amount, matches = filter_matches_with_amount(im_kp, ref_kp, raw_matches)
        mkp1, mkp2 = zip(*matches)
        logging.warning("matches %s", matches.__sizeof__())

        # show_match(im_kp, image, raw_matches, ref_kp, reference_form_path)

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

        tr_kp, tr_descriptors = akaze.detectAndCompute(image_transformed, None)
        tr_raw_matches = bf.knnMatch(tr_descriptors, trainDescriptors=ref_descriptors, k=2)
        tr_amount, tr_matches_filtered = filter_matches_with_amount(tr_kp, ref_kp, tr_raw_matches)
        trkp1, trkp2 = zip(*tr_matches_filtered)
        similarity = feature_similarity(trkp1, trkp2) if tr_amount > 0 else -1

        transformed_image = write_transformed_image(image_transformed, homography, transform, good_enough_match,
                                                    file_path,
                                                    output_path, target_path, store_files)
        logging.info("transformed %s, %s", transformed_image, (datetime.now() - lap).total_seconds())
        return create_response(transformed_image, good_enough_match, difference_hash, similarity), image_transformed
    except Exception as e:
        logging.exception("Registration failed")
        return json.dumps(
            {'transformedUrl': None,
             'transformedUri': None,
             'similarity': -1.0,
             'hash': str(difference_hash), 'success': False},
            separators=(',', ':'))


def register_image_brisk(file_path, reference_form_path, output_path, result_writer, target_path=""):
    from datetime import datetime
    lap = datetime.now()
    key_points = read_descriptors(reference_form_path, "brisk")
    ref_kp, ref_descriptors = unpickle_keypoints(key_points['keypoints'])
    h = key_points['h']
    w = key_points['w']

    logging.info("BRISK reference %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    image = read_image(file_path)
    logging.info("image read %s", (datetime.now() - lap).total_seconds())
    lap = datetime.now()

    difference_hash = dhash(image)
    similarity = 0.0
    try:

        brisk = cv2.BRISK_create()
        im_kp, im_descriptors = brisk.detectAndCompute(cv2.resize(image, None, fx=1.0, fy=1.0), None)
        logging.info("BRISK image %s", (datetime.now() - lap).total_seconds())
        lap = datetime.now()

        bf = cv2.BFMatcher(cv2.NORM_L2)
        raw_matches = bf.knnMatch(np.float32(im_descriptors), trainDescriptors=np.float32(ref_descriptors), k=2)
        logging.info("knn matched %s", (datetime.now() - lap).total_seconds())
        lap = datetime.now()

        amount, matches = filter_matches_with_amount(im_kp, ref_kp, raw_matches)
        mkp1, mkp2 = zip(*matches)
        logging.warning("matches %s", matches.__sizeof__())


        # show_match(im_kp, image, raw_matches, ref_kp, reference_form_path)

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

        tr_kp, tr_descriptors = brisk.detectAndCompute(image_transformed, None)
        tr_raw_matches = bf.knnMatch(np.float32(tr_descriptors), trainDescriptors=np.float32(ref_descriptors), k=2)
        tr_amount, tr_matches_filtered = filter_matches_with_amount(tr_kp, ref_kp, tr_raw_matches)
        trkp1, trkp2 = zip(*tr_matches_filtered)
        similarity = feature_similarity(trkp1, trkp2) if tr_amount > 0 else -1

        transformed_image = write_transformed_image(image_transformed, similarity, transform, good_enough_match,
                                                    file_path,
                                                    output_path, target_path)
        logging.info("transformed %s, %s", transformed_image, (datetime.now() - lap).total_seconds())
        return create_response(transformed_image, good_enough_match, difference_hash, similarity), image_transformed
    except Exception as e:
        logging.exception("Registration failed")
        return json.dumps(
            {'transformedUrl': None,
             'transformedUri': None,
             'similarity': -1.0,
             'hash': str(difference_hash), 'success': False},
            separators=(',', ':'))


def show_match(im_kp, image, raw_matches, ref_kp, reference_form_path):
    reference = cv2.imread(reference_form_path, 0)
    img_match = np.empty((max(reference.shape[0], image.shape[0]), reference.shape[1] + image.shape[1], 3),
                         dtype=np.uint8)
    good = []
    for m, n in raw_matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])
    # img3 = cv2.drawMatchesKnn(image, im_kp, reference, ref_kp, matches, None, **draw_params)
    im_matches = cv2.drawMatchesKnn(img1=image, keypoints1=im_kp, img2=reference,
                                    keypoints2=ref_kp, matches1to2=good, outImg=img_match, matchColor=None,
                                    singlePointColor=(255, 255, 255), matchesMask=[], flags=2)
    factor = 0.5
    im_matches_small = cv2.resize(im_matches, None, fx=factor, fy=factor)
    cv2.imshow("match", im_matches_small)
    cv2.waitKey(0)


def process_file(result_writer, count, root, file_name, reference_form_path, config_file, feature_algorithm):
    image_path = join(root + '/upload', file_name)
    output_path = join(root, 'transformed')

    func = ""
    # if feature_algorithm == "akaze":
    #     func = register_image_akaze
    # if feature_algorithm == "sift":
    #     func = register_image_sift
    if feature_algorithm == "brisk":
        func = register_image_brisk
    return func(image_path, reference_form_path, output_path, result_writer, config_file)


def check_match(homography, transform):
    if homography < 0.05:
        return True
    return homography < 1.0 or transform < 0.3


def feature_similarity(mkp1, mkp2):
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
    return similarity


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
