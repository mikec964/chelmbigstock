"""
Stock object used in chelmbigstock

@Author: Andy Webber
Created: March 1, 2014
"""

import os
import csv

import dateutl
import numpy as np


class Stock(object):
    """A stock has a symbol and a list of date/value pairs"""
    
    def __init__(self, name, directory):
        """ The creation of a stock takes in a name assuming it is a
            character string and creates arrays to store dates and
            values
            """
            
        self.name = name
        self.directory = directory
        self.length = 0
        self.dates = []
        self.values = []
        self.rsi = []
        self.ema = []
        
    @classmethod
    def read_stocks(cls, stock_file, max_stocks):
        """ This method takes in a file of the stock symbols to be read and 
            returns an array of Stock objects. """
            
        stocks = []
        f = open(stock_file, 'r')
        count = 0
        for stock_symbol in f:
            stock_symbol = stock_symbol.strip()
            this_stock = Stock(stock_symbol, '../data')
            this_stock.populate()
            this_stock.rsi_calc()
            stocks.append(this_stock)
            count = count + 1
            if count >= max_stocks:
                break
        
        return(stocks)

    def populate(self):
        """ This method populates the dates and values of the stock.

        The name of the file is the name of the stock and the directory
        is already known so no arguments are needed
        """

        file = os.path.join(self.directory, self.name + '.csv')
        with open(file, 'U') as f:
            reader = csv.reader(f)
            headers = f.readline()
            dates = []
            values = []
            for row in reader:
                try:
                    date = dateutl.days_since_1900(row[0])
                    # Data in the csv files are in reverse cronological order,
                    # insert is used rather than append to put them into cronological
                    dates.append(date) 
                    values.append(float(row[6]))
                except:
                    continue
             #       print("empty row")
        self.dates, self.values = dates, values
    def rsi_calc(self):
        """ This method calculates the relative strength index of the stock.
            Calculations are based on a 14 day period"""
        
        """ Go through the original 14 days to initialize ave_gain and 
        ave_loss """
        self.rsi = np.zeros(len(self.dates))
        ave_gain = 0
        ave_loss = 0
        last_val = self.values[len(self.dates)-1]
        oneO14 = 1/14
        for iday in range(len(self.dates)-2,len(self.dates)-15,-1):
            gain = self.values[iday] - last_val
            if gain > 0:
                ave_gain += gain
            else:
                ave_loss -= gain
            last_val = self.values[iday]
            
        """ Now go through rest of data field to assign relative strength """
        for iday in range(len(self.dates)-16, 0, -1):
            gain = self.values[iday] - last_val
            if gain > 0:
                ave_gain = (ave_gain*13 + gain)*oneO14
                ave_loss = (ave_loss*13)*oneO14
            else:
                ave_gain = (ave_gain*13)*oneO14
                ave_loss = (ave_loss*13 - gain)*oneO14
            last_val = self.values[iday]
            if ave_loss > 0:
                RS = ave_gain/ave_loss
                self.rsi[iday] = 100 - 100/(1.0 + RS)
            else:
                self.rsi[iday] = 100
    def ema_calc(self):
        """ This method calculates the exponential moving average of the stock.
            Here we use N=9, or alpha = 0.2 as suggested in Shah"""
        
        """ Go through the original 14 days to initialize ave_gain and 
        ave_loss """
        self.ema = np.zeros(len(self.dates))
        """ seed first 
        self.ema[len(self.dates)-1] = self.values[len(self.dates)-1]
        ave_gain = 0
        ave_loss = 0
        last_val = self.values[len(self.dates)-1]
        oneO14 = 1/14
        for iday in range(len(self.dates)-2,len(self.dates)-15,-1):
            gain = self.values[iday] - last_val
            if gain > 0:
                ave_gain += gain
            else:
                ave_loss -= gain
            last_val = self.values[iday]
            
        """ """Now go through rest of data field to assign relative strength""" """
        for iday in range(len(self.dates)-16, 0, -1):
            gain = self.values[iday] - last_val
            if gain > 0:
                ave_gain = (ave_gain*13 + gain)*oneO14
                ave_loss = (ave_loss*13)*oneO14
            else:
                ave_gain = (ave_gain*13)*oneO14
                ave_loss = (ave_loss*13 - gain)*oneO14
            last_val = self.values[iday]
            if ave_loss > 0:
                RS = ave_gain/ave_loss
                self.rsi[iday] = 100 - 100/(1.0 + RS)
            else:
                self.rsi[iday] = 100 """