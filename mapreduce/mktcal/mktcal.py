#!/usr/bin/env python3

'''
mktsched.py
Saves open dates of the stock market from 1960 to 2016
Takes the dates between 1960 and 2014 from the actual data

Data source:
    the holidays in 2015 and 2016
    https://www.nyse.com/markets/hours-calendars

Result:
    mktsched.csv
'''

import sys
import os
import datetime
import csv

sys.path.append('..')
from download_data import download_stocks

Holidays15_16 = [
    '2015-01-01',   # New Years Day
    '2015-01-19',   # Martin Luther King, Jr. Day
    '2015-02-16',   # Washington's Birthday
    '2015-04-03',   # Good Friday
    '2015-05-25',   # Memorial Day
    '2015-07-03',   # Independence Day (observed)
    '2015-09-07',   # Labor Day
    '2015-11-26',   # Thanksgiving Day
    '2015-12-25',   # Christmas Day
    '2016-01-01',
    '2016-01-18',
    '2016-02-15',
    '2016-03-25',
    '2016-05-30',
    '2016-07-04',
    '2016-09-05',
    '2016-11-24',
    '2016-12-26'    # observed
    ]

def get_dates_upto_14():
    return []


def get_dates_after_14():
    return []


def save_open_days(filename):
    with open(filename, 'w') as f_sched:
        dates = get_dates_upto_14()
        for date in dates:

