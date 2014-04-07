#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.abspath('..'))

from chelmbigstock.data_download import *

import unittest

# You can run all tests in this directory with:
# python -m unittest discover -p '*tests.py'

class test_data_download(unittest.TestCase):
    """ Tests for the data_download module"""

    def test_stock_url(self):
        url = stock_url('apl')
        expected_url = 'http://ichart.finance.yahoo.com/table.csv?s=apl&amp;d=4&amp;e=7&amp;f=2014&amp;g=d&amp;a=1&amp;b=1&amp;c=1960&amp;ignore=.csv'
        # print(url)
        # check the URL before today's date
        # print(url[0:47])
        self.assertEqual(url[0:47],expected_url[0:47])
        # check the URL after today's date
        # print(url[-51:])
        self.assertEqual(url[-51:],expected_url[-51:])


if __name__ == '__main__':
    unittest.main()
