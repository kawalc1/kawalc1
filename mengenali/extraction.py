import numpy as np
import cv2
import os.path
from PIL import ImageFilter
from PIL import Image
from scipy import ndimage
from os.path import join
import json
import imageclassifier
import settings
import logging


def get_bounding_box(ar, index):
    indices = np.where(ar == index)
    maxy = np.max(indices[0])
    miny = np.min(indices[0])
    maxx = np.max(indices[1])
    minx = np.min(indices[1])
    return maxy, miny, maxx, minx


def get_avg_border_distance(ar, index):
    indices = np.where(ar == index)
    xs = indices[0]
    ys = indices[1]
    w, h = ar.shape
    bpix = 0.0
    for idx0, idx1 in zip(xs, ys):
        if idx0 < 2 or idx0 > w - 2 or idx1 < 2 or idx1 > h - 2:
            bpix += 1
    return bpix / float(len(xs))


def process_image(cropped):
    h, w = cropped.shape
    if h > w:
        pil_im = Image.fromarray(cropped)
        mnist_size = int((22.0 / h) * w), 22
        test_im = pil_im.resize(mnist_size, Image.ANTIALIAS)
        # now place the image into a 28x28 array
        output_image = Image.fromarray(np.zeros((28, 28)))
        left = int((28 - mnist_size[0])) / 2
        box = left, 3
        output_image.paste(test_im, box)
        return output_image
    else:
        pil_im = Image.fromarray(cropped)
        mnist_size = 22, int((22.0 / w) * h)
        test_im = pil_im.resize(mnist_size, Image.ANTIALIAS)
        # now place the image into a 28x28 array
        output_image = Image.fromarray(np.zeros((28, 28)))
        top = int((28 - mnist_size[1])) / 2
        box = 3, top
        # digits[i]=np.array(outputim)
        output_image.paste(test_im, box)
        return output_image


def process_signature(signatures, structuring_element, i, signature):
    ret, thresholded = cv2.threshold(signature, 180, 1, type=cv2.THRESH_BINARY_INV)
    signatures[i], number_of_objects = ndimage.measurements.label(thresholded, structuring_element)
    # determine the sizes of the objects
    sizes = np.bincount(np.reshape(signatures[i], -1))
    selected_object = -1
    maxsize = 0
    for j in range(1, number_of_objects + 1):
        if sizes[j] < 11:
            continue  # this is too small to be a number
        maxy, miny, maxx, minx = get_bounding_box(signatures[i], j)
        if (maxy - miny < 3 and (miny < 2 or maxy > 59)) or (maxx - minx < 3 and (minx < 2 or maxx > 25)):
            continue  # this is likely a border artifact
        borderdist = get_avg_border_distance(signatures[i], j)
        # print borderdist
        if borderdist > 0.2:
            continue  # this is likely a border artifact

        if sizes[j] > maxsize:
            maxsize = sizes[j]
            selected_object = j
    return selected_object != -1


def prepare_results(images):
    results = []
    for i in range(0, len(images)):
        entry = {"index": i, "filename": 'img/empty.png'}
        results.append(entry)
    return results


def unsharp_image(directory, file_name):
    image = Image.open(join(directory, file_name))
    image.load()
    pil_im = image.filter(ImageFilter.UnsharpMask(radius=15, percent=350, threshold=3))
    sharpened_image = np.array(pil_im)
    return sharpened_image


def cut_digits(unsharpened_image):
    return [unsharpened_image[261:323, 693:721],
            unsharpened_image[261:323, 726:754],
            unsharpened_image[261:323, 759:787],
            unsharpened_image[327:389, 693:721],
            unsharpened_image[327:389, 726:754],
            unsharpened_image[327:389, 759:787],
            unsharpened_image[395:457, 693:721],
            unsharpened_image[395:457, 726:754],
            unsharpened_image[395:457, 759:787],
            unsharpened_image[463:525, 693:721],
            unsharpened_image[463:525, 726:754],
            unsharpened_image[463:525, 759:787]]


