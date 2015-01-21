#!/usr/bin/env python3

'''
mktcal.py
Saves open dates of the stock market from 1960 to 2016
Takes the dates between 1960 and 2014 from the actual data

Data source:
    the holidays in 2015 and 2016
    https://www.nyse.com/markets/hours-calendars

Result:
    mktcal.csv
'''

import sys
import os
from datetime import datetime, timedelta
import csv

sys.path.append('..')
from download_data import download_stocks

Mktcal_csv = os.path.join('..', 'mktcal.csv')

# first day of 2015
First_day = datetime(2015,1,1)

# the next day of the last day of 2016
Last_day = datetime(2017,1,1)

# Holidays in 2015 and 2016 in ISO 8601 format
ISO_holidays15_16 = [ '2015-01-01'  # New Years Day
                    , '2015-01-19'  # Martin Luther King, Jr. Day
                    , '2015-02-16'  # Washington's Birthday
                    , '2015-04-03'  # Good Friday
                    , '2015-05-25'  # Memorial Day
                    , '2015-07-03'  # Independence Day (observed)
                    , '2015-09-07'  # Labor Day
                    , '2015-11-26'  # Thanksgiving Day
                    , '2015-12-25'  # Christmas Day
                    , '2016-01-01'
                    , '2016-01-18'
                    , '2016-02-15'
                    , '2016-03-25'
                    , '2016-05-30'
                    , '2016-07-04'
                    , '2016-09-05'
                    , '2016-11-24'
                    , '2016-12-26'  # observed
                    ]

Weekends = [ 5, # Saturday
             6  # Sunday
           ]

Isoformat = '%Y-%m-%d'


def date_iter(start, end):
    '''
    Iterates date from start to end
    start : inclusive. end : exclusive.
    '''
    current = start
    while current < end:
        yield current
        current += timedelta(days = 1)


def get_dates_after_14():
    '''
    Returns the list of the open dates
    '''
    # converts holidays in ISO format string to datetime object
    holidays = [ datetime.strptime(d, Isoformat) for d in ISO_holidays15_16 ]

    opendates = []
    for cur_date in date_iter(First_day, Last_day):
        if cur_date.weekday() not in Weekends and cur_date not in holidays:
            opendates.append(cur_date)

    return opendates


def get_dates_until_14():
    '''
    Extracts dates from a stock data
    Returns the list of the dates
    '''
    work_dir = '.'
    ref_stock = 'IBM'
    symbols = [ref_stock]
    download_stocks(symbols, '1960-01-01', '2015-01-01', work_dir)

    opendates = []
    stock_csv = os.path.join(work_dir, ref_stock + '.csv')
    with open(stock_csv, 'r') as fh_csv:
        reader = csv.reader(fh_csv)
        next(reader)
        for row in reader:
            opendates.append(datetime.strptime(row[0], Isoformat))
    os.remove(stock_csv)

    opendates.sort()

    return opendates


def save_open_dates(filename):
    with open(filename, 'w') as f_cal:
        dates = get_dates_until_14()
        for date in dates:
            print(date.strftime(Isoformat), file=f_cal)
        dates = get_dates_after_14()
        for date in dates:
            print(date.strftime(Isoformat), file=f_cal)


if __name__ == '__main__':
    save_open_dates(Mktcal_csv)
