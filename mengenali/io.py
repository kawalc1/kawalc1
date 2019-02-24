import logging
import urllib

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import cv2
from os import path
import numpy as np
from urllib import parse
import urllib.request
import certifi

from kawalc1 import settings


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
        file = default_storage.open(file_path, 'rb')
        return _to_image(file)


def write_image(file_path, image):
    file, extension = path.splitext(file_path)
    encoded, name = cv2.imencode(extension, image)
    logging.info("writing %s", file_path)
    default_storage.save(file_path, ContentFile(name))


def image_url(file_path):
    return file_path if settings.LOCAL else default_storage.url(path.join(settings.STATIC_DIR, file_path))
