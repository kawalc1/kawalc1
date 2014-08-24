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
    signatures[i], nrOfObjects = ndimage.measurements.label(thresholded, structuring_element)
    # determine the sizes of the objects
    sizes = np.bincount(np.reshape(signatures[i], -1))
    selected_object = -1
    maxsize = 0
    for j in range(1, nrOfObjects + 1):
        if sizes[j] < 11:
            continue  # this is too small to be a number
        maxy, miny, maxx, minx = get_bounding_box(signatures[i], j)
        if (maxy - miny < 3 and (miny < 2 or maxy > 59) ) or (maxx - minx < 3 and (minx < 2 or maxx > 25)):
            continue  # this is likely a border artifact
        borderdist = get_avg_border_distance(signatures[i], j)
        # print borderdist
        if borderdist > 0.2:
            continue  #this is likely a border artifact

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


def extract(file_name, targetpath):
    image = Image.open(join(targetpath, file_name))
    image.load()
    output_dir = join(targetpath, 'extracted')

    pil_im = image.filter(ImageFilter.UnsharpMask(radius=15, percent=350, threshold=3))

    image = np.array(pil_im)

    # cut out the digits
    digits = [image[261:323, 693:721],
              image[261:323, 726:754],
              image[261:323, 759:787],
              image[327:389, 693:721],
              image[327:389, 726:754],
              image[327:389, 759:787],
              image[395:457, 693:721],
              image[395:457, 726:754],
              image[395:457, 759:787],
              image[463:525, 693:721],
              image[463:525, 726:754],
              image[463:525, 759:787]]

    signatures = [image[932:972, 597:745], image[977:1018, 597:745]]

    # save the digits
    head, tail = os.path.split(file_name)
    tail_part, ext = os.path.splitext(tail)

    #create atructureing element for the connected component analysis
    s = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

    for i, digit in enumerate(digits):
        ret, thresholded = cv2.threshold(digit, 180, 1, type=cv2.THRESH_BINARY_INV)

        #do connected component analysis
        digits[i], nr_of_objects = ndimage.measurements.label(thresholded, s)
        #determine the sizes of the objects
        sizes = np.bincount(np.reshape(digits[i], -1))
        selected_object = -1
        max_size = 0
        for j in range(1, nr_of_objects + 1):
            if sizes[j] < 11:
                continue  #this is too small to be a number
            maxy, miny, maxx, minx = get_bounding_box(digits[i], j)
            if (maxy - miny < 3 and (miny < 2 or maxy > 59) ) or (maxx - minx < 3 and (minx < 2 or maxx > 25)):
                continue  #this is likely a border artifact
            border_dist = get_avg_border_distance(digits[i], j)
            #print borderdist
            if border_dist > 0.2:
                continue  #this is likely a border artifact

            if sizes[j] > max_size:
                max_size = sizes[j]
                selected_object = j

        if selected_object == -1:
            digits[i] = None
            continue

        loc = ndimage.find_objects(digits[i])[selected_object - 1]
        cropped = digits[i][loc]
        #replace the shape number by 255
        cropped[cropped == selected_object] = 255

        outputim = process_image(cropped)
        digits[i] = np.array(outputim)
    signature_result = prepare_results(signatures)
    for i, signature in enumerate(signatures):
        is_valid = process_signature(signatures, s, i, signature)
        signature_file = tail_part + "~sign~" + str(i) + ".jpg"
        extracted = join(output_dir, signature_file)
        cv2.imwrite(extracted, signature)
        signature_result[i]["filename"] = 'extracted/' + signature_file
        signature_result[i]["isValid"] = is_valid
        #return False

    digit_result = prepare_results(digits)

    order, layers = imageclassifier.parse_network(join(targetpath, "datasets/network10.xml"))
    orderx, layersx = imageclassifier.parse_network(join(targetpath, "datasets/network11.xml"))
    probmatrix = np.ndarray(shape=(12, settings.CATEGORIES_COUNT), dtype='f')

    #fill with 0 as most likely by default
    probmatrix.fill(0.001)
    for (x, y), element in np.ndenumerate(probmatrix):
        if y == 0:
            probmatrix[x, y] = 0.999

    for i, digit in enumerate(digits):
        if digit is not None:
            digit_file = tail_part + "~" + str(i) + ".jpg"
            extracted = join(output_dir, digit_file)
            cv2.imwrite(extracted, digit)

            ret, thresholded_tif = cv2.threshold(digit, 128, 255, type=cv2.THRESH_BINARY)
            digit_tif = tail_part + "~" + str(i) + ".tif"
            extracted_tif = join(output_dir, digit_tif)
            cv2.imwrite(extracted_tif, thresholded_tif)

            if imageclassifier.is_probably_x(extracted_tif, orderx, layersx):
                continue
            probmatrix[i] = imageclassifier.classify_number(extracted_tif, order, layers)

            digit_result[i]["filename"] = 'extracted/' + digit_file

    result = {"digits": digit_result, "signatures": signature_result, "probabilities": probmatrix.tolist()}
    print >> None, result

    return json.dumps(result)