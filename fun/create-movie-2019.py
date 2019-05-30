import argparse
import os
import csv
from PIL import Image, ImageFont, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument("-inputdir", help="location of directory to traverse")
parser.add_argument("-outputfile", help="location of directory to traverse")

args = parser.parse_args()
input_dir = args.inputdir
output_file = args.outputfile

background = Image.open("background.png")
pointsize = 65
fillcolor = "black"
shadowcolor = "white"


font_bold = ImageFont.truetype("verdanab.ttf", pointsize)
font_normal = ImageFont.truetype("Verdana.ttf", pointsize)

x, y = 60, 80
text = "PASIE KUALA ASAHAN\nTPS 11"


def draw_text(draw, x, y, text, font, align):
    draw.multiline_text((x, y), text, fill=fillcolor, font=font, align=align)


def draw_text_shadow(draw, x, y, text, font, align):
    draw.text((x - 1, y), text, font=font, fill=shadowcolor)
    draw.text((x + 1, y), text, font=font, fill=shadowcolor)
    draw.text((x, y - 1), text, font=font, fill=shadowcolor)
    draw.text((x, y + 1), text, font=font, fill=shadowcolor)
    # thicker border
    t = 3
    draw.text((x - t, y - t), text, font=font, fill=shadowcolor)
    draw.text((x + t, y - t), text, font=font, fill=shadowcolor)
    draw.text((x - t, y + t), text, font=font, fill=shadowcolor)
    draw.text((x + t, y + t), text, font=font, fill=shadowcolor)

    draw.multiline_text((x, y), text, fill=fillcolor, font=font, align=align)

def leadingspaces(number):
    if len(number) == 3:
        return number
    if len(number) == 2:
        return " " + number
    if len(number) == 1:
        return "  " + number


def create_image(file_path, text, kelurahan, tps, pas1, pas2, tsah):
    new_image = background.copy()
    scan = Image.open(file_path).resize((318 * 2, 613 * 2), Image.ANTIALIAS)
    new_image.paste(scan, (640, 0))
    draw = ImageDraw.Draw(new_image)
    draw_text_shadow(draw, x, y, text + "\nTPS " + tps, font_bold, "left")
    names = "Jokowi-Ma'ruf\n\nPrabowo-Sandi\n\nTidak sah"
    draw_text(draw, x, y + 200, names, font_bold, "right")
    numbers = f'\n{leadingspaces(pas1)}\n\n{leadingspaces(pas2)}\n\n{leadingspaces(tsah)}'

    draw_text(draw, x + 430, y + 200, numbers, font_normal, "right")
    new_image.save(f'/Users/samtheisens/PycharmProjects/movie/{output_file}/{kelurahan}-{tps}.png')


with open(input_dir) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    last_kelurahan = 0
    last_tps = 0
    last_photo = ""
    last_item = ""
    for row in csv_reader:
        if line_count < 87768:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            kelurahan = row[0]
            tps = row[1]
            nama = row[2]
            photo = row[3]
            photo_name = photo.split('/')[3]
            new_item = f'{kelurahan}-{tps}'
            file_path = f'/Users/samtheisens/PycharmProjects/digits/{photo_name}=s1280~digit-area.webp'
            if os.path.isfile(file_path):
                if last_item != new_item:
                    print(f'Found {kelurahan} {tps} {photo_name}')
                    if not os.path.isfile(f'/Users/samtheisens/PycharmProjects/movie/{output_file}/{kelurahan}-{tps}.png'):
                        create_image(file_path, nama, kelurahan, tps, row[4], row[5], row[6])
                        last_item = new_item

# now draw the text over it
