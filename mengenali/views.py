# Create your views here.
import json
import logging
import traceback
from os import path
from pathlib import Path
from time import sleep

from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse

from kawalc1 import settings
from django.views.static import serve as static_serve

from mengenali import registration, processprobs, io
from mengenali import extraction
from urllib import request
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime

from mengenali.image_classifier import detect_most_similar
from mengenali.io import write_string, read_image, write_image, write_json, read_color_image, write_color_image, \
    image_url
from mengenali.processprobs import print_outcome, print_outcome_parsable
from mengenali.registration import write_transformed_image

STORAGE_BASE_URL = "https://storage.googleapis.com/kawalc1/2024"


def index(request):
    return static_serve(request, 'index.html', '/home/sjappelodorus/verifikatorc1/static')


def handle_uploaded_file(f, filename):
    target_location = path.join(settings.STATIC_DIR, 'upload/' + filename)
    default_storage.save(target_location, f)


def download_file(uri, target_path):
    file_to_get = request.urlopen(uri)
    with open(path.join(settings.STATIC_DIR, target_path + '/' + path.basename(uri)), 'wb') as downloaded_file:
        downloaded_file.write(file_to_get.read())


@csrf_exempt
def extract_upload(request):
    filename = request.GET.get("filename", "")
    config_file = request.GET.get("configFile", 'digit_config_pilpres_2019.json') if request.GET else \
        json.loads(request.body.decode('utf-8'))["configFile"]
    output = extraction.extract_rois(filename, settings.STATIC_DIR, path.join(settings.STATIC_DIR, 'extracted'),
                                     settings.STATIC_DIR,
                                     load_config(config_file))
    return JsonResponse(output)


@csrf_exempt
def extract_tps(request, kelurahan, tps, filename):
    config_file = request.GET.get('configFile', 'digit_config_pilpres_2019.json').lower()
    config = load_config(config_file)
    base_url = request.GET.get('baseUrl',
                               f'{STORAGE_BASE_URL}/static/transformed/{kelurahan}/{tps}/')
    file_path = path.join(settings.STATIC_DIR, f'transformed/{kelurahan}/{tps}/{filename}')
    # file_path = f'https://storage.googleapis.com/kawalc1/static/transformed/{kelurahan}/{tps}/{filename}'

    output = extraction.extract_rois(file_path, settings.STATIC_DIR,
                                     path.join(settings.STATIC_DIR, f'transformed/{kelurahan}/{tps}/extracted'),
                                     settings.STATIC_DIR,
                                     config)
    return JsonResponse(output)


def load_config(config_file_name):
    with open(path.join(settings.DATASET_DIR, config_file_name)) as config_file:
        config = json.load(config_file)
    return config


@csrf_exempt
def get_probabilities_result_parsable(request):
    json_data = json.loads(request.body.decode('utf-8'))
    outcomes = processprobs.get_possible_outcomes_for_config(load_config(json_data["configFile"]),
                                                             json_data["probabilities"], settings.CATEGORIES_COUNT,
                                                             print_outcome_parsable)
    results = []
    for outcome in outcomes:
        results.append(outcome)
    output = {'probabilityMatrix': outcomes}

    return JsonResponse(output)


@csrf_exempt
def get_probabilities_result(request):
    json_data = json.loads(request.body.decode('utf-8'))

    # logging.info(str(json_data))

    outcomes = processprobs.get_possible_outcomes_for_config(load_config(json_data["configFile"]),
                                                             json_data["probabilities"], settings.CATEGORIES_COUNT,
                                                             print_outcome)
    results = []
    for outcome in outcomes:
        results.append(outcome)
    output = {'probabilityMatrix': outcomes}

    return JsonResponse(output)


def get_reference_form(config_file_name):
    config = load_config(config_file_name)
    return path.join(settings.DATASET_DIR, config["referenceForm"])


def find_number(output, name):
    for prob_sets in output['probabilityMatrix']:
        for prob in prob_sets:
            for (k, v) in prob.items():
                if type(v) is dict and v['shortName'] == name:
                    return v['number']


def get_outcome(output, bubbleNumbers, config_file):
    if config_file == "pilpres_2024_plano_halaman2.json":
        confidence = output['probabilityMatrix'][0][0]['confidence']
        neural_numbers = {
            'anies': find_number(output, 'anies'),
            'prabowo': find_number(output, 'prabs'),
            'ganjar': find_number(output, 'ganjar'),
            'confidence': confidence,
        }
        bubble_numbers = {
            'anies': bubbleNumbers[0],
            'prabowo': bubbleNumbers[1],
            'ganjar': bubbleNumbers[2]
        }
        return {
            "neuralNumbers": neural_numbers,
            "bubbleNumbers": bubble_numbers,
            "confidence": confidence
        }
    return {
        'phpJumlah': find_number(output, 'phpJumlah'),
        'confidence': output['probabilityMatrix'][1][0]['confidence']
    }


