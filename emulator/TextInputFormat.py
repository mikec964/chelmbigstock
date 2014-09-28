"""
TextInputFormat module for Hadoop stream API emulator

@Author: Hideki Ikeda
Created: September 19, 2014
"""

from __future__ import print_function

import os
import sys


def input_formatter(fn_list, f_out):
    """
    Reads data files and send the contents to a file object as is.
    Parameters:
        fn_list: list of input file names
        f_out:   file object to store inputs
    """
    for fn in fn_list:
        with open(fn, 'r') as fh:
            for line in fh:
                print(line.strip(), file=f_out)
