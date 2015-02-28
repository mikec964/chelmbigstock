#!/usr/bin/env python

'''
Feb 25, 2015
@author Hideki Ikeda
'''

import sys
from collections import defaultdict

TR = 0
CV = 1
Stocks = {}
Dates = defaultdict(list)

def setup_options(fn_opt):
    with open(fn_opt, 'r') as f_opt:
        for line in f_opt:
            items = line.strip().split(',')
            if len(items) == 1:
                # stock item; data_type:stock_symbol
                items = items[0].split(':')
                if len(items) == 2:
                    if items[0] == 'TR':
                        Stocks[items[1]] = TR
                    elif items[0] == 'CV':
                        Stocks[items[1]] = CV
            elif len(items) == 2:
                Dates[items[0]] = [ date_type for date_type in items[1].split(':') ]


def mapper():
    for line in sys.stdin:
        columns = line.strip().split(',')
        symbol = columns[0]
        a_date = columns[1]
        if symbol not in Stocks or a_date not in Dates:
            continue

        for ref_type in Dates[a_date]:
            if ref_type[0] == 'T':
                date_type = 'TE'
            else:
                date_type = 'TR' if Stocks[symbol] == TR else 'CV'
            print '{}{},{}\t{},{}'.format(
                    date_type, ref_type[1], symbol,
                    a_date, columns[7] )

if __name__=='__main__':
    setup_options('options.csv')
    mapper()
