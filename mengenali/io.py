import logging

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import cv2
from os import path
import numpy as np

from kawalc1 import settings


def read_image(file_path):
    logging.info("reading %s", file_path)
    file = default_storage.open(file_path, 'rb')

    image = np.asarray(bytearray(file.read()), dtype="uint8")
    file.close()
    return cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)


def write_image(file_path, image):
    file, extension = path.splitext(file_path)
    encoded, name = cv2.imencode(extension, image)
    logging.info("writing %s", file_path)
    default_storage.save(file_path, ContentFile(name))


def image_url(file_path):
    return file_path if settings.LOCAL else default_storage.url(path.join(settings.STATIC_DIR, file_path))
