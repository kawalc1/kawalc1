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


def index(request):
    return static_serve(request, 'index.html', '/home/sjappelodorus/verifikatorc1/static')


def handle_uploaded_file(f, filename):
    with open(path.join(settings.STATIC_DIR, 'upload/' + filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def extract(request):
    filename = request.GET.get("filename", "")
    output = extraction.extract(filename, settings.STATIC_DIR)
    return HttpResponse(output)


def get_probabilities_result(request):
    rows = request.GET.getlist("probabilities")
    matrix = []
    probability_matrix = np.ndarray(shape=(12, settings.CATEGORIES_COUNT), dtype='f')
    for i, row in enumerate(rows):
        probability_matrix[i] = json.loads(row)

    print >> None, str(matrix)

    outcomes = processprobs.get_possible_outcomes(probability_matrix, settings.CATEGORIES_COUNT)
    results = []
    for outcome in outcomes:
        results.append(outcome)
    output = json.dumps({'probabilityMatrix': outcomes}, separators=(',', ':'))

    return HttpResponse(output)


def transform(request):
    if request.method == 'POST':
        filename = request.POST.get("flowFilename", "")
        handle_uploaded_file(request.FILES['file'], filename)

        try:
            output = registration.process_file(None, 1, settings.STATIC_DIR, filename)
        except:
            output = json.dumps({'transformedUrl': None, 'success': False}, separators=(',', ':'))
        return HttpResponse(output)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')
