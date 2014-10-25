#!/usr/bin/env python3

'''
Oct 24, 2014
@author Hideki Ikeda
'''

import os
import sys


# data type
TYPE_TRAINING = 'TR'
TYPE_CV = 'CV'
TYPE_TEST = 'TE'


class data_type_generator(object):
    # class property
    data_types = [TYPE_CV, TYPE_TRAINING]

    def __init__(self):
        self._idx = 0

    def next(self):
        self._idx = (self._idx + 1) % len(self.data_types)
        return self.data_types[self._idx]


def read_symbols(file_name):
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
    return symbols


def preprocess(symbols, data_dir, fn_dst, max_stocks = None):
    '''
    Read the stock data from csv files, delete the header line, and prepend
    the stock symbol and data set type to each line.
    Input:
        symbols   : iterable objects which contain stock symbols
        data_dir  : directory name where stock data are stored
        fn_dst    : name of the file where the processed data are stored
        max_stocks: maximum number of csv files to be processed
    Return:
        None
    Exceptions:
        OSError if failed to open fn_dst
    '''
    with open(fn_dst, 'w') as f_dst:
        gen = data_type_generator()
        num_processed = 0
        for symbol in symbols:
            if max_stocks is not None and num_processed >= max_stocks:
                return
            fn_src = os.path.join(data_dir, symbol + '.csv')
            try:
                if not os.path.getsize(fn_src) > 0:
                    print('size of file "{}" is 0; skip'.format(fn_src), file=sys.stderr)
                    continue
                with open(fn_src, 'r') as f_src:
                    head = '{},{},'.format(symbol, gen.next())

                    # skip header
                    f_src.readline()

                    for line in f_src:
                        f_dst.write(head + line)
            except OSError as e:
                print('Failed to access to {}; skip'.format(fn_src), file=sys.stderr)

            num_processed += 1


if __name__ == '__main__':
    class options(object):
        def __init__(self, argv):
            self.max = None
            self.symbol_file_name = 'stock_symbols.txt'
            self.data_dir = 'data'
            self.processed_file_name = 'processed.csv'
            option_handlers = [ self.set_max,
                                self.set_symbol_file_name,
                                self.set_data_dir,
                                self.set_processed_file_name ]

            for i in range(min(len(option_handlers), len(argv)-1)):
                option_handlers[i](argv[i+1])

        def set_max(self, option):
            self.max = int(option)

        def set_symbol_file_name(self, option):
            self.symbol_file_name = option

        def set_data_dir(self, option):
            self.data_dir = option

        def set_processed_file_name(self, option):
            self.processed_file_name = option

    if sys.argv[1][0] == '-':
        print('Usage: {} [max_stocks [,symbol_file [,data_dir, [,result_file]]]]'
                .format(os.path.basename(sys.argv[0])))
        sys.exit(1)
    opt = options(sys.argv)

    symbols = read_symbols(opt.symbol_file_name)
    preprocess(symbols, opt.data_dir, opt.processed_file_name, opt.max)
