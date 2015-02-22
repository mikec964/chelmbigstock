#!/usr/bin/env python

'''
Oct 24, 2014
@author Hideki Ikeda

mkmropt.py
Creates options for MapReduce
'''

import os
import sys
import datetime as dt
import bisect as bi
from collections import defaultdict
import ConfigParser as cp


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
        filename   : the file name of the stock symbol file
        max_stocks : the max number of stocks we use
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


def make_symbol_sets(symbols, cv_factor, f_dst):
    '''
    Categorize stock symbols into train data or CV data
    Input:
        symbols   : iterable objects which contain stock symbols
        cv_factor : determines what portion of stocks to put in cross validation
                    set and what portion to leave in training set.
        f_dst     : file handle to store the processed data; must be writable
    Return:
        None
    '''
    gen = data_type_generator(cv_factor)
    for symbol in symbols:
        print >> f_dst, '{}:{}'.format(gen.next(), symbol)

def read_calendar(fn_cal):
    '''
    Read a market calendar file and returns list of dates
    Input:
        fn_cal  : file name of a calendar file
    return
        list of dates
    '''
    with open(fn_cal, 'r') as f_cal:
        cal = [ dt.datetime.strptime(line.strip(), '%Y-%m-%d').date()
                for line in f_cal ]
    return cal

def extract_dates(cal, first_date, train_days, train_inc, future_day):
    '''
    Make a list of dates whose stock values are used as feature.
    Input:
        cal         : list of dates when the stock market opens
        first_date  : the first date of date range
        train_days  : difference between the first date and the last date
                      of training/test date range
        train_inc   : difference between each feature date in the date range
        future_day  : difference between the first date and the target date
    Return:
        The list of dates. If calendar doesn't have enough dates, returns None.
    '''
    if train_days < 1 or train_inc < 1 or future_day < train_days:
        raise ValueError

    # get index of the first date in cal. If there is no exact date,
    # returns the next open date
    i_first = bi.bisect_left(cal, first_date)
    if i_first + train_days > len(cal):
        return None
    dates = [ cal[i] for i in xrange(i_first, i_first + train_days, train_inc) ]
    dates.append(cal[i_first + future_day])
    return dates

def make_date_sets(cal, ref_dates, test_dates, train_days, train_inc, future_day, f_dst):
    '''
    Make a list of dates whose stock values are used as feature and target.
    The result is stored in the specifed file.
    Input:
        cal         : list of dates when the stock market opens
        ref_dates   : list of reference dates (first dates of training dates)
        test_dates  : list of test dates (first dates of test dates)
        train_days  : difference between the first date and the last date
                      of training/test date range
        train_inc   : difference between each feature date in the date range
        future_day  : difference between the first date and the target date
        f_dst       : file handle to store the processed data; must be writable
    return:
        None
    '''
    dt_dict = defaultdict(list)

    for idx, rdate in enumerate(ref_dates):
        label = 'R{}'.format(idx)
        dates = extract_dates(cal, rdate, train_days, train_inc, future_day)
        for date in dates:
            dt_dict[date].append(label)

    for idx, tdate in enumerate(test_dates):
        label = 'T{}'.format(idx)
        dates = extract_dates(cal, tdate, train_days, train_inc, future_day)
        for date in dates:
            dt_dict[date].append(label)

    for k in sorted(dt_dict):
        datestr = k.strftime('%Y-%m-%d,')
        labelstr = ':'.join(dt_dict[k])
        print >> f_dst, datestr + labelstr

