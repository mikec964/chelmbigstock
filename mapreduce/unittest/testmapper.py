#!/usr/bin/env python
'''
Created on Feb 25, 2015

@author: Hideki Ikeda
'''

import os
import sys
import ast
import tempfile
import filecmp
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import mapper as target

class StdioSwitcher(object):
    """
    Utility to set / reset stdin and stdout
    """
    def __init__(self, new_stdin, new_stdout):
        """
        Parameters:
            new_stdin:  File object to set to system stdin.
            new_stdout: File object to set to system stdout.
        """
        self._stdin = new_stdin
        self._stdout = new_stdout

    def __enter__(self):
        swap_buf = sys.stdin
        sys.stdin = self._stdin
        self._stdin = swap_buf

        swap_buf = sys.stdout
        sys.stdout = self._stdout
        self._stdout = swap_buf

    def __exit__(self, *args):
        sys.stdin = self._stdin
        sys.stdout = self._stdout


def read_test_data(filename):
    '''
    Read a Python expression in a file and return the evaluated value.
    '''
    with open(filename, 'r') as f_data:
        data = f_data.read()
    return ast.literal_eval(data)


class TestMapper(unittest.TestCase):
    '''
    Unit tests for mapper
    '''
    data_dir = 'data'
    test_option_path = os.path.join(data_dir, 'test_options.csv')

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

    def test_mapper(self):
        fn_stocks = os.path.join(self.data_dir, 'map_stock1.py')
        target.Stocks = read_test_data(fn_stocks)
        fn_dates = os.path.join(self.data_dir, 'map_date1.py')
        target.Dates = read_test_data(fn_dates)

        fn_map_input = os.path.join(self.data_dir, 'test_stock.csv')
        with open(fn_map_input, 'r') as f_map_input:
            fn_map_output = None
            with tempfile.NamedTemporaryFile(mode='w',
                    suffix='.tmp', prefix='map',
                    dir=self.data_dir,
                    delete=False) as f_map_out:
                fn_map_output = f_map_out.name
                with StdioSwitcher(f_map_input, f_map_out):
                    target.mapper()
            fn_expected = os.path.join(self.data_dir, 'map_expected1.txt')

            # check result
            self.assertTrue(filecmp.cmp(fn_expected, fn_map_output),
                    'check {}'.format(fn_map_output))

            # delete output file
            if fn_map_output is not None:
                os.remove(fn_map_output)


if __name__ == '__main__':
    unittest.main()
