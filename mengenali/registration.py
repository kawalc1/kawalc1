import numpy as np
import cv2
import os
import datetime
import math
import json

from os.path import join


def create_response(bad_image_file_name, success):
    return json.dumps({'transformedUrl': bad_image_file_name, 'success': success}, separators=(',', ':'))


def process_file(result_writer, count, root, file_name):
    reference = cv2.imread(join(root, 'datasets/referenceform.jpg'), 0)
    print >> result_writer, "read reference"
    orb = cv2.SIFT()
    kp2, des2 = orb.detectAndCompute(reference, None)

    image = cv2.imread(join(root + '/upload', file_name), 0)
    print >> result_writer, "read upload"
    kp1, des1 = orb.detectAndCompute(image, None)
    print >> result_writer, "detected orb"
    bf = cv2.BFMatcher(cv2.NORM_L2)
    raw_matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)
    print >> result_writer, "knn matched"
    matches = filter_matches(kp1, kp2, raw_matches)
    mkp1, mkp2 = zip(*matches)
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    print >> result_writer, "starting RANSAC"
    homography_transform, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    print >> result_writer, "RANSAC finished"
    homography, transform = check_homography(homography_transform)

    good_enough_match = check_match(homography, transform)

    h, w = reference.shape
    image_transformed = cv2.warpPerspective(image, homography_transform, (w, h))
    print >> result_writer, "transformed image"
    if good_enough_match:
        # save the images
        head, tail = os.path.split(file_name)
        #transformed image
        good_image_file_name = "~trans~hom" + str(homography) + "~warp" + str(transform) + "~" + tail
        good_image = join(root + '/transformed', good_image_file_name)
        cv2.imwrite(good_image, image_transformed)
        print >> result_writer, "good image"
        print_result(result_writer, count, good_image, homography, transform, "good")
        return create_response(good_image_file_name, True)
    else:
        head, tail = os.path.split(file_name)
        bad_image_file_name = "~bad~hom" + str(homography) + "~warp" + str(transform) + "~" + tail
        bad_image = join(root + '/transformed', bad_image_file_name)
        cv2.imwrite(bad_image, image_transformed)
        print >> result_writer, "bad image"
        print_result(result_writer, count, bad_image, homography, transform, "bad")
        return create_response(bad_image_file_name, False)


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
        #do the check
        trans = np.dot(test, homography_transform)
        #print trans
        dist1 = math.sqrt(math.pow(trans[0, 0] - trans[2, 0], 2) + math.pow(trans[0, 1] - trans[2, 1], 2))
        dist2 = math.sqrt(math.pow(trans[1, 0] - trans[3, 0], 2) + math.pow(trans[1, 1] - trans[3, 1], 2))

        measure = math.fabs((dist1 / dist2) - 1) - math.fabs((dist2 / dist1) - 1)
        absolute_measure = math.fabs(measure)
        return homography, absolute_measure
    else:
        return homography, 0


def print_result(result_writer, iteration, file_name, homography, transform, result):
    row = [str(iteration), file_name, str(datetime.datetime.now()), homography, transform, result]
    print >> result_writer, "output: " + str(row)
    print row
