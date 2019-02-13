__author__ = 'samtheisens'
import os
import shutil

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# import django
# from django.conf import settings
#
# settings.configure(DEBUG=True)
# django.setup()
from kawalc1 import settings
import urllib2
import json
import psycopg2
from mengenali import process_form, load_config
from mengenali import get_total_of_checksum, get_numbers_in_checksum_sigma_part

conn = psycopg2.connect("host='localhost'")
cursor = conn.cursor()

base_url = "https://www.kawalpilkada.id/suara/get/2015/Provinsi/"
# start_level = [20802, 20803, 20804, 20813]
start_level = [61965]
# start_level = [20802, 20803, 20804, 87768]


# /tabulasi.html/Provinsi/2015/20802/20803/20804/20813


def compare_with_kpu(response, most_probable, tidak_sah, config):
    suara_kandidat = response["suaraKandidat"]
    probable = most_probable[0]

    # print("prob: " + str(probable))
    numbers = []
    for i, prob in enumerate(probable):
        if prob != "confidence":
            probable[prob]["id"] = prob
            numbers.append(probable[prob])
            # print (str(i) + " : " + str(probable[prob]))
    numbers_in_checksums = {}
    for i, checksum in enumerate(config["checkSums"]):
        for j, number_in_checksum in enumerate(get_numbers_in_checksum_sigma_part(numbers, checksum)):
            numbers_in_checksums[number_in_checksum["id"]] = number_in_checksum
    # print("suara kandidat: " + str(suara_kandidat))
    # print("nou moe!" + str(numbers_in_checksums))

    for number in numbers_in_checksums:
        kawalc1_number = numbers_in_checksums[number]
        pilkada_number = suara_kandidat[str(int(number) + 1)]
        pilkada_number["suaraKawalC1"] = kawalc1_number["number"]
    response["suarahsahKawalC1"] = get_total_of_checksum(numbers, checksum)[0]["number"]

    response["suaratidaksahKawalC1"] = tidak_sah


def process_tps(response):
    kpugambar = response["kpugambar3"]
    outcome = None
    result = None
    if kpugambar != "" and kpugambar is not None:
        config = load_config("kalimantan_selatan.json")
        failed_to_process = False
        try:
            result = json.loads(process_form("kalimantan_sel.json", config, kpugambar))
            most_probable = result["probabilityMatrix"][0]
            other_numbers = result["probabilityMatrix"][1]
            if other_numbers:
                index, tak_sah = other_numbers[0].items()[0]
                tidak_sah = tak_sah["number"]
            else:
                tidak_sah = 0
        except:
            failed_to_process = True
            most_probable = None
            tidak_sah = 0

        if failed_to_process:
            outcome = "incomplete-tps-info"
        elif not most_probable:
            outcome = "detection-failed"
        else:
            compare_with_kpu(response, most_probable, tidak_sah, config)
            cursor.execute(
                "INSERT INTO tps (urllink, image_url, kpuid, sah_pilkada, sah_kpu, sah_kawalc1, tidak_sah_pilkada, tidak_sah_kpu, tidak_sah_kawalc1, roi_url) " +
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (response["urllink"], response["kpugambar3"], response["kpuid"], response["suarasah"],
                 response["suarasahKPU"], response["suarahsahKawalC1"],
                 response["suaratidaksah"], response["suaratidaksahKPU"], response["suaratidaksahKawalC1"],
                 result["digitArea"]
                 ))

            outcome = "match"

            for index in response["suaraKandidat"]:
                kandidat = response["suaraKandidat"][index]
                cursor.execute("INSERT INTO hasil_kandidat (nama, kpu, kawalc1, pilkada, urut, kpuid) " +
                               "VALUES (%s, %s, %s, %s, %s, %s)",
                               (kandidat["nama"], kandidat["suaraKPU"], kandidat["suaraKawalC1"],
                                kandidat["suaraVerifikasiC1"], kandidat["urut"], response["kpuid"]))
                if kandidat["suaraVerifikasiC1"] != kandidat["suaraKawalC1"]:
                    outcome = "vote-mismatch"
                    break
            conn.commit()
            if response["suarasah"] != response["suarahsahKawalC1"]:
                outcome = "vote-mismatch"

            if outcome != "vote-mismatch" and response["suaratidaksah"] != response["suaratidaksahKawalC1"]:
                outcome = "tidak-sah-mismatch"
    else:
        outcome = "incomplete-tps-info"

    target_folder = os.path.join(settings.VALIDATION_DIR, outcome)

    with open(os.path.join(target_folder, response["kpuid"] + ".json"), "w") as result_file:
        result_file.write(json.dumps(response))

    if result is not None and outcome is not "detection-failed":
        digit_area = result["digitArea"]
        shutil.copy(os.path.join(settings.STATIC_DIR, digit_area),
                    os.path.join(target_folder, response["kpuid"] + os.path.basename(digit_area)))

    print("pilkada: " + json.dumps(response))


def skip_until(sub_levels, recorded_level):
    remaining_levels = []
    start_adding = False
    for sub_level in sub_levels:
        if sub_level["kpuid"] == str(recorded_level):
            start_adding = True
        if start_adding:
            print sub_level["kpuid"] + " - " + str(recorded_level)
            remaining_levels.append(sub_level)
    return remaining_levels


def get_level(level, level_id):
    url = base_url + str(level_id)
    print url
    response = json.load(urllib2.urlopen(url))
    # sub_levels = response[0] if start_level else itertools.dropwhile(lambda x: x["kpuid"] != level_id, response[0])
    # sub_levels =
    # print(sub_levels)
    for sub_level in (skip_until(response[0], start_level[0]) if start_level else response[0]):
        if sub_level["tingkat"] == "TPS":
            # print str(level) + " we zijn er!" + sub_level["urllink"]
            process_tps(sub_level)
        else:
            next_level = start_level.pop(0) if start_level else sub_level["kpuid"]

            get_level(level + 1, next_level)


get_level(0, start_level.pop(0))
