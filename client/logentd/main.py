#!/usr/bin/env python

import click

from config import Config
from parser import LogParserFactory
from watcher import Watcher
from worker import LogManagerFactory

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
