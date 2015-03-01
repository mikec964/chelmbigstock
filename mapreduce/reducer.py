#!/usr/bin/env python

'''
Feb 28, 2015
@author Hideki Ikeda
'''

import sys
import datetime

def write_feature(feature, prices):
    prices.sort(key=lambda i : i[0])
    base = prices[0][1]
    prices = [ str(price[1] / base) for price in prices ]
    print '{}\t{}'.format(feature[:2], ','.join(prices))
        
def reducer():
    '''
    MapReduce implementation of Andy Webber's stock price prediction
    ELT reducer
    For each stcok, gather and normalize adjusted close prices
    '''
    feature = None
    prices = []

    for line in sys.stdin:
        items = line.strip().split('\t')
        if len(items) != 2:
            continue
        if feature != items[0]:
            if feature is not None:
                write_feature(feature, prices)
            feature = items[0]
            prices = []
        
        dstr, pstr = items[1].split(',')
        prices.append( (datetime.datetime.strptime(dstr, '%Y-%m-%d').date(), float(pstr)) )

    if feature is not None:
        write_feature(feature, prices)


if __name__ == '__main__':
    reducer()
