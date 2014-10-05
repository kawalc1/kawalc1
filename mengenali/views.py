# Create your views here.
from os import path
import json

from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
import numpy as np
from django.views.static import serve as static_serve

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


def download_file(uri):
    file_to_get = urllib2.urlopen(settings.KPU_SCANS_URL + uri)
    with open(path.join(settings.STATIC_DIR, 'upload/' + path.basename(uri)), 'wb') as downloaded_file:
        downloaded_file.write(file_to_get.read())


def extract(request):
    filename = request.GET.get("filename", "")
    output = extraction.extract(filename, settings.STATIC_DIR, path.join(settings.STATIC_DIR, 'extracted'),
                                settings.STATIC_DIR)
    return HttpResponse(output)


def load_config():
    with open(path.join(settings.DATASET_DIR, 'digit_config.json')) as config_file:
        config = json.load(config_file)
    return config


def get_probabilities_result(request):
    json_data = json.loads(request.body)

    print >> None, str(json_data)

    outcomes = processprobs.get_possible_outcomes_for_config(load_config(), json_data["probabilities"], settings.CATEGORIES_COUNT)
    results = []
    for outcome in outcomes:
        results.append(outcome)
    output = json.dumps({'probabilityMatrix': outcomes}, separators=(',', ':'))

    return HttpResponse(output)


def get_reference_form():
    config = load_config()
    return path.join(settings.DATASET_DIR, config["referenceForm"])


def download(request):
    scan_uri = request.GET.get("scanURI", "")
    download_file(scan_uri)

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
            output = registration.process_file(None, 1, settings.STATIC_DIR, filename, get_reference_form())
        except:
            output = json.dumps({'transformedUrl': None, 'success': False}, separators=(',', ':'))
        return HttpResponse(output)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')
