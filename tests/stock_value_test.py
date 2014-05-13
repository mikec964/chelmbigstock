#

'''
May,08, 2014
@author Hideki Ikeda
Unit test for the StockValue class in stock_value.py
'''

import os
import sys
from datetime import date, datetime, timedelta
import shutil
import unittest
from sklearn import linear_model

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
from chelmbigstock import stock_value


class TestStockValue(unittest.TestCase):
    """
    Unit tests for the StockValue class
    StockValue uses the StockHist and LinearAdapter classes.
    Make sure these classes work before testing StockValue
    """

    _test_data = [
        # [ symbol, start_date, end_date ]
            [ 'HPQ', date(1993, 6, 14), date(1993, 7, 19) ],    # small data
            [ 'MSFT', None, None ]                              # large data
        ]

    @classmethod
    def setUpClass(cls):
        cls._my_path = os.path.abspath(os.path.dirname(__file__))
        cls._result_path = os.path.join(cls._my_path, 'result')
        cls._expected_path = os.path.join(cls._my_path, 'expected')
        os.mkdir(cls._result_path)
        stock_value.StockHist.default_path = cls._result_path
        cls._predictor = stock_value.LinearAdapter(linear_model.Ridge(alpha=0.1, fit_intercept=False))
        cls._comment = 'Ridge alpha=0.1'
        cls._histories = []
        for symbol, sdate, edate in cls._test_data:
            cls._histories.append(stock_value.StockHist(symbol, sdate, edate))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._result_path)

    def test_past(self):
        for hist in self._histories:
            stock = stock_value.StockValue(hist, self._predictor, self._comment)
            # test dates
            expected = hist.dates
            result = stock.past_dates
            self.assertEqual(expected, result)
            # test highs
            expected = hist.highs
            result = stock.past_highs
            self.assertEqual(expected, result)

    def test_comment(self):
        stock = stock_value.StockValue(self._histories[0], self._predictor, self._comment)
        self.assertEqual(self._comment, stock.comment)

    def test_future(self):
        future_dates = [ date.today() + timedelta(days=1), date.today() + timedelta(days=30) ]
        for hist in self._histories:
            stock = stock_value.StockValue(hist, self._predictor, self._comment)
            result = stock.future_highs(future_dates)
            self.assertEqual(len(future_dates), len(result))



if __name__ == "__main__":
    unittest.main()
