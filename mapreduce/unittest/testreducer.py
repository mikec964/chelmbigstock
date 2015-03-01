#!/usr/bin/env python

'''
Feb 28, 2015
@author Hideki Ikeda
'''

import os
import sys
import filecmp
import tempfile
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import reducer as target
from testmapper import StdioSwitcher

class TestReducer(unittest.TestCase):
    '''
    Unit tests for reducer
    '''
    data_dir = 'data'
    test_option_path = os.path.join(data_dir, 'test_options.csv')

    def test_reducer(self):
        '''
        test data set 1
        '''
        fn_red_input = os.path.join(self.data_dir, 'red_input1.txt')
        with open(fn_red_input, 'r') as f_red_input:
            fn_red_output = None
            with tempfile.NamedTemporaryFile(mode='w',
                    suffix='.tmp', prefix='red',
                    dir=self.data_dir,
                    delete=False) as f_red_out:
                fn_red_output = f_red_out.name
                with StdioSwitcher(f_red_input, f_red_out):
                    target.reducer()

        # check result
        f_red_out.close()
        fn_expected = os.path.join(self.data_dir, 'red_expected1.txt')
        with open(fn_expected, 'r') as f_exp, open(fn_red_output, 'r') as f_result:
            for lcnt, l_exp in enumerate(f_exp):
                l_result = f_result.readline()

                # check format of the line
                items_exp = l_exp.split('\t')
                items_result = l_result.split('\t')
                self.assertEqual(len(items_exp), len(items_result),
                        'num items: at line {} in {}'.format(lcnt, fn_red_output))

                # check data type
                self.assertEqual(items_exp[0], items_result[0],
                        'Item type: at line {} in {}'.format(lcnt, fn_red_output))

                # check # of prices
                prices_exp = [float(v) for v in items_exp[1].split(',')]
                prices_result = [float(v) for v in items_result[1].split(',')]
                self.assertEqual(len(prices_exp), len(prices_result),
                        'num price at line {} in {}'.format(lcnt, fn_red_output))

                # compare prices
                for i, price in enumerate(prices_exp):
                    self.assertAlmostEqual(price, prices_result[i], 7,
                            'price at line {} in {}'.format(lcnt, fn_red_output))

        # delete output file
        if fn_red_output is not None:
            os.remove(fn_red_output)


if __name__ == '__main__':
    unittest.main()
