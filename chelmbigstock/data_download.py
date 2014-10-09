#!/usr/bin/env python3

""" Downloads CSV files for stock analysis

Created on Mar 15, 2014

@author: Andy Webber
"""

from urllib import request
import datetime


def stock_url(stock_symbol, day=None, month=None, year=None):
    """ Compose the web URL to download the stock data from Yahoo.com

    This will request data from Jan 1, 1960 to present.
    Mostly for test purposes, you can specify the most recent data you'd
    like to collect, instead of defaulting to the present.

    >>> stock_url('IBM', 31, 1, 2013)
    'http://ichart.finance.yahoo.com/table.csv?s=IBM&amp;d=1&amp;e=31&amp;f=2013&amp;g=d&amp;a=1&amp;b=1&amp;c=1960&amp;ignore=.csv'

    >>> stock_url('IBM') #doctest: +ELLIPSIS
    'http://ichart.finance.yahoo.com/table.csv?s=IBM...

    """

    page = "http://ichart.finance.yahoo.com/table.csv?"
    page = ''.join([page, 's=', stock_symbol])
    now = datetime.datetime.now()
    if day == None:
        day = now.day
    if month == None:
        month = now.month
    if year == None:
        year = now.year
    page = ''.join([page, '&amp;d=', str(month)])
    page = ''.join([page, '&amp;e=', str(day)])
    page = ''.join([page, '&amp;f=', str(year)])
    page = ''.join([page, '&amp;g=d'])
    # Set the start date to Jan 1 1960 and the file will pick up data for as far
    # back as possible
    page = ''.join([page, '&amp;a=1'])
    page = ''.join([page, '&amp;b=1'])
    page = ''.join([page, '&amp;c=1960'])
    page = ''.join([page, '&amp;ignore=.csv'])
    # print(page)
    return(page)


def stock_download(stock_symbol, day=None, month=None, year=None):
    """ Download the stock history into a CSV file.

    File is rows of: 
    date, open, high, low, close, volume and adjusted close

    >>> stock_download('IBM')
    ../data/IBM.csv

    """

    page = stock_url(stock_symbol, day, month, year)
    response = request.urlopen(page)
    csv = response.read()

    # Save the string to a file
    csvstr = str(csv).strip("b'")
    out_file = "../data/"
    out_file = ''.join([out_file, stock_symbol, ".csv"])

    lines = csvstr.split("\\n")
#    #f = open("../data/historical.csv", "w")
    print(out_file)
    f = open(out_file, "w")
    f.write(lines[0] + '\n')  # write out the header
    #next(lines)
    for line in lines[1:]:
        elements = line.split(',')
        if len(elements) > 1 and float(elements[6]):
            f.write(line + "\n")
    f.close()


def download_all():
    """ Download data for each of the stocks in the stock_symbols.txt file

    Each stock is read and the data is stored in <symbol>.csv
    The stocks_read.txt file is updated with each symbol.

    >>> download_all() #doctest: +ELLIPSIS
    ../data/...

    """
    f = open('stock_symbols.txt', 'r')
    fout = open('../data/stocks_read.txt', 'w')
    count_max = 500
    count = 0
    for stock_symbol in f:
        stock_symbol = stock_symbol.strip()
        try:
            stock_download(stock_symbol)
            fout.write(stock_symbol + '\n')
        except:
            print("was not able to read file ", stock_symbol)
        count = count + 1
        if count >= count_max:
            break
    f.close()
    fout.close

    
def main():
    download_all()

if __name__ == "__main__":
    main()
