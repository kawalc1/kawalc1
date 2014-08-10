import numpy as np
import cv2
import os.path
from PIL import ImageFilter
from PIL import Image
from scipy import ndimage
from os.path import join
import json

def getBoundingBox(ar,index):
    indices=np.where(ar == index)
    maxy=np.max(indices[0])
    miny=np.min(indices[0])
    maxx=np.max(indices[1])
    minx=np.min(indices[1])
    return maxy,miny,maxx,minx

def getAvgBorderDistance(ar,index):
    indices=np.where(ar == index)
    xs=indices[0]
    ys=indices[1]
    w,h=ar.shape
    bpix=0.0;
    for idx0,idx1 in zip(xs,ys):
        if idx0<2 or idx0>w-2 or idx1<2 or idx1>h-2:
            bpix=bpix+1
    return bpix/float(len(xs))    


def processImage(cropped):
    h, w = cropped.shape
    if h > w:
        pil_im = Image.fromarray(cropped)
        mnistsize = int((22.0 / h) * w), 22
        test_im = pil_im.resize(mnistsize, Image.ANTIALIAS)
        #now place the image into a 28x28 array
        outputim = Image.fromarray(np.zeros((28, 28)))
        left = int((28 - mnistsize[0])) / 2
        box = left, 3
        outputim.paste(test_im, box)
    else:
        pil_im = Image.fromarray(cropped)
        mnistsize = 22, int((22.0 / w) * h)
        test_im = pil_im.resize(mnistsize, Image.ANTIALIAS)
        #now place the image into a 28x28 array
        outputim = Image.fromarray(np.zeros((28, 28)))
        top = int((28 - mnistsize[1])) / 2
        box = 3, top
        #digits[i]=np.array(outputim)
        outputim.paste(test_im, box)


def processSignature(signatures, structuring_element, i, signature):
    ret, thresholded = cv2.threshold(signature, 180, 1, type=cv2.THRESH_BINARY_INV)
    signatures[i], nrOfObjects = ndimage.measurements.label(thresholded, structuring_element)
    #determine the sizes of the objects
    sizes = np.bincount(np.reshape(signatures[i], -1))
    selectedObject = -1
    maxSize = 0
    for j in range(1, nrOfObjects + 1):
        if sizes[j]<11:
            continue #this is too small to be a number
        maxy,miny,maxx,minx=getBoundingBox(signatures[i],j)
        if (maxy-miny < 3 and (miny<2 or maxy>59) ) or (maxx-minx < 3 and (minx<2 or maxx>25)):
            continue #this is likely a border artifact
        borderdist=getAvgBorderDistance(signatures[i],j)
        #print borderdist
        if(borderdist>0.2):
            continue #this is likely a border artifact
        
        if sizes[j] > maxSize:
            maxSize=sizes[j]
            selectedObject=j
    return (selectedObject != -1)


def prepareResults(images):
    results = [] 
    for i in range(0, len(images)):
        entry = {}
        entry["index"] = i
        entry["filename"] = 'img/empty.png'
        results.append(entry)
    return results
    


def extract(file, targetpath):
    image = Image.open(join(targetpath, file))
    image.load()
    outputdir = join(targetpath, 'extracted')

    pil_im=image.filter(ImageFilter.UnsharpMask(radius=15,percent=350,threshold=3))

    image=np.array(pil_im)
        
    #cut out the digits 
    digits=[image[261:323,693:721],
    image[261:323,726:754],
    image[261:323,759:787],
    image[327:389,693:721],
    image[327:389,726:754],
    image[327:389,759:787],
    image[395:457,693:721],
    image[395:457,726:754],
    image[395:457,759:787],
    image[463:525,693:721],
    image[463:525,726:754],
    image[463:525,759:787]]

    signatures=[image[930:974,594:749],image[976:1020,594:749]]

    #save the digits
    head, tail = os.path.split(file)
    tailPart, ext = os.path.splitext(tail)

    #create atructureing element for the connected component analysis
    s = [[1,1,1],[1,1,1],[1,1,1]]

    for i, digit in enumerate(digits):
        ret, thresholded=cv2.threshold(digit,180,1,type=cv2.THRESH_BINARY_INV)

        #do connected component analysis
        digits[i], nrOfObjects=ndimage.measurements.label(thresholded,s)
        #determine the sizes of the objects
        sizes=np.bincount(np.reshape(digits[i],-1))
        selectedObject=-1
        maxSize=0
        for j in range(1,nrOfObjects+1):
            if sizes[j]<11:
                continue #this is too small to be a number
            maxy,miny,maxx,minx=getBoundingBox(digits[i],j)
            if (maxy-miny < 3 and (miny<2 or maxy>59) ) or (maxx-minx < 3 and (minx<2 or maxx>25)):
                continue #this is likely a border artifact
            borderdist=getAvgBorderDistance(digits[i],j)
            #print borderdist
            if(borderdist>0.2):
                continue #this is likely a border artifact
            
            if sizes[j] > maxSize:
                maxSize=sizes[j]
                selectedObject=j
            
        if selectedObject==-1:
            digits[i]=None
            continue

        loc = ndimage.find_objects(digits[i])[selectedObject-1]
        cropped=digits[i][loc]
        #replace the shape number by 255
        cropped[cropped==selectedObject]=255

        processImage(cropped)
            #digits[i]=np.array(outputim)
    signatureResult = []
    signatureResult = prepareResults(signatures)
    for i, signature in enumerate(signatures):
        isValid = processSignature(signatures, s, i, signature)
        signatureFile = tailPart + "~sign~" + str(i) + ".jpg"
        extracted = join(outputdir, signatureFile)
        cv2.imwrite(extracted, signature)
        signatureResult[i]["filename"] = 'extracted/' + signatureFile
        signatureResult[i]["isValid"] = isValid
                #return False

           
    digitResult = prepareResults(digits)
    for i, digit in enumerate(digits):
        if digit is not None:
            #if isPossiblyCross(digit) and not isMinus(digit) :
            #digitFile = tailPart + "~" + str(i) + ".tif"
            digitFile = tailPart + "~" + str(i) + ".jpg"
            extracted = join(outputdir, digitFile)
            cv2.imwrite(extracted,digit)
            digitResult[i]["filename"] = 'extracted/' + digitFile
    
    result = {}
    result["digits"] = digitResult
    result["signatures"] = signatureResult
    print >> None, result
    
    
    return json.dumps(result)