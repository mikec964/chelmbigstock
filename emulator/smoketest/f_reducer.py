#!/usr/bin/env python

from __future__ import print_function

import sys

def emit(key, value):
    print('{}\t{}'.format(key,value))


def reducer():
    for raw in sys.stdin:
        key, value = raw.strip().split('\t',1)
        emit(key, value)


if __name__ == '__main__':
    reducer()
