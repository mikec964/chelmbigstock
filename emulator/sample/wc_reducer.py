#!/usr/bin/env python

from __future__ import print_function

import sys

def emit(word, count):
    print('{}\t{}'.format(word, count))

def main():
    last_word = None
    last_count = 0
    for line in sys.stdin:
        word, count = line.split('\t', 1)
        try:
            count = int(count)
        except ValueError:
            continue

        if last_word == word:
            last_count += count
        else:
            if last_word:
                emit(last_word, last_count)
            last_word = word
            last_count = count

    if last_word:
        emit(last_word, last_count)


if __name__ == '__main__':
    main()
