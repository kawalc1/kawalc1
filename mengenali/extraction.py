import numpy as np
import cv2
import os.path
from PIL import ImageFilter
from PIL import Image
from scipy import ndimage
from os.path import join

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

def extract(file, targetpath):
    img1 = Image.open(join(targetpath, file))
    img1.load()
    pil_im=img1.filter(ImageFilter.UnsharpMask(radius=15,percent=350,threshold=3))
    #pil_im.show()
    
    outputdir = join(targetpath, 'extracted')

    img1=np.array(pil_im)
        
    #cut out the images 
    images=[img1[261:323,693:721],
    img1[261:323,726:754],
    img1[261:323,759:787],
    img1[327:389,693:721],
    img1[327:389,726:754],
    img1[327:389,759:787],
    img1[395:457,693:721],
    img1[395:457,726:754],
    img1[395:457,759:787],
    img1[463:525,693:721],
    img1[463:525,726:754],
    img1[463:525,759:787]]

    #save the images
    head, tail = os.path.split(file)
    tailPart, ext = os.path.splitext(tail)

    #create atructureing element for the connected component analysis
    s = [[1,1,1],[1,1,1],[1,1,1]]

    for i, im in enumerate(images):
        ret, thresholded=cv2.threshold(im,180,1,type=cv2.THRESH_BINARY_INV)

        #do connected component analysis
        images[i], nrOfObjects=ndimage.measurements.label(thresholded,s)
        #determine the sizes of the objects
        sizes=np.bincount(np.reshape(images[i],-1))
        selectedObject=-1
        maxSize=0
        for j in range(1,nrOfObjects+1):
            if sizes[j]<11:
                continue #this is too small to be a number
            maxy,miny,maxx,minx=getBoundingBox(images[i],j)
            if (maxy-miny < 3 and (miny<2 or maxy>59) ) or (maxx-minx < 3 and (minx<2 or maxx>25)):
                continue #this is likely a border artifact
            borderdist=getAvgBorderDistance(images[i],j)
            #print borderdist
            if(borderdist>0.2):
                continue #this is likely a border artifact
            
            if sizes[j] > maxSize:
                maxSize=sizes[j]
                selectedObject=j
            
        if selectedObject==-1:
            images[i]=None
            continue

        loc = ndimage.find_objects(images[i])[selectedObject-1]
        cropped=images[i][loc]
        #replace the shape number by 255
        cropped[cropped==selectedObject]=255

        h,w = cropped.shape
        if h > w:
            pil_im=Image.fromarray(cropped)
            mnistsize=int((22.0/h)*w), 22
            test_im=pil_im.resize(mnistsize, Image.ANTIALIAS)
            #now place the image into a 28x28 array
            outputim=Image.fromarray(np.zeros((28,28)))
            left=int((28-mnistsize[0]))/2
            box=(left,3)
            outputim.paste(test_im,box)
            images[i]=np.array(outputim)
        else:
            pil_im=Image.fromarray(cropped)
            mnistsize=22,int((22.0/w)*h)
            test_im=pil_im.resize(mnistsize, Image.ANTIALIAS)
            #now place the image into a 28x28 array
            outputim=Image.fromarray(np.zeros((28,28)))
            top=int((28-mnistsize[1]))/2
            box=(3,top)
            outputim.paste(test_im,box)
            images[i]=np.array(outputim)

    for i, im in enumerate(images):
        if im is not None:
            #if isPossiblyCross(im) and not isMinus(im) :
            tiffie = join(outputdir, tailPart + "~" + str(i) + ".tif")
            print tiffie
            cv2.imwrite(tiffie,im)
        
    return 'bla'