#

'''
Apr 28, 2014
@author Hideki Ikeda
Unit test for the StockHist class in stock_value.py
'''

import os
import sys
from datetime import date, datetime, timedelta
import shutil
import csv
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
from chelmbigstock import stock_value


class TestStockHist(unittest.TestCase):
    """
        Tests for stock_value
    """

    _data_no_end_date = [
        # [ symbol, start_date param, expected start_date ]
            ['IBM', None, date.min],
            ['IBM', date(2014, 4, 27), date(2014, 4, 27)]
        ]

    _data_dates = [
        # [ symbol, start_date param, end_date param, start_date expected, end_date expecte, API URL ]
        #                             ^^^^^^^^ end_date must be non-None
            ['IBM', date(2001, 4, 27), date(2013, 7, 18), date(2001, 4, 27), date(2013, 7 ,18), 'http://ichart.yahoo.com/table.csv?s=IBM&a=3&b=27&c=2001&d=6&e=18&f=2013&g=w&ignore=.csv'],
            ['IBM', None, date(1965, 6, 14), date.min, date(1965, 6, 14), 'http://ichart.yahoo.com/table.csv?s=IBM&d=5&e=14&f=1965&g=w&ignore=.csv']
        ]

    _data_contents = [
        # [ symbol, start_date param, end_date param, expected path ]
            [ 'MSFT', date(2011, 7, 18), date(2011, 9, 12), 'case1_MSFT' ]
        ]
    
    _data_cache = [
        # [ symbol, start_date, end_date ]
            [ 'HPQ', date(1993, 6, 14), date(1993, 7, 19) ]
        ]

    @classmethod
    def setUpClass(cls):
        cls._my_path = os.path.abspath(os.path.dirname(__file__))
        cls._result_path = os.path.join(cls._my_path, 'result')
        cls._expected_path = os.path.join(cls._my_path, 'expected')
        os.mkdir(cls._result_path)
        stock_value.StockHist.default_path = cls._result_path

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._result_path)

    def test_no_dates(self):
        for test_data in self._data_no_end_date:
            symbol, start_date, expected_start = test_data
            expected_end = date.today() - timedelta(days=1)
            if start_date == None:
                stock = stock_value.StockHist(symbol)
            else:
                stock = stock_value.StockHist(symbol, start_date)
            self.assertEqual(symbol, stock.symbol)
            self.assertEqual(expected_start, stock.start_date)
            self.assertEqual(expected_end, stock.end_date)

    def test_dates(self):
        for test_data in self._data_dates:
            symbol, start_date, end_date, expected_start, expected_end, expected_url = test_data
            stock = stock_value.StockHist(symbol, start_date, end_date)
            self.assertEqual(symbol, stock.symbol)
            self.assertEqual(expected_start, stock.start_date)
            self.assertEqual(expected_end, stock.end_date)
            self.assertEqual(expected_url, stock._make_url())

    def test_content(self):
        for test_data in self._data_contents:
            symbol, start_date, end_date, expected_file = test_data
            expected_path = os.path.join(self._expected_path, expected_file)
            date_list = []
            high_list = []
            with open(expected_path, newline='') as f_expected:
                exp_reader = csv.reader(f_expected)
                next(exp_reader)     # skip the title row
                for row in exp_reader:
                    date_list.append(datetime.strptime(row[0], '%Y-%m-%d').date())
                    high_list.append(float(row[2]))
                date_list.reverse()  # Yahoo returns newest first; we need oldest first
                high_list.reverse()
            stock = stock_value.StockHist(symbol, start_date, end_date)
            self.assertEqual(date_list, stock.dates)
            self.assertEqual(high_list, stock.highs)
    
    def test_cache(self):
        pass # todo
        for test_data in self._data_cache:
            symbol, start_date, end_date = test_data
            stock = stock_value.StockHist(symbol, start_date, end_date)
            dates = stock.dates
            highs = stock.highs
            stock = None        # make sure we are going to use a new instance
            stock = stock_value.StockHist(symbol, start_date, end_date)
            self.assertEqual(dates, stock.dates)
            self.assertEqual(highs, stock.highs)



if __name__ == "__main__":
    unittest.main()