def make_option_data(
        fn_cal, ref_dates, test_dates, train_days, train_inc, future_day,
        fn_sym, cv_factor, max_stocks,
        fn_opt):
    '''
    Make an option data for MapReduce program of stock price prediction,
    and store the data in a file
    Input:
        fn_cal     : file name of market calendar
        ref_dates  : list of reference dates (first dates of training dates)
        test_dates : list of test dates (first dates of test dates)
        train_days : difference between the first date and the last date
                     of training/test date range
        train_inc  : difference between each feature date in the date range
        future_day : difference between the first date and the target date
        symbols    : iterable objects which contain stock symbols
        cv_factor  : determines what portion of stocks to put in cross validation
                     set and what portion to leave in training set.
        max_stocks : the max number of stocks we use; If None, take all symbols
        fn_opt     : name of file where the reuslt is stored
    return:
        None
    '''
    if ref_dates is None or len(ref_dates) == 0:
        raise ValueError("No reference dates")
    if test_dates is None or len(test_dates) == 0:
        raise ValueError("No test dates")
    if train_days < 2:
        raise ValueError("Not enough train days")
    if train_inc < 1:
        raise ValueError("train increment must be > 0")
    if train_days <= train_inc:
        raise ValueError("train_inc too large")
    if future_day < train_days:
        raise ValueError("future day before last train date")
    if cv_factor < 2:
        raise ValueError("cv_factor must >= 2")
    if max_stocks is not None and max_stocks < cv_factor:
        raise ValueError("max_stocks must be equal to or larger than cv_factor")

    symbols = read_symbols(fn_sym, max_stocks)
    cal = read_calendar(fn_cal)
    with open(fn_opt, 'w') as f_dst:
        make_symbol_sets(symbols, cv_factor, f_dst)
        make_date_sets(cal, ref_dates, test_dates,
                train_days, train_inc, future_day, f_dst)

class ini_reader(object):
    '''
    Read an argument file in .ini format
    '''
    def __init__(self, arg_file):
        '''
        See the text for argument_reader for the details about arg_file
        '''
        section = 'mkmropt'
        parser = cp.SafeConfigParser()
        with open(arg_file, 'r') as fp_arg:
            parser.readfp(fp_arg)

            try:
                self._calendar_file = parser.get(section, 'calendar_file')

                datelist = parser.get(section, 'reference_dates')
                datelist = datelist.split(',')
                self._reference_dates = [
                        dt.datetime.strptime( line.strip(), '%Y-%m-%d').date()
                        for line in datelist ]

                datelist = parser.get(section, 'test_dates')
                datelist = datelist.split(',')
                self._test_dates = [
                        dt.datetime.strptime( line.strip(), '%Y-%m-%d').date()
                        for line in datelist ]

                self._train_days = parser.getint(section, 'train_days')

                self._train_increment = parser.getint(section, 'train_increment')

                self._future_day = parser.getint(section, 'future_day')

                self._symbol_file = parser.get(section, 'symbol_file')

                self._cv_factor = parser.getint(section, 'cv_factor')

                self._result_file = parser.get(section, 'result_file')
            except cp.NoSectionError as nose:
                raise ValueError("No section:{}".format(nose.message))
            except cp.NoOptionError as noop:
                raise ValueError('No option:{}'.format(noop.message))

            try:
                self._max_stocks = parser.getint(section, 'max_stocks')
            except cp.NoOptionError:
                # set default value
                self._max_stocks = None

    @property
    def calendar_file(self):
        return self._calendar_file

    @property
    def reference_dates(self):
        return self._reference_dates

    @property
    def test_dates(self):
        return self._test_dates

    @property
    def train_days(self):
        return self._train_days

    @property
    def train_increment(self):
        return self._train_increment

    @property
    def future_day(self):
        return self._future_day

    @property
    def symbol_file(self):
        return self._symbol_file

    @property
    def cv_factor(self):
        return self._cv_factor

    @property
    def max_stocks(self):
        return self._max_stocks

    @property
    def result_file(self):
        return self._result_file

def argument_reader(arg_file):
    '''
    Read an argument file for mkmropt
    Input:
        arg_file : file name of argument file.
                   .ini (Windows configuration format) is supported.
    Return:
        Argument object. The object has attributes below:
            calendar_file
            reference_dates
            test_dates,
            train_days,
            train_increment
            future_day
            symbol_file
            cv_factor
            max_stocks
            result_file
    Exceptions:
        IOError    : Failed to open the argument file
        ValueError : Argument value is not specified
    '''
    return ini_reader(arg_file)

if __name__ == '__main__':
    print "not implemented yet"
