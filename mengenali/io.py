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

storage = get_storage_class(settings.STORAGE_CLASS)()


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
    file = read_file(file_path)
    if file_extension.lower() == ".webp":
        return _from_webp(file)
    return _to_image(file)


def read_file(file_path):
    if is_url(file_path):
        logging.warning("downloading from %s", file_path)
        return urllib.request.urlopen(file_path, cafile=certifi.where())
    else:
        logging.info("reading %s", os.path.abspath(file_path))
        try:
            return storage.open(file_path, 'rb')
        except Exception as e:
            logging.error("Could not open %s \n %s", os.path.abspath(file_path), e)

def open_file(path, flags):
    return storage.open(path, flags)

def write_string(file_path, string):
    storage.save(file_path, ContentFile(string))

def write_image(file_path, image):
    file, extension = path.splitext(file_path)
    if extension.lower() == ".webp":
        logging.info("writing .webp %s", os.path.abspath(file_path))
        fp = BytesIO()
        im_pil = Image.fromarray(image)
        im_pil.save(fp, Image.registered_extensions()['.webp'])

        storage.save(file_path, ContentFile(fp.getbuffer()))
    else:
        logging.info("writing jpeg %s %s", file_path, extension)
        encoded, image = cv2.imencode(extension, image)
        storage.save(file_path, ContentFile(image))

def image_url(file_path):
    return file_path.replace("static/transformed", "https://storage.googleapis.com/kawalc1/static/transformed") if settings.LOCAL else storage.url(file_path)
