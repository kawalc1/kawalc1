import cv2
from cv2.cv import *
# from cv2.highgui import *
isColor = 1
fps = 25
frameW = 1280  # images width
frameH = 720  # images height


writer = cv2.VideoWriter("video.avi", cv2.cv.CV_FOURCC('X', 'V', 'I', 'D'), fps, (frameW, frameH), True)

nFrames = 7000;  # number of frames
for i in range(nFrames):
    digit_image = "C:/temp/pilpres-recog/movie/" + "{0:0>5}".format(i) + ".png"
    print(digit_image)
    img = cv2.imread(digit_image)  # specify filename and the extension
    # add the frame to the video
    writer.write(img)

writer.release()
