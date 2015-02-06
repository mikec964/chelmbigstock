#!/usr/bin/env python3

'''
mktcal.py
Saves open dates of the stock market from 1960 to 2016
Takes the dates between 1960 and 2014 from the actual data

Source file:
    holidays.txt

Result:
    mktcal.csv

Jan 21, 2015
@author Hideki Ikeda
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


def get_holidays_after_14():
    holidays = []
    # Holidays in 2015 and after in ISO 8601 format
    with open('holidays.txt', 'r') as f_holidays:
        for line in f_holidays:
            date_comment = line.split('#', 1)
            if len(date_comment) > 0:
                date_str = date_comment[0].strip()
                if len(date_str) > 0:
                    holidays.append(date_comment[0].strip())

    return holidays



def get_dates_after_14():
    '''
    Returns the list of the open dates
    '''
    # converts holidays in ISO format string to datetime object
    holidays = [ datetime.strptime(d, Isoformat) for d in get_holidays_after_14() ]

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
