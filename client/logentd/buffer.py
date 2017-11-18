#!/usr/bin/env python

from collections import deque


class Buffer(deque):
    def is_empty(self):
        return len(self) == 0

    def get(self):
        try:
            return self.pop()
        except IndexError: # Incase empty
            return None

    def get_multi(self, count):
        elements = []
        for _ in xrange(count):
            element = self.get()
            if element:
                elements.append(element)
        return elements
