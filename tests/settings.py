import os


LOCAL = True
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = "./"

import logging
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)


INMEMORYSTORAGE_PERSIST = True
STATIC_DIR = os.path.join(BASE_DIR, 'static')
VALIDATION_DIR = os.path.join(BASE_DIR, 'validation')
DATASET_DIR = os.path.join(STATIC_DIR, 'datasets')
CONFIG_FILE = os.path.join(DATASET_DIR, 'gubernur-jakarta.json')
CATEGORIES_COUNT = 11
GS_BUCKET_NAME = 'kawalc1'
GS_FILE_OVERWRITE = True
GS_DEFAULT_ACL = 'publicRead'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_146et)+93n!)efakmmt4%$@3^zng1c0nf=f)3hc@gw6p@yy4e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '159.203.92.77',
    '0.0.0.0',
    '127.0.0.1',
    'localhost',
    'kawalc1.appspot.com'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_DIRS = 'static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    STATIC_DIRS
]
