#!/usr/bin/env python

import atexit
import logging
import os
import time
import unittest

from logger import log

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
        self.watcher.watch(manual_handling=True)
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
    def __init__(self, filename, callback, seek_to_end=True):
        self.filename = filename
        self.callback = callback

        # Sanity checks
        assert callable(callback), 'Not a callable: %s' % self.callback
        assert os.path.isfile(self.filename), 'Not a file: %s' % self.filename

        self._filectime = -1
        self._open_file()
        if seek_to_end:
            self._seek()
        self._enable_logger()
        self.log(self.filename, 'File is sane!')
        self.log(self.filename, 'Watcher is set!')

    def _enable_logger(self):
        self.log = log

    def unwatch(self):
        self.log(self.filename, 'Closing file.')
        self._opened_file.close()

    def _open_file(self):
        self._opened_file = open(self.filename)
        self._set_filectime()

    def _seek(self):
        self._opened_file.seek(os.path.getsize(self.filename))

    def _set_filectime(self):
        self._filectime = self._get_filectime(self.filename)

    @staticmethod
    def _get_filectime(filename):
        return os.stat(filename).st_ctime

    def _if_file_changed(self):
        return self._filectime != self._get_filectime(self.filename)

    def watch(self, interval=1, manual_handling=False):
        try:
            while True:
                #if self._if_file_changed():
                #    self.log('File has changed! Reloading...')
                #    self.unwatch()
                #    self._open_file()
                lines = self._opened_file.readlines()
                for line in lines:
                    self.callback(self.filename, line)
                else:
                    self.log('Sleeping', interval)
                    time.sleep(interval)
                if manual_handling:
                    break
        finally:
            if not manual_handling:
                self.unwatch()
