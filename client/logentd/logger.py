#!/usr/bin/env python

import logging


logger = logging.getLogger('logent')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def log(*args):
    """
    log anything and everything!!!
    """
    format_list = []
    for arg in args:
        if isinstance(arg, (str, unicode)):
            format_list.append('%s')
        else:
            format_list.append('%r')
    args_formatter = ' '.join(format_list)
    logger.debug(args_formatter, *args)
