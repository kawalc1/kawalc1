import numpy as np
import cv2
import os
import datetime
import math
import json

from os.path import join



def createResponse(badImageFileName, success):
    return json.dumps({'transformedUrl':badImageFileName, 'success': success}, separators=(',', ':'))

def processFile(resultWriter, count, root, file):
    reference = cv2.imread(join(root, 'referenceform.jpg'),0)
    print >> resultWriter, "read reference"
    orb = cv2.SIFT()
    kp2, des2 = orb.detectAndCompute(reference,None)

    img1 = cv2.imread(join(root + '/upload', file), 0)
    print >> resultWriter, "read upload"
    kp1, des1 = orb.detectAndCompute(img1, None)
    print >> resultWriter, "detected orb"
    bf = cv2.BFMatcher(cv2.NORM_L2)
    raw_matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)
    print >> resultWriter, "knn matched"
    matches = filter_matches(kp1, kp2, raw_matches)
    mkp1, mkp2 = zip(*matches)
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    print >> resultWriter, "starting RANSAC"
    M, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    print >> resultWriter, "RANSAC finished"
    homography, transform = checkHomography(M)

    goodEnoughMatch = check_match(homography, transform)

    h, w = reference.shape
    imgTransformed = cv2.warpPerspective(img1, M, (w, h))
    print >> resultWriter, "transformed image"
    if (goodEnoughMatch):
    #save the images
        head, tail = os.path.split(file)
    #transformed image
        goodImageFileName = "~trans~hom" + str(homography) + "~warp" + str(transform) + "~" + tail
        goodImage = join(root + '/transformed', goodImageFileName)
        cv2.imwrite(goodImage, imgTransformed)
        print >> resultWriter, "good image"
        printResult(resultWriter, count, goodImage,  homography, transform, "good")
        return createResponse(goodImageFileName, True)
    else:
        head, tail = os.path.split(file)
        badImageFileName = "~bad~hom" + str(homography) + "~warp" +  str(transform) + "~" + tail
        badImage = join(root + '/transformed', badImageFileName)
        cv2.imwrite(badImage, imgTransformed)
        print >> resultWriter, "bad image"
        printResult(resultWriter, count, badImage, homography, transform, "bad")
        return createResponse(badImageFileName, False)

def check_match(homography, transform):
    if homography < 0.01 :
        return True
    return transform < 0.1

def filter_matches(kp1, kp2, matches, ratio = 0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
    kp_pairs = zip(mkp1, mkp2)
    return kp_pairs

def checkHomography(M):
    homography = abs(M[0,0]-M[1,1])
    if homography > 0.01:
        #test=np.array([[10,20,20,10],[10,10,20,20],[1,1,1,1]])
        test=np.array([[10,10,1],[20,10,1],[20,20,1],[10,20,1]])
        #do the check
        trans=np.dot(test,M)
        #print trans
        dist1=math.sqrt(math.pow(trans[0,0]-trans[2,0],2)+math.pow(trans[0,1]-trans[2,1],2))
        dist2=math.sqrt(math.pow(trans[1,0]-trans[3,0],2)+math.pow(trans[1,1]-trans[3,1],2))

        measure=math.fabs((dist1/dist2)-1)-math.fabs((dist2/dist1)-1)
        absmeasure = math.fabs(measure)
        return (homography, absmeasure)
    else:
        return (homography, 0)

def printResult(resultWriter, iteration, file, homography, transform, result) :
    row = [str(iteration), file, str(datetime.datetime.now()), homography, transform, result]
    print >> resultWriter, "output: " + str(row)
    #resultWriter.writerow(row)
    print row
