#!/usr/bin/env python
# for python 2.7
import sys
from sample import func1, func2, func3

"""
'python main.py -p' runs the PARALLEL code.
'python main.py -l' runs the NON parallel code.
"""

if __name__ == '__main__':
    func1()
    print
    func2()
    print
    func3()
