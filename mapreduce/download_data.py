#!/usr/bin/env python3

'''
Oct 23, 2014
@author Hideki Ikeda
'''

import datetime
import os
import sys
from urllib import request as urlreq
from urllib import error as urlerr

# local import
from preprocess import read_symbols


base_url='http://ichart.finance.yahoo.com/table.csv?s={sym}&a={from_m}&b={from_d}&c={from_y}&d={to_m}&e={to_d}&f={to_y}&g=d&ignore=.csv'
iso_date_fmt = '%Y-%m-%d'

def download_stocks(symbols, from_date, to_date = None, data_dir = 'data', max_stocks = None):
    '''
    Download stock quotes from Yahoo finance web page and stores as a file
    Input:
        symbols   : iterable object of stock symbols
        from_date : date string in ISO format. ex) '2014-02-23' for Feb 23, 2014
        to_date   : date string in ISO format. If None, uses today's.
                    Default is None.
        data_dir  : directory where data files are stored.
                    Default is data right under the current directory.
        max_stocks: the maximum number of fils to read. If none, reads all.
                    Default is None.
    Return:
        None
    Exceptions:
        exceptions which datetime.datetime.strptime throws
        exceptions which the symbols iterable object throws
    '''
    print(from_date, to_date, data_dir, max_stocks)
    from_date = datetime.datetime.strptime(from_date, iso_date_fmt)
    if to_date is None:
        to_date = datetime.date.today()
    else:
        to_date = datetime.datetime.strptime(to_date, iso_date_fmt)

    num = 0
    for symbol in symbols:
        if max_stocks is not None and num >= max_stocks:
            break
        url = base_url.format(
                sym = symbol,
                from_m = from_date.month - 1, from_d = from_date.day, from_y = from_date.year,
                to_m = to_date.month - 1, to_d = to_date.day, to_y = to_date.year
                )
        file_name = os.path.join(data_dir, symbol + '.csv')
        print('Downloading {} ...'.format(symbol))

        try:
            with urlreq.urlopen(url) as src, open(file_name, 'w') as dst:
                dst.write(src.read().decode('utf-8'))
        except urlerr.URLError as e:
            print('Failed to download "{}", Reason:"{}"; Skip'.format(symbol, e.reason), file=sys.stderr)
            continue
        except IOError:
            print('Failed to write to "{}": continue'.format(file_name), file=sys.stderr)
            continue
        if max_stocks is not None:
            num += 1


if __name__ == '__main__':
    class options(object):
        def __init__(self, argv):
            self.max = None
            self.symbol_file_name = 'stock_symbols.txt'
            self.from_date = '1990-01-01'
            self.to_date = None
            self.data_dir = 'data'
            option_handlers = [ self.set_max,
                                self.set_symbol_file_name,
                                self.set_from_date,
                                self.set_to_date,
                                self.set_data_dir ]

            for i in range(min(len(option_handlers), len(argv)-1)):
                option_handlers[i](argv[i+1])

        def set_max(self, option):
            self.max = int(option)

        def set_symbol_file_name(self, option):
            self.symbol_file_name = option

        def set_from_date(self, option):
            self.from_date = option

        def set_to_date(self, option):
            self.to_date = option

        def set_data_dir(self, option):
            self.data_dir = option

    opt = options(sys.argv)

    symbols = read_symbols(opt.symbol_file_name)
    download_stocks(symbols, from_date=opt.from_date, to_date=opt.to_date,
            data_dir=opt.data_dir, max_stocks=opt.max)
