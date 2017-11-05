#!/usr/bin/env python

import threading
import re
import datetime
import json
import time
import requests

import click

from collections import deque

from watcher import Watcher


class LogParserFactory(object):
    parsers = {}

    @classmethod
    def register(cls, klass):
        cls.parsers[klass.TYPE] = klass

    @classmethod
    def get_parser(cls, parser_type, context):
        ParserClass = cls.parsers.get(parser_type)
        if not ParserClass:
            raise NotImplementedError('Unknown parser', parser_type)
        parser = ParserClass(context)
        return parser


class ParserMeta(type):
    def __new__(cls, *args, **kwargs):
        cls = type.__new__(cls, *args, **kwargs)
        log_parser_factory = LogParserFactory()
        parser_type = getattr(cls, 'TYPE', None)
        if parser_type:
            log_parser_factory.register(cls)
        return cls


class BaseParser(object):
    __metaclass__ = ParserMeta

    def __init__(self, context, *args, **kwargs):
        self.context = context

    def parse(self, line):
        raise NotImplementedError()


class RegexParser(BaseParser):
    TYPE = 'regex'

    def get_pattern(self):
        return self.context

    def parse(self, line):
        pattern = self.get_pattern()
        result = re.match(pattern, line)
        return {
            'key': line
        }


class LogManagerFactory(object):
    _instance = None

    @classmethod
    def get_instance(cls, namespace, parser):
        instance = cls._instance
        if not instance:
            cls._instance = LogManger(namespace, parser)
        return cls._instance


class LogManger(object):
    def __init__(self, namespace, parser):
        self.namespace = namespace
        self.parser = parser
        self.buffer = deque()

    def start_worker(self):
        thread = threading.Thread(target=self.send_data)
        thread.daemon = True
        thread.start()

    def send_data(self):
        while True:
            if len(self.buffer) > 0:
                data = self.buffer.pop()
                print data
                requests.post('http://127.0.0.1:8081/', data=json.dumps(data))
            #time.sleep(5)

    def prepare_data(self, data):
        return {
            'namespace': self.namespace,
            'timestamp': datetime.datetime.now().isoformat(),
            'data': data,
        }

    def add_to_buffer(self, data):
        self.buffer.append(data)

    def callback(self, filename, log):
        parsed_content = self.parser.parse(log)
        data = self.prepare_data(parsed_content)
        self.add_to_buffer(data)


class Config(object):
    def __init__(self, config_file, *args, **kwargs):
        self.config_file = config_file

    def load(self):
        with open(self.config_file) as fp:
            self._config = json.load(fp)

    def __getattr__(self, key):
        return self._config.get(key)


collector = click.Group()

@collector.command()
@click.option('--config', default='hello.json')
def start(config):
    config = Config(config)
    config.load()
    namespace = config.namespace
    parser_type = config.pattern_type
    pattern = config.pattern
    log_file = config.log_file
    parser = LogParserFactory.get_parser(parser_type, pattern)
    log_manager = LogManagerFactory.get_instance(namespace, parser)
    log_manager.start_worker()
    w = Watcher(log_file, log_manager.callback)
    w.watch()


if __name__ == '__main__':
    collector()
