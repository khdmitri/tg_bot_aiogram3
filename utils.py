import logging
import sys

from core.config import settings


def get_logger():
    lvl = getattr(logging, settings.LOG_LEVEL)
    root = logging.getLogger()
    root.setLevel(lvl)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    return root