def align(request, kelurahan, tps, filename):
    try:
        config_file = request.GET.get('configFile', 'digit_config_pilpres_2019.json').lower()
        matcher = request.GET.get('featureAlgorithm', 'brisk').lower()
        a, image = __do_alignment(filename, kelurahan, request, tps, get_reference_form(config_file), matcher)
        output = {**a}

    except Exception as e:
        logging.exception("failed 'align/<int:kelurahan>/<int:tps>/<str:filename>'")
        output = {'transformedUrl': None, 'success': False}

    return JsonResponse(output)


def __do_alignment(filename, kelurahan, request, tps, reference_form, matcher, store_files=True):
    store_files = json.loads(request.GET.get('storeFiles', 'false').lower())
    base_url = request.GET.get('baseUrl', f'{STORAGE_BASE_URL}/firebase/{kelurahan}/{tps}/')
    url = f'{base_url}/{filename}'
    output_path = path.join(settings.TRANSFORMED_DIR, 'transformed')
    from datetime import datetime
    lap = datetime.now()
    func = registration.register_image_akaze
    # if matcher == "akaze":
    #     func = registration.register_image_akaze
    # if matcher == "sift":
    #     func = registration.register_image_brisk
    # if matcher == "brisk":
    #     func = registration.register_image_brisk

    resp, image = func(url, reference_form, output_path, None, f"{kelurahan}/{tps}/")
    a = json.loads(resp)
    logging.info("1: Register  %s", (datetime.now() - lap).total_seconds())
    return a, image


def extract_roi(request, kelurahan, tps, filename):
    file_path = f'{STORAGE_BASE_URL}/static/transformed/{kelurahan}/{tps}/{filename}.webp'

    tps_dir = path.join(settings.TRANSFORMED_DIR, f'transformed/{kelurahan}/{tps}/')
    image = read_image(file_path)
    tps_roi = image[18:66, 272:520]
    target_path = path.join(tps_dir, 'extracted')
    target_file = f'{filename}~nomorTPS.webp'
    target_image = path.join(target_path, target_file)

    write_image(target_image, tps_roi)
    return JsonResponse({})


def download_original(request, kelurahan, tps):
    filename = request.GET.get('url') + '=s1280'

    image = read_color_image(filename)

    target_image = path.join(settings.TRANSFORMED_DIR,
                             f'transformed/{kelurahan}/{tps}/{Path(filename).name}.original.webp')
    write_color_image(target_image, image)

    print(f"{kelurahan}, {tps}, {filename}, write: {target_image}")
    return JsonResponse({'url': image_url(target_image)})


