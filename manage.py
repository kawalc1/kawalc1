#!/usr/bin/env python
import logging
import os
import sys

from kawalc1 import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kawalc1.settings")
    logging.getLogger().setLevel(logging.INFO)
    logging.warning("version %s", settings.VERSION)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
