import logging
import os
import urllib

from io import BytesIO
from django.core.files.base import ContentFile
import cv2
from os import path
import numpy as np
from urllib import parse
import urllib.request
import certifi
from PIL import Image

from django.core.files.storage import get_storage_class

from kawalc1 import settings

storage = get_storage_class('django.core.files.storage.FileSystemStorage')()


def is_url(file_path):
    return parse.urlparse(file_path).scheme in ('http', 'https',)


def _to_image(input_stream):
    image = np.asarray(bytearray(input_stream.read()), dtype="uint8")
    input_stream.close()
    return cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)


def _from_webp(input_stream):
    pil_image = Image.open(BytesIO(input_stream.read()))
    input_stream.close()
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGR2GRAY)


def read_image(file_path):
    filename, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == ".webp":
        return _from_webp(read_file(file_path))
    return _to_image(read_file(file_path))


def read_file(file_path):
    if is_url(file_path):
        return urllib.request.urlopen(file_path, cafile=certifi.where())
    else:
        logging.info("reading %s", file_path)
        try:
            return storage.open(file_path, 'rb')
        except:
            logging.error("Could not open %s", file_path)


def write_image(file_path, image):
    file, extension = path.splitext(file_path)
    encoded, name = cv2.imencode(extension, image)
    logging.info("writing %s", file_path)
    storage.save(file_path, ContentFile(name))


def image_url(file_path):
    return file_path if settings.LOCAL else storage.url(path.join(settings.STATIC_DIR, file_path))
