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
        self.tsi = []
        self.ppo = []
        
    @staticmethod
    def ema(a, N):
        """ This method calculates the exponential moving average of an 
        array, a and period N. Because stock values are in reverse
        chronological order the input and outputs will also be in
        reverse chronological order. """
        
        alpha = 2.0/(N+1)
        """ Go through the original N days to initialize ave_a"""
        lengtha = len(a)
        a_ema = np.zeros(lengtha)
        a_sum = 0.0
        for iday in range(lengtha-1, lengtha-(N+1),-1):
            a_sum += a[iday]
            a_ema[lengtha-N] = a_sum/N
        
        for iday in range(lengtha-(N+1),-1,-1):
            a_ema[iday] = a[iday]*alpha + a_ema[iday+1]*(1.0-alpha)
        return a_ema
        
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
            this_stock.tsi_calc()
            this_stock.ppo_calc()
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
        for iday in range(len(self.dates)-16, -1, -1):
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
                self.rsi[iday] = 10
        return
        
    def tsi_calc(self):
        """ This method calculates the true strength index of the stock.
            It uses the ema method and a long period of 25 and short 
            period of 13 as suggested in wikipedia """
        r = 25
        s = 13
        vals = self.values
        days = len(vals)
        diff = np.zeros(days-1)
        for iday in range(0,days-2):
            diff[iday] = vals[iday] - vals[iday+1]
        num_array = Stock.ema(diff, r)
        num_array = Stock.ema(num_array, s)
        denom_array = Stock.ema(np.abs(diff), r)
        denom_array = Stock.ema(denom_array, s)
        """ The ema function sets first elements to zero so division will 
            give nan. Get rid of them with the nan_to_num method """
        self.tsi = np.nan_to_num(num_array/denom_array)
        return
        
    def ppo_calc(self):
        """ This method calculates the percentage price ocillator of the stock.
            It uses the ema method and a long period of 26 and short 
            period of 12 as suggested in wikipedia """
        r = 26
        s = 12
        vals = self.values
        num_array = Stock.ema(vals, s) - Stock.ema(vals, r)
        denom_array = Stock.ema(vals, r)
        """ The ema function sets first elements to zero so division will 
            give nan. Get rid of them with the nan_to_num method """
        self.ppo = np.nan_to_num(num_array/denom_array)
        self.ppo[self.ppo >= 1E300] = 0
        return
        
    
        