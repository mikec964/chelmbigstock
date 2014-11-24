#!/usr/bin/env python

from __future__ import print_function

import re
import sys
import os

def emit(key, value):
    print('{}\t{}'.format(key, value))


def mapper():
    with open('f_file.txt', 'r') as fh:
        f_key = fh.readline().strip()
        emit('file_key', f_key)


if __name__ == '__main__':
    mapper()
