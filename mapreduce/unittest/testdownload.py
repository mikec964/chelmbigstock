#!/usr/bin/env python
'''
Created on Feb 7, 2015

@author: Hideki Ikeda
'''

import os
import sys
import filecmp
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import download_data as target


class TestDownload(unittest.TestCase):
    '''
    Unit tests for download_data
    '''
    test_symbol_path = os.path.join('data', 'test_symbols.txt')
    default_result_file='stock.csv'

    def test_read_symbols_all(self):
        expected = [ 'SYMBOL1', 'SYMBOL2', 'SYMBOL3', 'SYMBOL4',
                'SYMBOL5', 'SYMBOL6', 'SYMBOL7', 'SYMBOL8' ]
        result = target.read_symbols(self.test_symbol_path)
        self.assertEqual(expected, result)

    def test_read_symbols_2(self):
        expected = [ 'SYMBOL1', 'SYMBOL2' ]
        result = target.read_symbols(self.test_symbol_path, 2)
        self.assertEqual(expected, result)

    def test_read_symbols_0(self):
        expected = []
        result = target.read_symbols(self.test_symbol_path, 0)
        self.assertEqual(expected, result)

    def test_read_symbols_negative(self):
        expected = []
        result = target.read_symbols(self.test_symbol_path, -1)
        self.assertEqual(expected, result)

    def test_download_ibm(self):
        symbols = ['IBM']
        target.download_stocks(symbols)
        self.assertTrue(os.path.exists(self.default_result_file))

        # make sure all lines start with 'IBM,'
        bIBM_column = True
        with open(self.default_result_file, 'r') as f_result:
            last_line = None
            for line in f_result:
                last_line = line
                first_column = last_line.split(',', 1)[0].strip()
                bIBM_column = (first_column == symbols[0])
                
                if not bIBM_column:
                    break
            self.assertTrue(bIBM_column, msg=last_line)

            # make sure there are 8 columns
            columns = last_line.split(',')
            self.assertTrue(len(columns) == 8,
                    msg='columns must be 8 but {}'.format(len(columns)))

            # make sure the first date is correct
            expected = '1962-01-02'
            self.assertEqual(expected, columns[1].strip(),
                    msg='the first date must be {} but {}'.format(
                        expected, columns[1].strip() ) )

        os.remove(self.default_result_file)

    def test_download_two(self):
        symbols = [ 'IBM', 'YHOO' ]
        from_date = '2014-01-06'
        to_date = '2014-02-04'
        file_name = 'IY.csv'
        target.download_stocks(symbols, from_date, to_date, file_name)
        self.assertTrue(os.path.exists(file_name))

        bIBM = False
        bYHOO = False
        with open(file_name, 'r') as f_result:
            first_line = None
            last_line = None
            lcnt = 0
            for line in f_result:
                # the first line is a label line. The second line is
                # the first data
                if lcnt == 1:
                    first_line = line
                lcnt += 1
                last_line = line

                # make sure first column is either IBM or YHOO
                first_column = last_line.split(',', 1)[0].strip()
                self.assertTrue(first_column in symbols,
                        msg='First column is' + first_column)
                if first_column == 'IBM':
                    bIBM = True
                else:
                    bYHOO = True

            # make sure there were both IBM and YHOO
            self.assertTrue(bIBM and bYHOO,
                    msg='IBM={}, YHOO={}'.format(bIBM, bYHOO))

            #make sure from_date is correct
            columns = last_line.split(',')
            self.assertEqual(from_date, columns[1].strip(),
                    msg='the from_date must be {} but {}'.format(
                        from_date, columns[1].strip() ) )

            #make sure to_date is correct
            columns = first_line.split(',')
            self.assertEqual(to_date, columns[1].strip(),
                    msg='the to_date must be {} but {}'.format(
                        to_date, columns[1].strip() ) )

        os.remove(file_name)


if __name__ == '__main__':
    unittest.main()
