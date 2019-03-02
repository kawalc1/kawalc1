import logging
import urllib

from django.core.files.base import ContentFile
import cv2
from os import path
import numpy as np
from urllib import parse
import urllib.request
import certifi
from django.core.files.storage import get_storage_class

from kawalc1 import settings

storage = get_storage_class('django.core.files.storage.FileSystemStorage')()


def is_url(file_path):
    return parse.urlparse(file_path).scheme in ('http', 'https',)


def _to_image(input_stream):
    image = np.asarray(bytearray(input_stream.read()), dtype="uint8")
    input_stream.close()
    return cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)


def read_image(file_path):
    if is_url(file_path):
        resp = urllib.request.urlopen(file_path, cafile=certifi.where())
        return _to_image(resp)
    else:
        logging.info("reading %s", file_path)
        file = storage.open(file_path, 'rb')
        return _to_image(file)


def write_image(file_path, image):
    file, extension = path.splitext(file_path)
    encoded, name = cv2.imencode(extension, image)
    logging.info("writing %s", file_path)
    storage.save(file_path, ContentFile(name))


def image_url(file_path):
    return file_path if settings.LOCAL else storage.url(path.join(settings.STATIC_DIR, file_path))