def pre_process_digits(digits, structuring_element, filter_invalids=True):
    for i, digit in enumerate(digits):
        ret, thresholded = cv2.threshold(digit, 180, 1, type=cv2.THRESH_BINARY_INV)

        # do connected component analysis
        digits[i], nr_of_objects = ndimage.measurements.label(thresholded, structuring_element)
        # determine the sizes of the objects
        sizes = np.bincount(np.reshape(digits[i], -1))
        selected_object = -1
        max_size = 0
        for j in range(1, nr_of_objects + 1):
            if sizes[j] < 11:
                if filter_invalids:
                    continue  # this is too small to be a number
            maxy, miny, maxx, minx = get_bounding_box(digits[i], j)
            if (maxy - miny < 3 and (miny < 2 or maxy > 59)) or (maxx - minx < 3 and (minx < 2 or maxx > 25)):
                if filter_invalids:
                    continue  # this is likely a border artifact
            border_dist = get_avg_border_distance(digits[i], j)
            # print borderdist
            if border_dist > 0.2:
                if filter_invalids:
                    continue  # this is likely a border artifact

            if sizes[j] > max_size:
                max_size = sizes[j]
                selected_object = j

        if selected_object == -1 and filter_invalids:
            digits[i] = None
            continue

        if selected_object == -1 and not filter_invalids:
            loc = (slice(25L, 42L, None), slice(8L, 13L, None))
        else:
            loc = ndimage.find_objects(digits[i])[selected_object - 1]

        cropped = digits[i][loc]

        # replace the shape number by 255
        cropped[cropped == selected_object] = 255

        output_image = process_image(cropped)
        digits[i] = np.array(output_image)


def extract(file_name, source_path, target_path, dataset_path):
    digit_image = unsharp_image(source_path, file_name)

    signatures = [digit_image[932:972, 597:745], digit_image[977:1018, 597:745]]
    head, tail = os.path.split(file_name)
    full_file_name, ext = os.path.splitext(tail)
    base_file_name = full_file_name.split('~')[-1]

    # save
    digit_area_file = base_file_name + "~digit-area.jpg"
    digit_area_path = join(target_path, digit_area_file)
    logging.warning("writing %s", digit_area_path)
    # logging.warning("image %s", digit_araea)
    cv2.imwrite(digit_area_path, digit_image[258:527, 621:799])

    # create structureing element for the connected component analysis
    structuring_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    digits = cut_digits(digit_image)
    pre_process_digits(digits, structuring_element)
    signature_result = prepare_results(signatures)

    for i, signature in enumerate(signatures):
        is_valid = process_signature(signatures, structuring_element, i, signature)
        signature_file = base_file_name + "~sign~" + str(i) + ".jpg"
        extracted = join(target_path, signature_file)
        cv2.imwrite(extracted, signature)
        signature_result[i]["filename"] = 'extracted/' + signature_file
        signature_result[i]["isValid"] = is_valid
        # return False

    digit_result = prepare_results(digits)

    order, layers = imageclassifier.parse_network(join(dataset_path, "datasets/C1TrainedNet.xml"))
    probmatrix = np.ndarray(shape=(12, settings.CATEGORIES_COUNT), dtype='f')

    for i, digit in enumerate(digits):
        if digit is not None:
            digit_file = base_file_name + "~" + str(i) + ".jpg"
            extracted = join(target_path, digit_file)
            cv2.imwrite(extracted, digit)

            ret, thresholded_tif = cv2.threshold(digit, 128, 255, type=cv2.THRESH_BINARY)
            digit_tif = base_file_name + "~" + str(i) + ".tif"
            extracted_tif = join(target_path, digit_tif)
            cv2.imwrite(extracted_tif, thresholded_tif)
            probmatrix[i] = imageclassifier.classify_number(extracted_tif, order, layers)

            digit_result[i]["filename"] = 'extracted/' + digit_file

    result = {"digits": digit_result, "digitArea": 'extracted/' + digit_area_file, "signatures": signature_result,
              "probabilities": probmatrix.tolist()}
    logging.info(result)

    return json.dumps(result)