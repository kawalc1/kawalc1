import mengenali.extraction as extraction
import os
import fnmatch
import argparse
import psycopg2
import csv


parser = argparse.ArgumentParser()
parser.add_argument("-inputdir", help="location of directory to traverse",
                    default="C:/temp/pilpres/53241-BALI/53242-JEMBRANA/53243-NEGARA/53244-BALER_BALE_AGUNG")
parser.add_argument("-kawalpemilucsv", help="location of the kawalpemilu ",
                    default="static/datasets/kawalpemilu.csv")

args = parser.parse_args()
csv_file = args.kawalpemilucsv
input_dir = args.inputdir

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


def classify_numbers():
    parent_path = os.path.split(os.path.abspath(os.path.join(root, filename)))[0]
    head, tail = os.path.split(parent_path)
    kelurahan = tail.split("-")[0]
    image_name = filename.split('~')[-1]
    tps_number = int(image_name[15:18])
    cursor = con.cursor()
    cursor.execute(
        "SELECT prabowo, jokowi, sah, tidaksah, entered, errorreportedby from human where kelurahan = %s and tpsno = %s",
        (kelurahan, tps_number))
    prabowo, jokowi, sah, tidaksah, entered, errorreportedby = cursor.fetchone()
    if errorreportedby is 1:
        return None
    return prabowo, jokowi, sah, tidaksah, entered, errorreportedby



for root, dirs, file_names in os.walk(input_dir):
    for filename in fnmatch.filter(file_names, '~trans*~hom*~warp*.jpg'):
        print classify_numbers()

        #print os.path.abspath(os.path.join(, os.pardir))


