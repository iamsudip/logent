#!/usr/bin/env python

import datetime
import json
import requests
import sys
import time
import threading
from collections import deque

from requests.exceptions import ConnectionError

from buffer import Buffer
from logger import log
from utils import debug


class LogManagerFactory(object):
    _instance = None

    @classmethod
    def get_instance(cls, namespace, parser, servers, buffer_size, transfer_count, transfer_thresold):
        instance = cls._instance
        if not instance:
            cls._instance = LogManger(namespace, parser, servers, buffer_size, transfer_count, transfer_thresold)
        return cls._instance


class LogManger(object):
    def __init__(self, namespace, parser, servers, buffer_size=10000, transfer_count=10, transfer_thresold=10):
        self.namespace = namespace
        self.parser = parser
        self.buffer = Buffer(maxlen=buffer_size)
        self.transfer_count = transfer_count
        self.transfer_thresold = transfer_thresold
        self.servers = servers
        self._enable_logger()

    def _enable_logger(self):
        self.log = log

    def start_worker(self):
        thread = threading.Thread(target=self.send_data)
        thread.daemon = True
        thread.start()

    def send_data(self):
        while True:
            data = self.get_from_buffer()
            try:
                if data:
                    payload = self.prepare_for_sending(data)
                    for server in self.servers:
                        requests.post(server, data=json.dumps(payload))
            except ConnectionError:
                self.log('Server not reachable!')
                self.add_to_buffer(data)
            time.sleep(self.transfer_thresold)

    def prepare_for_sending(self, data):
        return {
            'logs': data
        }

    def prepare_data(self, data):
        return {
            'namespace': self.namespace,
            'timestamp': datetime.datetime.now().isoformat(),
            'data': data,
        }

    def get_from_buffer(self):
        return self.buffer.get_multi(self.transfer_count)

    def add_to_buffer(self, data):
        self.buffer.extend(data)

    def callback(self, filename, log):
        # self.log('Callback getting called!')
        parsed_content = self.parser.parse(log)
        data = self.prepare_data(parsed_content)
        self.add_to_buffer([data])
