#!/usr/bin/env python

import sys
import re

def main():
    pattern = re.compile("[A-Za-z][0-9A-Za-z]*")

    for line in sys.stdin:
        for word in pattern.findall(line):
            print '{}\t{}'.format(word.lower(), 1)

if __name__ == '__main__':
    main()
