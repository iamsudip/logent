#!/usr/bin/env python

import re


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


