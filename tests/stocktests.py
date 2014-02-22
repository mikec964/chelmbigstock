import unittest

from ..chelmbigstock.stock import Stock

class test_stock(unittest.TestCase):
    '''Tests for the stock object.

    To run these tests, cd to the PARENT of chelmbigstock, then:
    python -m chelmbigstock.tests.read_file

    '''

    def test_load_data(self):
        '''Make sure at least one data point is loaded'''

        this_stock = Stock('ibm', 'chelmbigstock/data')
        this_stock.populate()
        self.assertIsNotNone(this_stock.dates[0])
        self.assertIsNotNone(this_stock.values[0])

if __name__ == '__main__':
    unittest.main()
