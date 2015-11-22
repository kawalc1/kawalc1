import argparse
import cv2
import cv2.ximgproc

parser = argparse.ArgumentParser()
parser.add_argument("-image", help="location of directory to traverse",
                    default="~/Downloads/metertje.jpg")

args = parser.parse_args()
input_image = args.image
img = cv2.imread(input_image)
cv2.imshow('image',img)
channels = []
cv2.ximgproc.create

cv2.waitKey(0)
cv2.destroyAllWindows()