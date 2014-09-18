#!/usr/bin/env python3

'''
May 10, 2014
@author Hideki Ikeda
Need python 3.x in Anaconda environment
python sample_plot1.py symbol [future_date [history_start_date [history_end_date]]]
The date format is YYYYMMDD'
ex)
python sample_plot1.py IBM 20140513 19950101 20041231
'''

import sys
# Resolve name conflict of 'dateutil'
# The local 'dateutil' conflicts with Anaconda's 'dateutil'
# Need to explicitly load Anaconda's
import imp
spath = sys.path[1:]        # remove the current directly from the search path
fp, pathname, desc = imp.find_module('dateutil', spath)
imp.load_module('dateutil', fp, pathname, desc)
spath = None
fp = None
pathname = None
desc = None
# name conflict resolved
import datetime
import matplotlib.pyplot as plt
from sklearn import linear_model as lm
from stock_value import StockHist, StockValue, LinearAdapter, QuadraticAdapter, CubicAdapter


def plot_stock(hist, a_past, a_future):
    predictor1 = LinearAdapter(lm.LinearRegression())
    stock1 = StockValue(hist, predictor1, 'Linear')
    predictor2 = QuadraticAdapter(lm.LinearRegression())
    stock2 = StockValue(hist, predictor2, 'Quadratic')
    predictor3 = CubicAdapter(lm.LinearRegression())
    stock3 = StockValue(hist, predictor3, 'Cubic')
    
    hist_x = stock1.past_dates
    hist_y = stock1.past_highs
    f1_x = [a_past, a_future]
    f1_y = stock1.future_highs(f1_x)
    
    ord_x0 = a_past.toordinal()
    ord_x1 = a_future.toordinal()
    pts = 20
    delta = (ord_x1 - ord_x0) // pts
    f2_x = [datetime.date.fromordinal(ord_x0 + i * delta) for i in range(0, pts)]
    f2_x.append(a_future)
    f2_y = stock2.future_highs(f2_x)
    
    f3_x = f2_x[:]
    f3_y = stock3.future_highs(f3_x)
    
    print(predictor1._clf.coef_, predictor1._clf.intercept_)
    print(predictor2._clf.coef_, predictor2._clf.intercept_)
    print(predictor3._clf.coef_, predictor3._clf.intercept_)
    print(hist.start_date.toordinal())
    
    plt.plot(hist_x, hist_y, 'ks', f1_x, f1_y, 'r-', f2_x, f2_y, 'g-', f3_x, f3_y, 'b-')
    plt.title(hist.symbol)
    plt.xlabel('Date')
    plt.ylabel('High')
    
    ## legend
    plt.legend(('History', stock1.comment, stock2.comment, stock3.comment), loc='upper left')
    plt.show()


class PseudoStockHist:
    _symbol = 'Pseudo'
    _dates = [
            datetime.date(2001, 1, 1),
            datetime.date(2001, 2, 1),
            datetime.date(2001, 3, 1),
            datetime.date(2001, 4, 1),
            datetime.date(2001, 5, 1),
            datetime.date(2001, 6, 1),
            datetime.date(2001, 7, 1),
            datetime.date(2001, 8, 1),
            datetime.date(2001, 9, 1),
            datetime.date(2001, 10, 1),
            datetime.date(2001, 11, 1),
        ]
    _highs = [ 0.541, 0.909, 0.9899, 0.750, 0.2818, -0.29, -0.79, -1.00, -0.94, -0.58, 0.01 ]
    
    @property
    def symbol(self):
        return self._symbol
        
    @property
    def start_date(self):
        return self._dates[0]
    
    @property
    def end_date(self):
        return self._dates[-1]
    
    @property
    def filename(self):
        return ''
    
    @property
    def dates(self):
        return self._dates[:]
    
    @property
    def highs(self):
        return self._highs[:]


def main(symbol, hist_start, hist_end, future_date):
    hist = StockHist(symbol, hist_start, hist_end)
    #hist = PseudoStockHist()
    delta = datetime.timedelta(days=20*len(hist.dates))
    a_past = hist.dates[0] - (future_date - hist.dates[0]) // 10
    plot_stock(hist, a_past, future_date)


if __name__ == "__main__":
    DATE_FORMAT = '%Y%m%d'
    argc = len(sys.argv)
    if argc < 2:
        print(sys.argv[0] + ' symbol [future_date [history_start_date [history_end_date]]]')
        print('The date format is YYYYMMDD')
        sys.exit(1)
    
    symbol = sys.argv[1]
    future_date = datetime.datetime.strptime(sys.argv[2], DATE_FORMAT).date() if argc >= 3 else datetime.date.today()
    hist_start = datetime.datetime.strptime(sys.argv[3], DATE_FORMAT).date() if argc >= 4 else None
    hist_end = datetime.datetime.strptime(sys.argv[4], DATE_FORMAT).date() if argc >= 5 else None
    main(symbol, hist_start, hist_end, future_date)
