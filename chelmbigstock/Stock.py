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
        self.vopen = [] # opening value. cannot use "open"
        self.high = []
        self.low = []
        self.close = []
        self.volume = []
        self.rsi = []
        self.tsi = []
        self.ppo = []
        self.dip14 = []
        self.dim14 = []
        self.adx = []
        self.cci = []
        self.cmo = []
        self.mfi = []
        self.natr = []
        self.roc = []
        self.stoch = []
        self.uo = []
        
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
        
    def sma(a, N):
        """ This method calculates the simple moving average of an 
        array, a and period N. Because stock values are in reverse
        chronological order the input and outputs will also be in
        reverse chronological order. """
        
        """ Go through the original N days to initialize ave_a"""
        lengtha = len(a)
        a_sma = np.zeros(lengtha)
        a_sum = 0.0
        for iday in range(lengtha-1, lengtha-(N+1),-1):
            a_sum += a[iday]
            a_sma[iday] = a_sum/(lengtha - iday)
        
        for iday in range(lengtha-(N+1),-1,-1):
            a_sum += a[iday]
            a_sum -= a[iday+N]
            a_sma[iday] = a_sum/N
        return a_sma
        
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
            this_stock.adx_calc()
            this_stock.cci_calc()
            this_stock.cmo_calc()
            this_stock.mfi_calc()
            this_stock.natr_calc()
            this_stock.roc_calc()
            this_stock.stoch_calc()
            this_stock.uo_calc()
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
            vopen = []
            high = []
            low = []
            close = []
            volume = []
            for row in reader:
                try:
                    date = dateutl.days_since_1900(row[0])
                    """ adjustment is for splits. Everything must be 
                        be multiplied by the ration of the adjusted close
                        to the actual close """
                    adjustment = float(row[6])/float(row[4])
                    # Data in the csv files are in reverse cronological order,
                    dates.append(date) 
                    vopen.append(float(row[1])*adjustment)
                    high.append(float(row[2])*adjustment)
                    low.append(float(row[3])*adjustment)
                    close.append(float(row[4])*adjustment)
                    volume.append(float(row[5]))
                except:
                    continue
             #       print("empty row")
        self.dates, self.vopen, self.high, self.low, self.close,self.volume = \
            dates, vopen, high, low, close, volume
    def rsi_calc(self):
        """ This method calculates the relative strength index of the stock.
            Calculations are based on a 14 day period"""
        
        """ Go through the original 14 days to initialize ave_gain and 
        ave_loss """
        self.rsi = np.zeros(len(self.dates))
        ave_gain = 0
        ave_loss = 0
        last_val = self.close[len(self.dates)-1]
        oneO14 = 1/14
        for iday in range(len(self.dates)-2,len(self.dates)-15,-1):
            gain = self.close[iday] - last_val
            if gain > 0:
                ave_gain += gain
            else:
                ave_loss -= gain
            last_val = self.close[iday]
            
        """ Now go through rest of data field to assign relative strength """
        for iday in range(len(self.dates)-16, -1, -1):
            gain = self.close[iday] - last_val
            if gain > 0:
                ave_gain = (ave_gain*13 + gain)*oneO14
                ave_loss = (ave_loss*13)*oneO14
            else:
                ave_gain = (ave_gain*13)*oneO14
                ave_loss = (ave_loss*13 - gain)*oneO14
            last_val = self.close[iday]
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
        vals = self.close
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
        vals = self.close
        num_array = Stock.ema(vals, s) - Stock.ema(vals, r)
        denom_array = Stock.ema(vals, r)
        """ The ema function sets first elements to zero so division will 
            give nan. Get rid of them with the nan_to_num method """
        self.ppo = np.nan_to_num(num_array/denom_array)
        self.ppo[self.ppo >= 1E300] = 0
        return
        
    def adx_calc(self):
        """ This method calculates the positive and negative directional 
            movement indicies and average directional index of the stock.
            Periods of 14 days are chosen as suggested by Wilder. Note that
            Wilders periods of 14 corresponds with a ema of 27. Data is in
            reverse chronological order so iday+1 is earlier day"""
        """First calculate true range """
        TR1 = np.zeros(len(self.high)-1)
        for iday in range(len(self.high)-1):
            a = self.high[iday] - self.low[iday]
            b = abs(self.high[iday] - self.close[iday+1])
            c = abs(self.low[iday] - self.close[iday+1])
            TR1[iday] = max(a, b, c)
        """initialize directional movement 1 (positive and negative) then calc"""
        days = len(self.close)
        DMP1 = np.zeros(days-1)
        DMM1 = np.zeros(days-1)
        for iday in range(0, days-2):
            pls_change = self.high[iday] - self.high[iday+1]
            mns_change = self.low[iday+1] - self.low[iday]
            if (pls_change > mns_change and pls_change > 0.0):
                DMP1[iday] = pls_change
            elif (pls_change > 0):
                DMM1[iday] = mns_change
        
        """ Do 14 day Wilder EMA on data which corresponds to 27 day EMA """
        TR14 = Stock.ema(TR1,27)
        DMP14 = Stock.ema(DMP1,27)
        DMM14 = Stock.ema(DMM1,27)
        
        """ Caclulate the directional indicies """
        self.dip14 = np.nan_to_num(DMP14/TR14)
        self.dip14[self.dip14 > 1E300] = 0
        self.dim14 = np.nan_to_num(DMM14/TR14)
        self.dim14[self.dim14 > 1E300] = 0
        
        """ Calculate ADX """
        dx = abs(self.dip14 - self.dim14)/(self.dip14 + self.dim14)
        dx = np.nan_to_num(dx)
        dx[dx >= 1E300] = 0
        self.adx = Stock.ema(dx,27)
        return
        
    def cci_calc(self):
        """ This method calculates the commodity channel index of the stock."""
            
        TP = (np.array(self.high)+np.array(self.low)+np.array(self.close))/3.0
        TPMA = Stock.sma(TP,20)
        
        deviation = np.zeros(len(TP))
        
        for iday in range(len(TP)-20):
            dev_sum = 0.0
            TPMA_iday = TPMA[iday]
            for i in range(0,20):
                dev_sum += abs(TP[iday+i] - TPMA_iday)
            dev_sum = dev_sum/20.0
            deviation[iday] = dev_sum
        
        self.cci = (TP - TPMA)/(0.015 * deviation)
        self.cci = np.nan_to_num(self.cci)
        self.cci[self.cci >= 1E300] = 0
        
        return
        
    def cmo_calc(self):
        """ This method calculates the chande Momentum Oscillator of the 
            stock. Using the default span of 9 days"""
            
        days = len(self.close)-1
        up = np.zeros(days)
        down = np.zeros(days)
        for iday in range(days):
            """ price change, data is in reverse chronological order
                diff is positive for up days and negative for down days"""
            diff = self.close[iday] - self.close[iday+1]
            if (diff > 0):
                up[iday] = diff
            else:
                down[iday] = -1.0 * diff
        su = Stock.sma(up,9)
        sd = Stock.sma(down,9)
        
        
        
        self.cmo = (su - sd)/(su + sd)
        self.cmo = np.nan_to_num(self.cmo)
        self.cmo[self.cmo >= 1E300] = 0
        
        return
        
    def mfi_calc(self):
        """ This method calculates the money flow index index of the stock."""
            
        TP = (np.array(self.high)+np.array(self.low)+np.array(self.close))/3.0
        
        mfpos1 = np.zeros(len(TP)-1)
        mfneg1 = np.zeros(len(TP)-1)
             
        for iday in range(len(TP)-1):
            diff = TP[iday] - TP[iday+1]
            if (diff > 0):
                mfpos1[iday] = diff * self.volume[iday]
            else:
                mfneg1[iday] = -1.0 * diff * self.volume[iday]
                
        mfpos14 = Stock.sma(mfpos1,14)
        mfneg14 = Stock.sma(mfneg1,14)
        mfneg14[mfneg14 < 0] = 0.0
        
        mfr = mfpos14/mfneg14
        mfr[mfneg14 == 0] = 1E299
        mfr[mfr >= 1E300] = 0
        
        self.mfi = 100 - 100/(1 + mfr)
        
        return
        
    def natr_calc(self):
        """ This method calculates the Normalized average true range"""
        """First calculate true range """
        TR1 = np.zeros(len(self.high)-1)
        for iday in range(len(self.high)-1):
            a = self.high[iday] - self.low[iday]
            b = abs(self.high[iday] - self.close[iday+1])
            c = abs(self.low[iday] - self.close[iday+1])
            TR1[iday] = max(a, b, c)
        
        
        """ Do 14 day Wilder EMA on data which corresponds to 27 day EMA """
        TR14 = Stock.ema(TR1,27)
        close = self.close
        close = np.delete(close,-1)
        self.natr = 100 * TR14/close
        return
        
    def roc_calc(self):
        """ This method calculates the percentage up or down from 12 days
            ago (Rate of change)"""
        roc = np.zeros(len(self.close)-12)
        for iday in range(len(self.close)-12):
            roc[iday] = 100 * (self.close[iday] - self.close[iday+12]) \
                    /self.close[iday+12]

        self.roc = roc
        return
        
    def stoch_calc(self):
        """ This method calculates the Stochastic (STOCH)"""
        high = self.high
        low = self.low
        percent_k = np.zeros(len(self.close)-14)
    
        for iday in range(len(self.close)-14):
            highest_high = np.max(high[iday:iday+14])
            lowest_low = np.min(low[iday:iday+14])
            percent_k[iday] = (self.close[iday]-lowest_low)/(highest_high-lowest_low)
#        percent_k[percent_k == nan] = 1.0
        where_are_NaNs = np.isnan(percent_k)
        percent_k[where_are_NaNs] = 1

        self.stoch = 100 * Stock.sma(percent_k,3)
        return
        
    def uo_calc(self):
        """ This method calculates the Ultimate Ocilator """
        """First calculate true range """
        TR = np.zeros(len(self.high)-1)
        BP = np.zeros(len(self.high)-1)
        for iday in range(len(self.high)-1):
            low = min(self.low[iday], self.close[iday+1])
            high = max(self.high[iday], self.close[iday+1])
            BP[iday] = self.close[iday] - low
            TR[iday] = high - low
        
        
        """ Calculate 7, 14 and 28 day moving averages """
        ave7 = Stock.sma(BP,7)/Stock.sma(TR,7)
        ave14 = Stock.sma(BP,14)/Stock.sma(TR,14)
        ave28 = Stock.sma(BP,28)/Stock.sma(TR,28)
        
        inv7 = 1.0/7.0
        self.uo = 100 * inv7 * (4.0*ave7 + 2.0*ave14 + ave28)
        self.uo = np.nan_to_num(self.uo)
        return
        