def download(request, kelurahan, tps, filename):
    config_file = request.GET.get('configFile', 'digit_config_pilpres_2019.json').lower()
    matcher = request.GET.get('featureAlgorithm', 'brisk').lower()
    tps_dir = path.join(settings.TRANSFORMED_DIR, f'transformed/{kelurahan}/{tps}/')

    try:
        maybe_extract_digits = json.loads(request.GET.get('extractDigits', 'true').lower())
        calculate_numbers = json.loads(request.GET.get('calculateNumbers', 'true').lower())
        store_files = json.loads(request.GET.get('storeFiles', 'false').lower())

        config_files = config_file.split(',')
        config_file = config_files[0]

        start_lap = datetime.now()
        a, aligned_image = __do_alignment(filename, kelurahan, request, tps, get_reference_form(config_file), matcher,
                                          store_files)
        similarity = a["similarity"]
        print("Sim1", similarity)
        # if a["similarity"] < 1:
        #     config_file = config_files[1]
        #     second, second_aligned_image = __do_alignment(filename, kelurahan, request, tps,
        #                                                   get_reference_form(config_file), matcher, store_files)
        #     print("Sim2", second["similarity"])
        #     if second["similarity"] > a["similarity"]:
        #         a = second
        #         aligned_image = second_aligned_image
        #         print("second", config_file)
        #     else:
        #         print("Sim1 (back to first)")
        #         output_path = path.join(settings.TRANSFORMED_DIR, 'transformed')
        #         target_path = f'{kelurahan}/{tps}'
        #         base_url = request.GET.get('baseUrl',
        #                                    f'{STORAGE_BASE_URL}/firebase/{kelurahan}/{tps}/')
        #         url = f'{base_url}/{filename}'
        #         write_transformed_image(aligned_image, 0, 0, True, url,
        #                                 output_path, target_path, store_files)
        #         config_file = config_files[0]
        #         print("first", config_file)

        logging.info("1: Align  %s", (datetime.now() - start_lap).total_seconds())

        lap = datetime.now()
        file_path = f'{tps_dir}/{filename}{settings.TARGET_EXTENSION}' if settings.LOCAL else a['transformedUri']

        loaded_config = load_config(config_file)
        extracted_numbers = extraction.extract_rois_in_memory(file_path, path.join(tps_dir, 'extracted'),
                                                              settings.STATIC_DIR, loaded_config, aligned_image, False,
                                                              True) if similarity > 1.0 else {"numbers": []}

        logging.info("2: Extract  %s", (datetime.now() - lap).total_seconds())
        lap = datetime.now()

        probabilities = []
        for number in extracted_numbers["numbers"]:
            probability_set = {"id": number["id"]}
            number_probabilities = []

            for digit_probability in number["extracted"]:
                number_probabilities.append(digit_probability["probabilities"])
            probability_set["probabilitiesForNumber"] = number_probabilities
            probabilities.insert(0, probability_set)

        calculated_outcomes = processprobs.get_possible_outcomes_for_config(loaded_config, probabilities,
                                                                            settings.CATEGORIES_COUNT,
                                                                            print_outcome) if calculate_numbers else {}
        logging.info("3: Probs  %s", (datetime.now() - lap).total_seconds())

        if calculate_numbers:
            # del b['numbers']
            # del b['signatures']
            extracted_numbers['probabilityMatrix'] = calculated_outcomes

        output = {**a, **extracted_numbers}

        outcome = get_outcome(output, extracted_numbers["bubbleNumbers"], config_file) if similarity > 1.0 else {
            'confidence': 0}
        confidence = outcome["confidence"]
        neural_numbers = outcome.get("neuralNumbers") if "neuralNumbers" in outcome else {}
        bubble_numbers = outcome.get("bubbleNumbers") if "bubbleNumbers" in outcome else {}

        output['neuralNumbers'] = neural_numbers
        output['bubbleNumbers'] = bubble_numbers

        outcome = neural_numbers if confidence > 0.6 else bubble_numbers
        output['outcome'] = outcome
        extracted_roi = extracted_numbers["extractedRoi"]
        output['summary'] = {
            'pas1': outcome['anies'],
            'pas2': outcome['prabowo'],
            'pas3': outcome['ganjar'],
            'roiNumbers': [x.get("paslon") for x in extracted_roi if "paslon" in x][0],
            'roiHeading': [x.get("lokasi") for x in extracted_roi if "lokasi" in x][0]
        }

        output['success'] = bool(confidence > 0.8)

        output['duration'] = (datetime.now() - start_lap).total_seconds()
        output['configFile'] = config_file
        response_dir = path.join(settings.LOGS_PATH, f'response/{kelurahan}/{tps}/')
        write_string(response_dir, f'{filename}.json', json.dumps(output, indent=4))
        del output["numbers"]
        del output["transformedUri"]
        del output["probabilityMatrix"]
        del output["duration"]
        if "party" in output:
            del output["party"]
        del output["success"]
        if similarity < 1:
            del output["transformedUrl"]

    except Exception as e:
        logging.exception("failed 'download/<int:kelurahan>/<int:tps>/<str:filename>'")
        trace = ''.join(traceback.TracebackException.from_exception(e).format())
        output = {'transformedUrl': None, 'success': False, 'exception': f'{trace}'}

    write_json(f"{tps_dir}/response.json", json.dumps(output))
    return JsonResponse(output)


@csrf_exempt
def transform(request):
    if request.method == 'POST':
        filename = request.POST.get("flowFilename", "")
        handle_uploaded_file(request.FILES['file'], filename)

        try:

            config_file = request.POST.get("configFile", "")

            detect_matching_config = False

            matching_config_file, reference_form = detect_matching_config_file_from_image(
                filename) if detect_matching_config else config_file, get_reference_form(config_file)

            result = registration.process_file(None, 1, settings.STATIC_DIR, filename, reference_form,
                                               matching_config_file, "brisk")
            output = json.loads(result)
            output["configFile"] = matching_config_file
        except Exception as e:
            logging.exception("this is not good!")
            output = {'transformedUrl': None, 'success': False}
        return JsonResponse(output)
    else:
        return HttpResponseNotFound('Method not supported')


