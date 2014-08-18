import time

start_time = time.time()
import numpy as np
import cv2
import argparse
import os.path
import pickle
from PIL import Image
from scipy import ndimage
from lxml import etree

np.set_printoptions(precision=6)
np.set_printoptions(suppress=True)


def applyReluNeuron(results):
    return np.maximum(results, np.zeros(results.shape))


def convolveImageStack(inputim, (channels, filters, filterSize, padding, dropout, neuron, bias, weights)):
    results = np.zeros((inputim.shape[0], inputim.shape[1], weights.shape[1]))
    for i, kernels in enumerate(weights.T):  # for each colum in weights
        filters = kernels.reshape((filterSize, filterSize, channels))
        for f in range(channels):
            tempres = ndimage.filters.convolve(inputim[:, :, f], filters[:, :, f], mode='constant', cval=0.0)
            results[:, :, i] += tempres
        results[:, :, i] += bias[i]
        results[:, :, i] *= (1.0 - dropout)

    if neuron == 'relu':
        return applyReluNeuron(results)
    else:
        return results


def poolImageStack(images, (outputDim, filterSize, stride, operation, neuron)):
    results = np.zeros((outputDim, outputDim, images.shape[2]))
    for l in range(images.shape[2]):
        tempres = ndimage.filters.maximum_filter(images[:, :, l], size=(filterSize, filterSize))
        # determine offset
        offset = int(filterSize / 2.0)
        results[:, :, l] += tempres[offset::stride, offset::stride]

    if neuron == 'relu':
        return applyReluNeuron(results)
    else:
        return results


def applyFullyConnected(images, (dropout, neuron, bias, weights)):
    results = np.dot(images, weights) + bias

    if neuron == 'relu':
        results = applyReluNeuron(results)

    results *= (1.0 - dropout)

    return results


def parseConvLayer(element):
    filters = int(element.findtext('filters'))
    filterSize = int(element.findtext('filterSize'))
    padding = int(element.findtext('padding'))
    dropout = float(element.findtext('dropout'))
    neuron = element.findtext('neuron')
    channels = int(element.findtext('channels'))

    # create ndarray to store the biases
    biasel = element.find('biases')
    rows = int(biasel.attrib['rows'])
    cols = int(biasel.attrib['cols'])
    longlist = []
    for row in biasel.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    bias = np.asarray(longlist)
    bias = bias.reshape(rows, cols)

    #create ndarray to store the weights
    weightel = element.find('weights')
    rows = int(weightel.attrib['rows'])
    cols = int(weightel.attrib['cols'])
    longlist = []
    for row in weightel.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    weights = np.asarray(longlist)
    weights = weights.reshape(rows, cols)

    #go over the weights to turn them into kernels
    for i, kernels in enumerate(weights.T):  #for each colum in weights
        filters = kernels.reshape((channels, filterSize, filterSize))
        for f in range(channels):
            filters[f, :, :] = np.fliplr(filters[f, :, :])
            filters[f, :, :] = np.flipud(filters[f, :, :])
        filters = np.swapaxes(filters, 0, 1)
        filters = np.swapaxes(filters, 1, 2)
        weights[:, i] = filters.reshape(-1).reshape(-1)

    return (channels, filters, filterSize, padding, dropout, neuron, bias,
            weights)  #should have made a class but too lazy to find out how


def parsePoolLayer(element):
    outputDim = element.findtext('outputsX')
    filterSize = element.findtext('sizeX')
    stride = element.findtext('stride')
    neuron = element.findtext('neuron')
    operation = element.findtext('pool')
    return (int(outputDim), int(filterSize), int(stride), operation, neuron)


def parseFullyConnectedLayer(element):
    dropout = element.findtext('dropout')
    neuron = element.findtext('neuron')

    # create ndarray to store the biases
    biasel = element.find('biases')
    rows = int(biasel.attrib['rows'])
    cols = int(biasel.attrib['cols'])
    longlist = []
    for row in biasel.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    bias = np.asarray(longlist)
    bias = bias.reshape(rows, cols)

    #create ndarray to store the weights
    weightel = element.find('weights')
    rows = int(weightel.attrib['rows'])
    cols = int(weightel.attrib['cols'])
    longlist = []
    for row in weightel.iterfind('row'):
        longlist.extend([float(n) for n in row.text.split()])
    weights = np.asarray(longlist)
    weights = weights.reshape(rows, cols)

    return (float(dropout), neuron, bias, weights)

# setup the argument parser
parser = argparse.ArgumentParser()
parser.add_argument("inputdirectory", help="location of the image files")
parser.add_argument("networkparameters", help="the network file")
parser.add_argument("outputdir", help="The directory where the straightened form is dumped")
args = parser.parse_args()

inputdir = args.inputdirectory
network = args.networkparameters
outputdir = args.outputdir

#read the network data
xmlnet = etree.parse(network)

#store the layer info
order = []
layers = dict()

for child in xmlnet.getroot():
    if child.tag == "layer":
        tp = child.find('type')
        if tp == None:
            continue
        print tp.text
        nm = child.attrib['name']
        if tp.text == 'conv':
            order.append((nm, tp.text))
            layers[nm] = parseConvLayer(child)
        elif tp.text == 'pool':
            order.append((nm, tp.text))
            layers[nm] = parsePoolLayer(child)
        elif tp.text == 'fc':
            order.append((nm, tp.text))
            layers[nm] = parseFullyConnectedLayer(child)

#now we have the network in memory, start the convolution process
start_time = time.time()
for file in os.listdir(inputdir):

    if not file.endswith('.tif'):
        continue

    inputimage = Image.open(inputdir + "\\" + file)
    inputimage = np.array(inputimage.getdata()).reshape(inputimage.size[0], inputimage.size[1])

    inputimage = inputimage.astype(np.float32)

    inputimage /= inputimage.max()

    inputimage = inputimage.reshape((inputimage.shape[0], inputimage.shape[1], 1))

    #run through the layers
    firstFullyConnected = True
    for (layername, type) in order:
        if type == 'conv':
            inputimage = convolveImageStack(inputimage, layers[layername])
        elif type == 'pool':
            inputimage = poolImageStack(inputimage, layers[layername])
        else:
            if firstFullyConnected:
                inputimage = np.swapaxes(inputimage, 1, 2)
                inputimage = np.swapaxes(inputimage, 0, 1)
                inputimage = inputimage.flatten('C')
                firstFullyConnected = False
            inputimage = applyFullyConnected(inputimage, layers[layername])

    #input image now contains the raw network output, apply softmax
    inputimage = np.exp(inputimage)
    sum = np.sum(inputimage)
    out = inputimage / sum

    print file
    print out

print "The classification script took ", time.time() - start_time, " to run"