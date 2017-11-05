#!/usr/bin/env python

import datetime
import requests
import threading
from collections import deque


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