def detect_matching_config_file_from_image(filename):
    image_path = path.join(settings.STATIC_DIR + '/upload', filename)
    image = read_image(image_path)
    most_similar, confidence = detect_most_similar(image, f'datasets/form_features')
    reference_form = most_similar.replace(".brisk", ".jpg")

    config_files = ["pilpres_2024_plano_halaman2.json", "pilpres_2024_plano_halaman3.json"]
    reference_forms = {f"{get_reference_form(config_file)}": config_file for config_file in config_files}
    matching_config_file = reference_forms[f"{settings.STATIC_DIR}/datasets/{reference_form}"]
    return matching_config_file, f"{settings.STATIC_DIR}/datasets/{reference_form}",


def lazy_load_reference_form(form_uri):
    if path.isfile(path.join(settings.DATASET_DIR, form_uri)):
        return path.join(settings.DATASET_DIR, form_uri)
    # file_name = path.basename(form_uri)
    # uploaded_location = path.join(settings.STATIC_DIR, 'datasets/' + file_name)
    # if path.isfile(uploaded_location):
    #     return uploaded_location
    # download_file(form_uri, "datasets")
    # return uploaded_location
    raise Exception("supplied reference form " + str(form_uri) + " not found.")


def custom(request):
    if request.method == 'POST':
        req = json.loads(request.body)

        if "scanURL" not in req:
            return HttpResponseBadRequest("scanURL parameter required")
        if "config" not in req:
            return HttpResponseBadRequest("config parameter required")
        if "configName" not in req:
            return HttpResponseBadRequest("configName parameter required")

        scan_url = req["scanURL"]
        posted_config = req["config"]
        config_name = req["configName"]
        try:
            output = process_form(config_name, posted_config, scan_url)

        except Exception as err:
            logging.exception(err)
            output = json.dumps({'transformedUrl': None, 'success': False, 'error': str(err)}, separators=(',', ':'))

        return HttpResponse(output)
    else:
        return HttpResponseNotAllowed('Method not supported')


def process_form(config_name, posted_config, scan_url):
    ref_form = lazy_load_reference_form(posted_config["referenceForm"])
    with open(path.join(settings.STATIC_DIR, 'datasets/' + config_name), "w") as outfile:
        json.dump(posted_config, outfile, separators=(',', ':'), indent=4)
    before_dot = scan_url.find('.jpg') - 1
    url_as_list = list(scan_url)
    try:
        start_page = int(url_as_list[before_dot])
        pages_in_order = range(1, 6)
        pages_in_order.remove(start_page)
        pages_in_order.insert(0, start_page)
    except ValueError:
        pages_in_order = []
    transform_output = None
    for page in pages_in_order:
        url_as_list[before_dot] = str(page)
        url_to_download = ''.join(url_as_list)
        download_file(url_to_download, "upload")
        try:
            registered_file = registration.process_file(None, 1, settings.STATIC_DIR,
                                                        path.basename(url_to_download),
                                                        ref_form,
                                                        config_name, "akaze")
        except Exception as err:
            logging.warning(Exception, err)
            continue
        transform_output = json.loads(registered_file)
        if transform_output["success"]:
            break
    if transform_output is None:
        download_file(scan_url, "upload")
        registered_file = registration.process_file(None, 1, settings.STATIC_DIR,
                                                    path.basename(scan_url),
                                                    ref_form,
                                                    config_name, "akaze")
        transform_output = json.loads(registered_file)
    transformed_url = transform_output["transformedUrl"]
    extracted = json.loads(extraction.extract_rois("transformed/" + transformed_url, settings.STATIC_DIR,
                                                   path.join(settings.STATIC_DIR, 'extracted'),
                                                   settings.STATIC_DIR, posted_config))
    digit_area = extracted["digitArea"]
    numbers = extracted["numbers"]
    probabilities = []
    for number in numbers:
        probability_set = {"id": number["id"]}
        number_probabilities = []

        for digit_probability in number["extracted"]:
            number_probabilities.append(digit_probability["probabilities"])
        probability_set["probabilitiesForNumber"] = number_probabilities
        probabilities.insert(0, probability_set)
    outcomes = processprobs.get_possible_outcomes_for_config(posted_config,
                                                             probabilities, settings.CATEGORIES_COUNT, print_outcome)
    results = []
    for outcome in outcomes:
        results.append(outcome)
    output = json.dumps({'probabilityMatrix': outcomes, 'digitArea': digit_area}, separators=(',', ':'))
    return output
