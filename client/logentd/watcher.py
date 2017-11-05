#!/usr/bin/env python

import atexit
import logging
import os
import time
import unittest

logger = logging.getLogger('logent.watcher')
# XXX: Make it a method!
# Enable logging to console
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


__all__ = ['Watcher']


class TestWatcher(unittest.TestCase):
    """
    >>>
    """
    def setUp(self):
        self.test_filename = 'hello.log'
        def create_file_if_not_exists(filename):
            if not os.path.exists(filename):
                os.mknod(filename)
        create_file_if_not_exists(self.test_filename)

        self.logs = {}
        def test_callback(filename, lines):
            if filename not in self.logs:
                self.logs[filename] = []
            self.logs[filename].append(lines)

        self.testfile = open(self.test_filename, 'w')
        self.watcher = Watcher(self.test_filename, callback=test_callback)

    def test_watcher(self):
        self.testfile.write('hello')
        self.testfile.flush()
        self.watcher.watch(seek_to_end=False, manual_handling=True)
        self.assertEqual(self.logs, {self.test_filename: ['hello']})

    def tearDown(self):
        self.watcher.unwatch()
        os.remove(self.test_filename)


class Watcher(object):
    """
    >>> logent = logentd.Watcher(
            '/var/log/nginx/access.log', callback=logentd.Watcher.log)
    >>> logent.watch()
    """
    def __init__(self, filename, callback):
        self.filename = filename
        self.callback = callback
        self.chunk_size = 1048576

        # Sanity checks
        assert callable(callback), 'Not a callable: %s' % self.callback
        assert os.path.isfile(self.filename), 'Not a file: %s' % self.filename
        self.log(self.filename, 'File is sane!')

        self.log(self.filename, 'Watcher is set!')

    @staticmethod
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

    def _watch_with_callback(self):
        while True:
            lines = self._opened_file.readline()
            if not lines: break
            self.callback(self.filename, lines)

    def unwatch(self):
        self.log(self.filename, 'Closing file.')
        self._opened_file.close()

    def watch(self, interval=1, seek_to_end=True, manual_handling=False):
        try:
            self._opened_file = open(self.filename, 'rb')
            if seek_to_end:
                self._opened_file.seek(os.path.getsize(self.filename))
            while True:
                self._watch_with_callback()
                if manual_handling:
                    break
                self.log('Sleeping', interval)
                time.sleep(interval)
        finally:
            if not manual_handling:
                self.unwatch()
