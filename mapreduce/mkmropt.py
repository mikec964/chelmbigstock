#!/usr/bin/env python

'''
Oct 24, 2014
@author Hideki Ikeda

mkmropt.py
Creates options for MapReduce
'''

import os
import sys


# data type
TYPE_TRAINING = 'TR'
TYPE_CV = 'CV'
TYPE_TEST = 'TE'


class data_type_generator(object):
    def __init__(self, factor = 2):
        self._idx = 0
        self._factor = factor

    def next(self):
        self._idx = (self._idx + 1) % self._factor
        return TYPE_CV if self._idx == 0 else TYPE_TRAINING


def read_symbols(file_name, max_stocks = None):
    '''
    Read a stock symbol file in text and put stock symbols into a list.
    Input:
        filename: the file name of the stock symbol file
    Return:
        The list of stock symbols
    Exceptions:
        Exceptions which open() throws
    '''
    with open(file_name,'r') as f_stocks:
        symbols = [ line.strip() for line in f_stocks ]
    if max_stocks is not None:
        symbols = symbols[:max_stocks]
    return symbols


def make_train_cv_data_sets(symbols, cv_factor, f_dst):
    '''
    Categorize stock symbols into train data or CV data
    Input:
        symbols   : iterable objects which contain stock symbols
        f_dst     : file handle to store the processed data; must be writable
    Return:
        None
    '''
    gen = data_type_generator(cv_factor)
    for symbol in symbols:
        print >> f_dst, '{}:{}'.format(gen.next(), symbol)


if __name__ == '__main__':
    print "not implemented yet"
