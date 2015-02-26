#!/usr/bin/env python
'''
Created on Feb 25, 2015

@author: Hideki Ikeda
'''

import os
import sys
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import mapper as target

class TestMapper(unittest.TestCase):
    '''
    Unit tests for mapper
    '''
    test_option_path = os.path.join('data', 'test_options.csv')

    def test_setup_options(self):
        '''
        test case for setup_options function
        '''
        target.setup_options(self.test_option_path)

        # make sure stock caegorization
        # train data: 0; CV data: 1
        expectedDataSet = { 'MMM':0, 'ABT':0, 'ANF':1, 'ACE':0,
                'ADBE':0, 'AMD':1, 'AES':0, 'AET':0, 'ACS':1, 'AFL':0 }
        self.assertEqual(expectedDataSet, target.Stocks, 'Stock Data Set')

        # make sure dates are correct
        expectedDateFeatures = {
                '2015-01-05':['R0'],
                '2015-01-06':['R0','R1'],
                '2015-01-07':['R0','R1'],
                '2015-01-08':['R0','R1'],
                '2015-01-09':['R0','R1','T0'],
                '2015-01-12':['R0','R1','T0','T1'],
                '2015-01-13':['R0','R1','T0','T1'],
                '2015-01-14':['R0','R1','T0','T1'],
                '2015-01-15':['R1','T0','T1'],
                '2015-01-16':['T0','T1'],
                '2015-01-20':['R0','T0','T1'],
                '2015-01-21':['R1','T0','T1'],
                '2015-01-22':['T1'],
                '2015-01-26':['T0'],
                '2015-01-27':['T1'] }
        # first, check dates only
        expected = set(expectedDatesFeatures.keys())
        result = set(target.Dates.keys())
        self.assertEqual(expected, result, 'Dates')
        # next, check each date
        for key in expectedDates:
            expected = set(expectedDatesFeatures[key])
            result = set(target.Dates[key])
            self.assertEqual(expected, result, 'reference/test')


if __name__ == '__main__':
    unittest.main()
