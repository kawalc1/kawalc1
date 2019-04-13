import os
import unittest

import cv2

from kawalc1 import settings
from mengenali import imageclassifier
from mengenali.extraction import unsharp_image, pre_process_digits, select_digits, extract_biggest_box
from mengenali.io import read_image
from mengenali.partyclassifier import detect_party
from tests import setup_django_settings
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt


class ExtractFromBoxes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_django_settings()

    def test_detect_party_pdi(self):
        party_file = 'toomuch.jpg'
        reference_form_path = f'./resources/forms/original/{party_file}'
        digit = read_image(reference_form_path)
        cv2.imshow("kak", digit)
        cv2.waitKey(0)
        unsharpened_image = unsharp_image(digit)
        cv2.imshow("kak", unsharpened_image)
        cv2.waitKey(0)

        structuring_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        cut_numbers = []
        cut_numbers.append(unsharpened_image)

        select_digits(cut_numbers, True, structuring_element)
        digit_image = cut_numbers[0]
        cv2.imshow("kak", digit_image)
        cv2.waitKey(0)

        image_threshold = 128
        ret, thresholded_tif = cv2.threshold(digit_image.astype(np.uint8), image_threshold, 255, type=cv2.THRESH_BINARY)
        neural_net_path = os.path.join('../', settings.STATIC_DIR, "datasets/C1TrainedNet.xml")
        print(os.path.abspath(neural_net_path))
        order, layers = imageclassifier.parse_network(neural_net_path)
        classified = imageclassifier.classify_number_in_memory(thresholded_tif, order, layers)
        probs = classified[0]
        max_value = max(probs)

        print(classified)
        cv2.imshow("kak", digit_image)
        cv2.waitKey(0)

    def test_wide_box(self):

        # party_file = '0-2-pure.jpg'
        # reference_form_path = f'./resources/numbers/set1/{party_file}'
        base_folder = './resources/numbers/set4/bad/'
        for file_name in cv2.os.listdir(base_folder):
            reference_form_path = f'{base_folder}{file_name}'
            digit = read_image(reference_form_path)
            plt.imshow(digit)
            plt.waitforbuttonpress()

            image = extract_biggest_box(digit)
            plt.imshow(image)
            plt.waitforbuttonpress()
            # cv2.imshow("kak", image)
            # cv2.waitKey(0)

        party_file = '4-13-pure.jpg'
        # Thresholding the image


        # measurements.append((int(ob[0].stop - ob[0].start), int(ob[1].stop - ob[1].start)))



        # ndimage.measurements.extrema()
        # print("measurements", measurements)

        # for i, j in enumerate(blobs):
        #     print(i, " size ", sizes[i])
        #     plt.imsave('blob' + str(i) + '.png', new_image[j])

        # for j in range(1, nr_of_objects + 1):
        #     print(j, " size ", sizes[j])
        #     loc = ndimage.find_objects(new_image)[j - 1]
        #     print(str(loc))
        #     cropped = new_image[loc]
        #     plt.imsave("kak" + str(j) + ".png", cropped)
            # cv2.imshow("kak", cropped)
            # cv2.waitKey(0)

        # Find contours for image, which will detect all the boxes
        # im2, contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort all the contours by top to bottom.
        # cv2.drawContours()

    def extract_biggest_box(self, reference_form_path, show_steps = False):
        digit = read_image(reference_form_path)
        if show_steps:
            cv2.imshow("kak", digit)
            cv2.waitKey(0)
        (thresh, img_bin) = cv2.threshold(digit, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        if show_steps:
            cv2.imshow("kak", img_bin)
            cv2.waitKey(0)
        img_bin = 255 - img_bin
        if show_steps:
            cv2.imshow("kak", img_bin)
            cv2.waitKey(0)
        # Defining a kernel length
        kernel_length = np.array(digit).shape[1] // 10
        # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
        verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
        # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
        hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
        # A kernel of (3 X 3) ones.
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # Morphological operation to detect vertical lines from an image
        img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
        verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
        if show_steps:
            cv2.imshow("kak", verticle_lines_img)
            cv2.waitKey(0)
        # Morphological operation to detect horizontal lines from an image
        img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
        horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
        if show_steps:
            cv2.imshow("kak", horizontal_lines_img)
            cv2.waitKey(0)
        # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
        alpha = 0.5
        beta = 1.0 - alpha
        # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
        img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
        img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
        (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        if show_steps:
            cv2.imshow("kak", img_final_bin)
            cv2.waitKey(0)
        structuring_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        new_image, nr_of_objects = ndimage.measurements.label(img_final_bin, structuring_element)
        if show_steps:
            plt.imsave("kak.png", new_image)
            # determine the sizes of the objects
            cv2.imshow("kak", new_image)
            cv2.waitKey(0)
        # sizes = np.bincount(np.reshape(new_image, -1).astype(np.int64))
        selected_object = -1
        max_size = 0
        blobs = ndimage.find_objects(new_image)
        measurements = []
        biggest_surface = 0
        biggest_feature = -1
        for i, ob in enumerate(blobs):
            slice_x, slice_y = blobs[i]
            width = slice_x.stop - slice_x.start
            height = slice_y.stop - slice_y.start
            surface = width * height
            if surface > biggest_surface:
                biggest_surface = surface
                biggest_feature = i
            print("ob " + str(i) + " " + str(ob) + " opp " + str(surface))
        slice_x, slice_y = blobs[biggest_feature]
        roi = digit[slice_x, slice_y]
        return roi