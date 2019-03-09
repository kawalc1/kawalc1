import argparse
import pickle

import cv2


def convert_key_points(keypoints, descriptors):
    key_point_array = []
    for i, point in enumerate(keypoints):
        temp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id, descriptors[i])
        key_point_array.append(temp)
    return key_point_array


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="Path to the image", default="./static/datasets/plano-C1-2019-reference.jpg")
args = vars(ap.parse_args())

image_path = args["image"]
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
scale = 1.0
img = cv2.resize(img, None, fx=scale, fy=scale)
brisk = cv2.BRISK_create()
ref_kp, ref_descriptors = brisk.detectAndCompute(img, None)

keypoint_array = convert_key_points(ref_kp, ref_descriptors)
print(img.shape)
w, h = img.shape

pickle.dump({'keypoints': keypoint_array, 'h': h, 'w': w}, open(image_path.replace('.jpg', '.p'), "wb"))
