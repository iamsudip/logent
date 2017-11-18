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
    parser_type = config.parser_type
    parser_context = config.parser_context
    log_file = config.log_file
    buffer_size = config.buffer_size
    transfer_count = config.bulk_transfer_max_count
    transfer_thresold = config.transfer_thresold
    servers = config.servers
    parser = LogParserFactory.get_parser(parser_type, parser_context)
    log_manager = LogManagerFactory.get_instance(namespace, parser, servers, buffer_size, transfer_count, transfer_thresold)
    log_manager.start_worker()
    w = Watcher(log_file, log_manager.callback)
    w.watch()


if __name__ == '__main__':
    collector()
