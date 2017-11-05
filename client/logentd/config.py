#!/usr/bin/env python

import json


class Config(object):
    """
    Config file loader
    """
    def __init__(self, config_file, *args, **kwargs):
        self.config_file = config_file

    def load(self):
        with open(self.config_file) as fp:
            self._config = json.load(fp)

    def __getattr__(self, key):
        return self._config.get(key)
