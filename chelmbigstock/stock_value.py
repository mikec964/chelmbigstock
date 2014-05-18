#!/usr/bin/env python3

'''
Apr 28, 2014
@author Hideki Ikeda
Need python 3.x in Anaconda environment
'''

import os
import csv
import datetime
import urllib.request

class StockHist:
    '''
    Acquires historical quote of a stock from Yahoo.
    StockHist(symbol, start_date = None, end_date = None)
        symbol: stock symbol
        start_date: the first date of history data. If the date is a holyday,
                   the date is fetched from the next work day.
        end_date: the last date of history date. If the date is a holyday,
                 the last work day before end_date is the last.
    Note: the constructor may raise an expception if it cannot establish
          connection to Yahoo server.
    '''
    # default directory to store stock data
    default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    # Yahoo finalcial API constants
    _FDELIM = '_'
    _DFMT = '%Y%m%d'
    _EXT = '.csv'
    _URL_HEADER = 'http://ichart.yahoo.com/table.csv?s='
    _URL_TRAILER = '&g=w&ignore=.csv'
    _URL_SMONTH = '&a='
    _URL_SDAY = '&b='
    _URL_SYEAR = '&c='
    _URL_EMONTH = '&d='
    _URL_EDAY = '&e='
    _URL_EYEAR = '&f='

    def _make_url(self):
        emonth = str(self._end_date.month - 1)
        eday = str(self._end_date.day)
        eyear = str(self._end_date.year)
        if self._start_date != None:
            smonth = str(self._start_date.month - 1)
            sday = str(self._start_date.day)
            syear = str(self._start_date.year)
            return ''.join([self._URL_HEADER, self._symbol,
                            self._URL_SMONTH, smonth, self._URL_SDAY, sday, self._URL_SYEAR, syear,
                            self._URL_EMONTH, emonth, self._URL_EDAY, eday, self._URL_EYEAR, eyear,
                            self._URL_TRAILER ])
        else:
            return ''.join([self._URL_HEADER, self._symbol,
                            self._URL_EMONTH, emonth, self._URL_EDAY, eday, self._URL_EYEAR, eyear,
                            self._URL_TRAILER ])

    def __init__(self, symbol, start_date = None, end_date = None):
        '''
        StockHist(symbol, start_date = None, end_date = None)
            symbol: stock symbol
            start_date: the first date of history data. If the date is a holyday,
                       the date is fetched from the next work day.
            end_date: the last date of history date. If the date is a holyday,
                     the last work day before end_date is the last.
        Note: the constructor may raise an expception if it cannot establish
              connection to Yahoo server.
        '''
        self._dates = None
        self._highs = None
        self._path = self.default_path      # data cache directory
        self._symbol = symbol
        self._start_date = start_date
        self._end_date = end_date if end_date != None else datetime.date.today() - datetime.timedelta(days=1)
        sdate_str = '' if start_date == None else start_date.strftime(self._DFMT)
        edate_str = self._end_date.strftime(self._DFMT)
        self._filename = os.path.join(self._path, ''.join([symbol, sdate_str, self._FDELIM, edate_str, self._EXT]))
        # if data is not cached yet, grab it from Yahoo
        if not os.path.isfile(self._filename):
            url = self._make_url()
            response = urllib.request.urlopen(url)
            with open(self._filename, 'wb') as f_out:
                f_out.write(response.read())

    @property
    def symbol(self):
        return self._symbol

    @property
    def start_date(self):
        return self._start_date if self._start_date != None else datetime.date.min

    @property
    def end_date(self):
        return self._end_date

    @property
    def filename(self):
        return self._filename

    def _read_data(self, pos, converter):
        new_list = []
        with open(self._filename, newline='') as f_csv:
            data_reader = csv.reader(f_csv)
            next(data_reader)   # the first line is a header; skip it
            for row in data_reader:
                new_list.append(converter(row[pos]))
        new_list.reverse()      # Yahoo returns newest first; we need oldest first
        return new_list
    
    @property
    def dates(self):
        if self._dates == None:
            self._dates = self._read_data(0, lambda datestr: datetime.datetime.strptime(datestr, '%Y-%m-%d').date())
        return self._dates[:]

    @property
    def highs(self):
        if self._highs == None:
            self._highs = self._read_data(2, lambda val: float(val))
        return self._highs[:]


class StockValue:
    '''
    Represents values of a stock from past to future
    '''

    def __init__(self, stock_hist, predictor, comment):
        self._hist = stock_hist
        self._predictor = predictor
        self._comment = comment
        self._fitted = False
        self._date_offset = 0

    @property
    def symbol(self):
        return self._hist.symbol

    @property
    def comment(self):
        return self._comment

    @property
    def past_dates(self):
        return self._hist.dates

    @property
    def past_highs(self):
        return self._hist.highs

    def future_highs(self, future_dates):
        if not self._fitted:
            original = self._hist.dates
            self._date_offset = original[0].toordinal()
            ordinal = [x.toordinal()-self._date_offset for x in original]
            self._predictor.fit(ordinal, self._hist.highs)
            self._fitted = True

        # convert date to interger
        ordinal_x = [x.toordinal()-self._date_offset for x in future_dates]
        return self._predictor.predict(ordinal_x)

class LinearAdapter:
    '''
    Adapter for linear model
    '''

    def __init__(self, clf):
        self._clf = clf

    def fit(self, x, y):
        X = [ [i] for i in x ]
        self._clf.fit(X, y)

    def predict(self, x):
        X = [[i] for i in x]
        return self._clf.predict(X)


class QuadraticAdapter:
    '''
    Adapter for quadratic regression
    '''
    
    def __init__(self, clf):
        self._clf = clf
        
    def fit(self, x, y):
        X = [ [i, i*i] for i in x ]
        self._clf.fit(X, y)

    def predict(self, ex):
        X = [[i, i*i] for i in ex]
        return self._clf.predict(X)


class CubicAdapter:
    '''
    Adapter for cubic regression
    '''

    def __init__(self, clf):
        self._clf = clf

    def fit(self, x, y):
        X = [ [i, i**2, i**3] for i in x ]
        self._clf.fit(X, y)

    def predict(self, ex):
        X = [[i, i**2, i**3] for i in ex]
        return self._clf.predict(X)
