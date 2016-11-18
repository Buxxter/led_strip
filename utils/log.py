#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging


def logger_init(target_logger, module_name):
    module_name = module_name if module_name is not None else __name__
    formatter = logging.Formatter('%(asctime)s - %(module)s[%(lineno)d] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    fh = logging.FileHandler('./log/{0}_log.txt'.format(module_name))
    fh.setLevel(logging.WARNING)
    fh.setFormatter(formatter)

    target_logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    target_logger.addHandler(ch)
    target_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger_init(logger, __name__)