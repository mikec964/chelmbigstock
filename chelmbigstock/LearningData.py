"""
LearningData object used in chelmbigstock

@Author: Andy Webber
Created: March 1, 2014
"""

import sys

from Stock import Stock
import dateutl

class LearningData(object):
    """ The  object of data. This object will be composed
        from an array of stocks and dates. It will consist
        of both input data (xs) and output data (ys). 
        """
        
    def __init__(self):
        """ The data is originally two empty array. The first array will be
            two dimensional input array called x that is m x n. The second
            array called y is the output array that is m x 1. The number of
            stocks is denoted by m and the number of dates used for learning
            is denoted by n. All notation is to be consistent with the
            Coursera Machine Learning course as much as possible.
            """
            
        self.X = []
        self.y = []
        self.m = 0
        self.n = 0

    def construct(self, stocks, date, future_day, features):
        """ This method constructs the data arrays. The inputs are an array
            of m stocks and an array of dates. The first element of dates
            is a character string to tell the referenced date such as
            '1/1/1980'. The second element is an array of n-1 integers
            telling the trading days to use to populate the input array.
            The final value is the integer value of the future date.
            An input value of ['1/1/1980',[50, 100, 150], 50] means
            we are using '1/1/1980' as our reference date along with the
            dates 50 trading days, 100 trading days and 150 trading days
            in the past for a total of 4 input values i.e. n = 4. From
            these values we are looking to anticipate the stock value
            50 days in the future. 

            The value of m for the data is expected to be m but not all stocks
            go back as far in time. If 1/1/1980 is the reference date and
            gs only went public in 1999 this stock will be left out of the
            Data object.
            """
            
        self.X = []
        self.y = []
        self.n = len(features)
        self.m = 0
        self.append(stocks, date, future_day, features)
        
    def append(self, stocks, date, future_day, features):
        """ This method appends data to a learningData object
            It is meant to be called from construct
            for a new object or from outside the method to append to an existing
            """
        if (self.n != len(features)):
            sys.exit("trying to append to wrong size data set")
        
 #       reference_date = dates[0]
        num_stocks = len(stocks)
        
        for i in range(0, num_stocks):
            # Before we add a stock we must makes sure the dates go back far enough
            # i_day is the index of the reference date. We need all this plus the
            # maximum of the history being used in order to use this stock
            i_day = dateutl.find_ref_date_idx(stocks[i], date)
            elements = len(stocks[i].dates) # This is the number of entries in stocks
            first_day_avail = stocks[i].dates[elements-1]
            i_day_first_avail = dateutl.find_ref_date_idx(stocks[i], first_day_avail)
            if (i_day < i_day_first_avail) and (i_day != -1): 
                self.m += 1
                temp_values = []
                if 'rsi' in features:
                    temp_values.append(stocks[i].rsi[i_day])
                if 'tsi' in features:
                    temp_values.append(stocks[i].tsi[i_day])
                if 'ppo' in features:
                    temp_values.append(stocks[i].ppo[i_day])
                if 'adx' in features:
                    temp_values.append(stocks[i].adx[i_day])
                if 'dip14' in features:
                    temp_values.append(stocks[i].adx[i_day])
                if 'dim14' in features:
                    temp_values.append(stocks[i].adx[i_day])
                if 'cci' in features:
                    temp_values.append(stocks[i].cci[i_day])
                if 'cmo' in features:
                    temp_values.append(stocks[i].cmo[i_day])
                if 'mfi' in features:
                    temp_values.append(stocks[i].mfi[i_day])
                if 'natr' in features:
                    temp_values.append(stocks[i].natr[i_day])
                if 'roc' in features:
                    temp_values.append(stocks[i].roc[i_day])
                if 'stoch' in features:
                    temp_values.append(stocks[i].stoch[i_day])
                if 'uo' in features:
                    temp_values.append(stocks[i].uo[i_day])
                self.X.append(temp_values)
                # Now get the future value and append it to self.y
                # For classification problem assign a one to stock that has gone
                # up and 0 to stock that has gone down
                adjusted_value = stocks[i].close[i_day - future_day]/ \
                    stocks[i].close[i_day]
                if adjusted_value >= 1:
                    self.y.append(1)
                else:
                    self.y.append(0)
                                   