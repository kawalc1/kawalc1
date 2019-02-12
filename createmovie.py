import argparse
import os
from PIL import Image
import cv2
import itertools
import numpy

parser = argparse.ArgumentParser()
parser.add_argument("-inputdir", help="location of directory to traverse",
                    default="C:/temp/pilpres-recog/classified - joint/")
parser.add_argument("-outputfile", help="location of directory to traverse",
                    default="C:/temp/pilpres-recog/movie/")

args = parser.parse_args()
input_dir = args.inputdir
output_file = args.outputfile

width = 1280
height = 720
x_offset = 160
number_size = 240
columns = 4
rows = 3
training_set_size = 7000
digits = range(0, 10)

blank_image = Image.open(os.path.join(output_file, "movie.jpg"))
logo_kawal_pemilu = Image.open(os.path.join(output_file, "kawalpemilu.png"))
logo_kawal_c1 = Image.open(os.path.join(output_file, "kawalc1.png"))

digit_files = []
for i in digits:
    digit_file_names = []
    current_path = os.path.join(input_dir, str(i))
    for root, dirs, file_names in os.walk(os.path.join(input_dir, str(i))):
        for it, file_name in enumerate(file_names):
            digit_file_names.append(file_name)
            # print i, it, file_name
            if it > (training_set_size - 1):
                break
    digit_files.append(digit_file_names)
print(len(digit_files))
print(len(digit_files[0]))
count = 0


def get_x_pos(position):
    return number_size * (position % columns) + x_offset


def get_y_pos(position):
    return number_size * ((position / columns) % rows)


for i in range(0, training_set_size):
    for digit in digits:
        current_dir = os.path.join(input_dir, str(digit))
        number_image = Image.open(os.path.join(current_dir, digit_files[digit][i]))
        number_image.copy()
        big_number = number_image.resize((number_size, number_size), Image.NEAREST)
        pos = digit + 1
        x = get_x_pos(pos)
        y = get_y_pos(pos)
        blank_image.paste(big_number, (x, y))
    blank_image.paste(logo_kawal_pemilu, (get_x_pos(0), get_y_pos(0)))
    blank_image.paste(logo_kawal_c1, (get_x_pos(11), get_y_pos(11)))
    count += 1
    output_file_name = "{0:0>5}".format(count) + ".png"
    print(output_file_name)
    blank_image.save(os.path.join(output_file, output_file_name), "PNG")

