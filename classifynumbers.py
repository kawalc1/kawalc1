import mengenali.extraction as extraction
from os.path import join, split, abspath, exists
from os import makedirs, walk
import fnmatch
import argparse
import psycopg2
import csv
import cv2


parser = argparse.ArgumentParser()
parser.add_argument("-inputdir", help="location of directory to traverse",
                    default="C:/temp/pilpres/60371-KALIMANTAN_TENGAH")
parser.add_argument("-outputdir", help="location of directory to traverse",
                    default="C:/temp/pilpres-recog/classified")
parser.add_argument("-kawalpemilucsv", help="location of the kawalpemilu ",
                    default="static/datasets/kawalpemilu.csv")

args = parser.parse_args()
csv_file = args.kawalpemilucsv
input_dir = args.inputdir
output_dir = args.outputdir

con = psycopg2.connect("dbname='django' user='django' host='localhost' password='Ccj4AgHQmc'")

def read_csv():
    global cur, file_input_stream, dictionary_reader, i, to_db
    cur = con.cursor()
    # cur.execute(
    #     "CREATE TABLE human (Propinsi, Kabupaten, Kecamatan, Kelurahan, TpsNo, Prabowo, Jokowi, Sah, TidakSah, entered, ErrorReportedBy)")
    with open(csv_file, 'rb') as file_input_stream:  # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dictionary_reader = csv.DictReader(file_input_stream)  # comma is default delimiter
        to_db = [(i['Propinsi'], i['Kabupaten'], i['Kecamatan'], i['Kelurahan'], i['TpsNo'], i['Prabowo'], i['Jokowi'],
                  i['Sah'], i['TidakSah'], i['entered'], i['ErrorReportedBy']) for i in dictionary_reader]
    cur.executemany(
        "INSERT INTO human (Propinsi, Kabupaten, Kecamatan, Kelurahan, TpsNo, Prabowo, Jokowi, Sah, TidakSah, entered, ErrorReportedBy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        to_db)
    con.commit()


def get_human_classification():
    parent_path = split(abspath(join(root, filename)))[0]
    head, tail = split(parent_path)
    kelurahan = tail.split("-")[0]
    image_name = filename.split('~')[-1]
    tps_number = int(image_name[15:18])
    cursor = con.cursor()
    string_to_execute = cursor.mogrify(
        "SELECT prabowo, jokowi, sah, tidaksah, entered, errorreportedby from human where kelurahan = %s and tpsno = %s",
        (kelurahan, tps_number))
    print(string_to_execute)
    cursor.execute(string_to_execute)
    return cursor.fetchone()

def get_joint_result_string(human_results):
    result = ""
    for human_result in human_results:
        result += "{0:0>3}".format(human_result)
    return result


for root, dirs, file_names in walk(input_dir):
    for filename in fnmatch.filter(file_names, '~trans*~hom*~warp*.jpg'):
        print("processing: " + str(join(root, filename)))
        digits, signatures = extraction.cut_digits(root, filename)
        structuring_element = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        extraction.pre_process_digits(digits, structuring_element, False)

        prabowo, jokowi, sah, tidaksah, entered, errorreportedby = get_human_classification()
        if prabowo is None or errorreportedby is 1:
            continue
        string = get_joint_result_string((prabowo, jokowi, sah))
        print(string)
        for i, digit in enumerate(string):
            if int(digit) not in [0]:
                continue
            digit_tif = filename + "~" + str(i) + ".tif"
            digit_dir = join(output_dir, digit)
            if not exists(digit_dir):
                makedirs(digit_dir)
            extracted_tif = join(digit_dir, digit_tif)

            cv2.imwrite(extracted_tif, digits[i])
        # print os.path.abspath(os.path.join(, os.pardir))


