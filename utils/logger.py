import logging
import sys


def get_logger(lvl=logging.DEBUG):
    root = logging.getLogger()
    root.setLevel(lvl)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    return root
