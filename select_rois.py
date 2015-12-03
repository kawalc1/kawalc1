# import the necessary packages
import argparse
import cv2
import scipy.misc

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
mouse_pos = (250, 250)
selecting = False
zoom_size = 250
zoom_factor = 2.0


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, selecting, mouse_pos, image

    if event == cv2.EVENT_MOUSEMOVE:
        mouse_pos = (x, y)
        if selecting and refPt.count is not 0:
            image = clone.copy()
            cv2.rectangle(image, refPt[0], (x, y), (0, 255, 0), 1)
            cv2.imshow("image", image)

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        selecting = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        selecting = False


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="Path to the image", default="./static/datasets/pilkada_reference.jpg")
args = vars(ap.parse_args())

# load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
clone = image.copy()
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)

cv2.namedWindow("zoom")
cv2.resizeWindow("zoom", zoom_size, zoom_size)
cv2.moveWindow("zoom", image.shape[1], 0)

# keep looping until the 'q' key is pressed
while True:
    # display the image and wait for a keypress
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    # if the 'r' key is pressed, reset the cropping region
    if key == ord("r"):
        image = clone.copy()

    # if the 'c' key is pressed, break from the loop
    elif key == ord("q"):
        break

    xpos = mouse_pos[0]
    ypos = mouse_pos[1]
    center = zoom_size / 2

    start_row = ypos - center
    end_row = ypos + zoom_size - center
    start_col = xpos - center
    end_col = xpos + zoom_size - center

    zoom_roi = image[max(start_row, 0):max(start_row, end_row), max(start_col, 0):max(start_col, end_col)]
    zoomed_image = scipy.misc.imresize(zoom_roi, zoom_factor)
    crosshair_size = 30
    zoomed_center = int(center * zoom_factor)
    cv2.line(zoomed_image, (zoomed_center, zoomed_center - crosshair_size),
             (zoomed_center, zoomed_center + crosshair_size), (0, 255, 0), 1)
    cv2.line(zoomed_image, (zoomed_center - crosshair_size, zoomed_center),
             (zoomed_center + crosshair_size, zoomed_center), (0, 255, 0), 1)
    cv2.imshow("zoom", zoomed_image)

    if key == ord("s") and len(refPt) == 2:
        print str(
            "[" + str(refPt[0][1]) + "," + str(refPt[1][1]) + ", " + str(refPt[0][0]) + "," + str(refPt[1][0]) + "]")
        roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
        cv2.imshow("ROI", roi)
        cv2.moveWindow("ROI", image.shape[1], int(zoom_size * zoom_factor) + 40)

# if there are two reference points, then crop the region of interest
# from teh image and display it


# close all open windows
cv2.destroyAllWindows()
