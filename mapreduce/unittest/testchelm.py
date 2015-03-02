#!/usr/bin/env python

'''
Mar 2, 2015
@author Hideki Ikeda
'''

import os
import sys
import ast
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import chelmbigstock as target

class StockData(object):
    '''
    Store test stock data from a data file
    Properies:
        X : 2D feature data
        y : 1D target data
    '''
    def __init__(self, filename):
        with open(filename, 'r') as f_data:
            txt = f_data.read()
            self.X, self.y = ast.literal_eval(txt)

    @property
    def m(self):
        return len(self.X[0])

    @property
    def n(self):
        return len(self.y)


class TestChelmbigstock(unittest.TestCase):
    '''
    Unit test cases for stock prediction
    '''
    data_dir = 'data'
    test_option_path = os.path.join(data_dir, 'test_options.csv')

    def assertEqualStockData(self, expected, result, msg):
        '''
        Compare expected stock data and result and
        raise assert if they are not equal.
        '''
        self.assertEqual(expected.m, result.m, '{} m={}'.format(msg, result.m))
        self.assertEqual(expected.n, result.n, '{} n={}'.format(msg, result.n))
        for i, x in enumerate(expected.X):
            for j, ve in enumerate(x):
                vr = result.X[i][j]
                self.assertAlmostEqual(ve, vr, 7,
                        '{}: X[{},{}]={}'.format(msg, i, j, vr))
        for i, ve in enumerate(expected.y):
            vr = result.y[i]
            self.assertAlmostEqual(ve, vr, 7,
                    '{}: y[{}]={}'.format(msg, i, vr))


    def test_stockDataFactory(self):
        '''
        Test normal case
        '''
        fn_tr = os.path.join(self.data_dir, 'chelm_TR1.py')
        fn_cv = os.path.join(self.data_dir, 'chelm_CV1.py')
        fn_te = os.path.join(self.data_dir, 'chelm_TE1.py')
        expected_tr = StockData(fn_tr)
        expected_cv = StockData(fn_cv)
        expected_te = StockData(fn_te)

        fn_data = os.path.join(self.data_dir, 'red_expected1.txt')
        result_tr, result_cv, result_te = target.stockDataFactory(fn_data)

        self.assertEqualStockData(expected_tr, result_tr, 'TR')
        self.assertEqualStockData(expected_cv, result_cv, 'CV')
        self.assertEqualStockData(expected_te, result_te, 'TE')


if __name__ == '__main__':
    unittest.main()
