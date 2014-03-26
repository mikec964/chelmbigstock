import unittest

from chelmbigstock.Stock import Stock

class test_stock(unittest.TestCase):
    '''Tests for the stock object.

    To run these tests, cd to the PARENT of chelmbigstock, then:
    python -m chelmbigstock.tests.stocktests

    '''

    def test_load_data(self):
        '''Make sure at least two data points are loaded'''

        this_stock = Stock('ibm', 'chelmbigstock/data')
        this_stock.populate()
        self.assertIsNotNone(this_stock.dates[0])
        self.assertIsNotNone(this_stock.values[0])
        self.assertIsNotNone(this_stock.dates[1])
        self.assertIsNotNone(this_stock.values[1])

if __name__ == '__main__':
    unittest.main()
