# Create your views here.
from os import path
import json

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseNotAllowed
from django.conf import settings
import numpy as np
from django.views.static import serve as static_serve
import logging

import registration
import extraction
import processprobs
import urllib2


def index(request):
    return static_serve(request, 'index.html', '/home/sjappelodorus/verifikatorc1/static')


def handle_uploaded_file(f, filename):
    with open(path.join(settings.STATIC_DIR, 'upload/' + filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def download_file(uri, target_path):
    file_to_get = urllib2.urlopen(uri)
    with open(path.join(settings.STATIC_DIR, target_path + '/' + path.basename(uri)), 'wb') as downloaded_file:
        downloaded_file.write(file_to_get.read())


def extract(request):
    filename = request.GET.get("filename", "")
    output = extraction.extract(filename, settings.STATIC_DIR, path.join(settings.STATIC_DIR, 'extracted'),
                                settings.STATIC_DIR, load_config(request.GET.get("configFile")))
    return HttpResponse(output)


def load_config(config_file_name):
    with open(path.join(settings.DATASET_DIR, config_file_name)) as config_file:
        config = json.load(config_file)
    return config


def get_probabilities_result(request):
    json_data = json.loads(request.body)

    print >> None, str(json_data)

    outcomes = processprobs.get_possible_outcomes_for_config(load_config(json_data["configFile"]),
                                                             json_data["probabilities"], settings.CATEGORIES_COUNT)
    results = []
    for outcome in outcomes:
        results.append(outcome)
    output = json.dumps({'probabilityMatrix': outcomes}, separators=(',', ':'))

    return HttpResponse(output)


def get_reference_form(config_file_name):
    config = load_config(config_file_name)
    return path.join(settings.DATASET_DIR, config["referenceForm"])


def download(request):
    scan_uri = request.GET.get("scanURI", "")
    download_file(settings.KPU_SCANS_URL + scan_uri, "upload")

    try:
        output = registration.process_file(None, 1, settings.STATIC_DIR, scan_uri, get_reference_form())
    except:
        output = json.dumps({'transformedUrl': None, 'success': False}, separators=(',', ':'))
    return HttpResponse(output)


def transform(request):
    if request.method == 'POST':
        filename = request.POST.get("flowFilename", "")
        handle_uploaded_file(request.FILES['file'], filename)

        try:
            config_file = request.POST.get("configFile", "")
            output = registration.process_file(None, 1, settings.STATIC_DIR, filename, get_reference_form(config_file),
                                               config_file)
        except:
            output = json.dumps({'transformedUrl': None, 'success': False}, separators=(',', ':'))
        return HttpResponse(output)
    else:
        return HttpResponseNotFound('Method not supported')


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
            ref_form = lazy_load_reference_form(posted_config["referenceForm"])

            with open(path.join(settings.STATIC_DIR, 'datasets/' + config_name), "w") as outfile:
                json.dump(posted_config, outfile, separators=(',', ':'), indent=4)

            before_dot = scan_url.find('.jpg') - 1
            url_as_list = list(scan_url)
            start_page = int(url_as_list[before_dot])
            pages_in_order = range(1, 6)
            pages_in_order.remove(start_page)
            pages_in_order.insert(0, start_page)

            for page in pages_in_order:
                url_as_list[before_dot] = str(page)
                url_to_download = ''.join(url_as_list)
                download_file(url_to_download, "upload")
                try:
                    registered_file = registration.process_file(None, 1, settings.STATIC_DIR,
                                                                path.basename(url_to_download),
                                                                ref_form,
                                                                config_name)
                except Exception, err:
                    print Exception, err
                    continue
                transform_output = json.loads(registered_file)
                if transform_output["success"]:
                    break

            transformed_url = transform_output["transformedUrl"]
            extracted = json.loads(extraction.extract("transformed/" + transformed_url, settings.STATIC_DIR,
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
                                                                     probabilities, settings.CATEGORIES_COUNT)
            results = []
            for outcome in outcomes:
                results.append(outcome)
            output = json.dumps({'probabilityMatrix': outcomes, 'digitArea': digit_area}, separators=(',', ':'))

        except Exception, err:
            print Exception, err
            output = json.dumps({'transformedUrl': None, 'success': False, 'error': str(err)}, separators=(',', ':'))

        return HttpResponse(output)
    else:
        return HttpResponseNotAllowed('Method not supported')
