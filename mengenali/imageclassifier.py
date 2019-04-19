import datetime
import logging

import numpy as np
import os.path
from PIL import Image
from scipy import ndimage
from lxml import etree
import time

from mengenali.io import read_image


def classify_number(input_file, order, layers):
    cv_image = read_image(input_file)
    classify_number_in_memory(cv_image, order, layers)


def classify_number_in_memory(cv_image, order, layers):
    input_image = Image.fromarray(cv_image)
    input_image = np.array(input_image.getdata()).reshape(input_image.size[0], input_image.size[1])
    input_image = input_image.astype(np.float32)
    input_image /= input_image.max()

    input_image = input_image.reshape((input_image.shape[0], input_image.shape[1], 1))

    # run through the layers
    first_fully_connected = True

    for layer_name, type in order:
        if type == 'conv':
            input_image = convolve_image_stack(input_image, layers[layer_name])
        elif type == 'pool':
            input_image = pool_image_stack(input_image, layers[layer_name])
        else:
            if first_fully_connected:
                input_image = np.swapaxes(input_image, 1, 2)
                input_image = np.swapaxes(input_image, 0, 1)
                input_image = input_image.flatten('C')
                first_fully_connected = False
            input_image = apply_fully_connected(input_image, layers[layer_name])

        #input image now contains the raw network output, apply softmax
    input_image = np.exp(input_image)
    sum = np.sum(input_image)
    out = input_image / sum

    return out


def classify_numbers(input_dir, order, layers):
    for file_name in os.listdir(input_dir):
        input_file = input_dir + "\\" + file_name;
        classify_number(input_file, order, layers)


def parse_network(network):
    xml_net = etree.parse(network)
    # store the layer info
    order = []
    layers = dict()
    for child in xml_net.getroot():
        if child.tag == "layer":
            tp = child.find('type')
            if tp is not None:
                logging.info(tp.text)
                nm = child.attrib['name']
                if tp.text == 'conv':
                    order.append((nm, tp.text))
                    layers[nm] = parse_convolution_layer(child)
                elif tp.text == 'pool':
                    order.append((nm, tp.text))
                    layers[nm] = parse_pool_layer(child)
                elif tp.text == 'fc':
                    order.append((nm, tp.text))
                    layers[nm] = parse_fully_connected_layer(child)

    return order, layers


start_time = time.time()

np.set_printoptions(precision=6)
np.set_printoptions(suppress=True)


def apply_relu_neuron(results):
    return np.maximum(results, np.zeros(results.shape))


def convolve_image_stack(inputim, params):
    channels, filters, filterSize, padding, dropout, neuron, bias, weights = params
    results = np.zeros((inputim.shape[0], inputim.shape[1], weights.shape[1]))
    for i, kernels in enumerate(weights.T):  # for each colum in weights
        filters = kernels.reshape((filterSize, filterSize, channels))
        for f in range(channels):
            tempres = ndimage.filters.convolve(inputim[:, :, f], filters[:, :, f], mode='constant', cval=0.0)
            results[:, :, i] += tempres
        results[:, :, i] += bias[i]
        results[:, :, i] *= (1.0 - dropout)

    if neuron == 'relu':
        return apply_relu_neuron(results)
    else:
        return results


def pool_image_stack(images, params):
    outputDim, filterSize, stride, operation, neuron = params
    results = np.zeros((outputDim, outputDim, images.shape[2]))
    for l in range(images.shape[2]):
        tempres = ndimage.filters.maximum_filter(images[:, :, l], size=(filterSize, filterSize))
        # determine offset
        offset = int(filterSize / 2.0)
        results[:, :, l] += tempres[offset::stride, offset::stride]

    if neuron == 'relu':
        return apply_relu_neuron(results)
    else:
        return results


def apply_fully_connected(images, params):
    dropout, neuron, bias, weights = params
    results = np.dot(images, weights) + bias

    if neuron == 'relu':
        results = apply_relu_neuron(results)

    results *= (1.0 - dropout)

    return results


def parse_convolution_layer(element):
    filters = int(element.findtext('filters'))
    filter_size = int(element.findtext('filterSize'))
    padding = int(element.findtext('padding'))
    dropout = float(element.findtext('dropout'))
    neuron = element.findtext('neuron')
    channels = int(element.findtext('channels'))

    # create ndarray to store the biases
    bias_element = element.find('biases')
    rows = int(bias_element.attrib['rows'])
    cols = int(bias_element.attrib['cols'])
    longlist = []
    for row in bias_element.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    bias = np.asarray(longlist)
    bias = bias.reshape(rows, cols)

    #create ndarray to store the weights
    weight_element = element.find('weights')
    rows = int(weight_element.attrib['rows'])
    cols = int(weight_element.attrib['cols'])
    longlist = []
    for row in weight_element.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    weights = np.asarray(longlist)
    weights = weights.reshape(rows, cols)

    #go over the weights to turn them into kernels
    for i, kernels in enumerate(weights.T):  #for each colum in weights
        filters = kernels.reshape((channels, filter_size, filter_size))
        for f in range(channels):
            filters[f, :, :] = np.fliplr(filters[f, :, :])
            filters[f, :, :] = np.flipud(filters[f, :, :])
        filters = np.swapaxes(filters, 0, 1)
        filters = np.swapaxes(filters, 1, 2)
        weights[:, i] = filters.reshape(-1).reshape(-1)

    return (channels, filters, filter_size, padding, dropout, neuron, bias,
            weights)  #should have made a class but too lazy to find out how


def parse_pool_layer(element):
    output_dimensions = element.findtext('outputsX')
    filter_size = element.findtext('sizeX')
    stride = element.findtext('stride')
    neuron = element.findtext('neuron')
    operation = element.findtext('pool')
    return int(output_dimensions), int(filter_size), int(stride), operation, neuron


def parse_fully_connected_layer(element):
    dropout = element.findtext('dropout')
    neuron = element.findtext('neuron')

    # create ndarray to store the biases
    bias_element = element.find('biases')
    rows = int(bias_element.attrib['rows'])
    cols = int(bias_element.attrib['cols'])
    longlist = []
    for row in bias_element.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    bias = np.asarray(longlist)
    bias = bias.reshape(rows, cols)

    #create ndarray to store the weights
    weight_element = element.find('weights')
    rows = int(weight_element.attrib['rows'])
    cols = int(weight_element.attrib['cols'])
    longlist = []
    for row in weight_element.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    weights = np.asarray(longlist)
    weights = weights.reshape(rows, cols)

    return float(dropout), neuron, bias, weights